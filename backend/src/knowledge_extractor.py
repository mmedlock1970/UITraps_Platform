"""
Knowledge Base Extractor for Two-Pass Analysis

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework

Manages loading and extraction from two knowledge sources:
- trap_kb_v2.md / trap_kb_v1.0.md  →  Pass 1 (detection, condensed, AI-optimized)
- UI_Tenets_Traps.txt             →  Pass 2 (enrichment, full book content)

Book images are extracted from the source PDF and stored in data/book_images/
organized by trap name for use in Pass 2 enrichment.
"""
import os
import re
import base64
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Paths relative to this file
_DATA_DIR = Path(__file__).parent.parent / "data"
ANALYSIS_REFERENCE_PATH = _DATA_DIR / "trap_kb_v2.md"
ANALYSIS_REFERENCE_PATH_V1 = _DATA_DIR / "trap_kb_v1.0.md"

# Detection-pass KB master per version. Single mode injects the whole file for the
# selected version. v1.1 / v2 are the self-instructing masters; v1 is the legacy
# KB-only master. Unknown versions fall back to trap_kb_v2.md.
_ANALYSIS_REFERENCE_PATHS = {
    "v1":   ANALYSIS_REFERENCE_PATH_V1,
    "v1.1": _DATA_DIR / "trap_kb_v1.1.md",
    "v2": _DATA_DIR / "trap_kb_v2.md",
}
FULL_BOOK_PATH = _DATA_DIR / "UI_Tenets_Traps.txt"
BOOK_IMAGES_DIR = _DATA_DIR / "book_images"
BOOK_IMAGES_DIR_V1 = BOOK_IMAGES_DIR / "v1"
BOOK_IMAGES_DIR_V2 = BOOK_IMAGES_DIR / "v2"

# Max characters to extract per trap section (avoids token bloat for verbose traps)
MAX_SECTION_CHARS = 6000
# Image extraction limits
MAX_IMAGES_PER_TRAP = 8
MIN_IMAGE_BYTES = 5000  # Skip tiny decorative images/icons

# All 27 valid trap names — used to find section boundaries in the book
TRAP_NAMES = [
    "INVISIBLE ELEMENT",
    "EFFECTIVELY INVISIBLE ELEMENT",
    "DISTRACTION",
    "UNCOMPREHENDED ELEMENT",
    "INVITING DEAD END",
    "POOR GROUPING",
    "FORCED SYNTAX",
    "MEMORY CHALLENGE",
    "FEEDBACK FAILURE",
    "PHYSICAL CHALLENGE",
    "ACCIDENTAL ACTIVATION",
    "SLOW OR NO RESPONSE",
    "CAPTIVE WAIT",
    "UNNECESSARY STEP(S)",
    "INFORMATION OVERLOAD",
    "SYSTEM AMNESIA",
    "BAD PREDICTION",
    "INCORRECT INFORMATION",
    "IRREVERSIBLE ACTION",
    "UNWANTED DISCLOSURE",
    "DATA LOSS",
    "GRATUITOUS REDUNDANCY",
    "VARIABLE OUTCOME",
    "WANDERING ELEMENT",
    "INCONSISTENT APPEARANCE",
    "AMBIGUOUS HOME",
    "POOR AESTHETIC",
]

# Module-level caches — one entry per version, loaded once per process
_full_book_cache: str | None = None
_analysis_reference_caches: dict[str, str | None] = {
    v: None for v in _ANALYSIS_REFERENCE_PATHS
}


def _strip_non_analysis_sections(text: str) -> str:
    """
    Remove any top-level (``## ``) section the KB self-marks as not-for-analysis —
    e.g. ``## VERBATIM DEFINITIONS (report display only — never loaded into analysis
    passes)`` and ``## AUTHORING STANDARDS (... never loaded into the analyzer)``.

    Single mode injects the whole master file into the analysis pass, so any section
    the KB says must never reach analysis has to be stripped here. The contract is the
    KB's own marker: a ``## `` heading containing the phrase "never loaded" (case-
    insensitive) drops that section up to the next ``## `` heading. Masters without any
    such marker are returned unchanged.
    """
    out, skipping = [], False
    for line in text.split("\n"):
        if line.startswith("## "):  # top-level heading (h2); trap chunks are h3 (### )
            # Contract: a heading the KB marks "never loaded" is not-for-analysis and is
            # dropped up to the next ## heading. This is generic — the KB decides what to
            # exclude by marking it, so new display/maintainer sections are handled without
            # a tool change. (OPEN ITEMS is not marked yet; recommend the KB add the marker.)
            skipping = "never loaded" in line.lower()
        if not skipping:
            out.append(line)
    return "\n".join(out)


def load_analysis_reference(version: str = "v2") -> str:
    """
    Load the condensed AI analysis reference (Pass 1 knowledge base) for the
    given KB version. Cached per version after first load.

    Sections the master marks "never loaded into analysis" (verbatim definitions,
    authoring standards) are stripped before caching so they cannot contaminate the
    analysis pass — single mode injects this whole string into the model.

    Args:
        version: one of "v1", "v1.1", "v2". Unknown versions fall back
            to "v2" (the current deployed KB).
    """
    if version not in _ANALYSIS_REFERENCE_PATHS:
        version = "v2"

    if _analysis_reference_caches.get(version) is None:
        path = _ANALYSIS_REFERENCE_PATHS[version]
        if not path.exists():
            raise FileNotFoundError(
                f"Analysis reference for KB version {version!r} not found at {path}. "
                f"Ensure {path.name} is in the data/ directory."
            )
        _analysis_reference_caches[version] = _strip_non_analysis_sections(
            path.read_text(encoding="utf-8")
        )
    return _analysis_reference_caches[version]


# ── KB-authoritative render strings — ONE source of truth (the KB), zero synced copies ──────────
# The tenet cash-out glosses and the v1 trap→Tenet map are evaluative, KB-owned content. They are
# parsed ONCE from the already-loaded, cached reference (no second file read) and memoized per
# process, so the tool holds NO hand-maintained copy and can never silently disagree with the KB.
# Parse failure is LOUD (raises) — a silent blank/guess would reintroduce exactly the drift this
# eliminates.
_CANON_TENETS = ("UNDERSTANDABLE", "COMFORTABLE", "RESPONSIVE", "EFFICIENT",
                 "ACCURATE", "PROTECTIVE", "HABITUATING", "BEAUTIFUL")
# Parser contract (KB Ledger 24): the eight glosses live in a uniquely-delimited fenced block, one
# per line as `- less <Tenet>: "<gloss>"`. We parse ONLY within the fences — this disambiguates the
# live glosses from the Ledger 23 prose that quotes them. Wording inside is free to reword; the
# fences + line shape are the contract.
_GLOSS_BLOCK_START = "<!-- TENET-GLOSSES:START -->"
_GLOSS_BLOCK_END = "<!-- TENET-GLOSSES:END -->"
_GLOSS_LINE_RX = re.compile(r'-\s*less\s+([A-Za-z]+)\s*:\s*"([^"]+)"')
_tenet_gloss_cache: "dict[str, dict]" = {}


def _fenced_block_lines(version: str, start_marker: str, end_marker: str, what: str, note: str) -> "list[str]":
    """Return the lines strictly BETWEEN two STANDALONE marker lines in the loaded KB reference. The
    real fence sits on its own line, while a backtick mention of the markers may appear in the prose
    above the block — anchoring on standalone lines targets the true fence, not the prose reference.
    Raises loudly if either marker is absent: a KB-owned fenced block the tool parses at runtime must
    never silently yield nothing. Shared by the TENET-GLOSSES and ASSESSABILITY-DIGEST parsers."""
    ref_lines = load_analysis_reference(version).splitlines()
    si = next((i for i, l in enumerate(ref_lines) if l.strip() == start_marker), -1)
    ei = next((i for i in range(si + 1, len(ref_lines)) if ref_lines[i].strip() == end_marker),
              -1) if si != -1 else -1
    if si == -1 or ei == -1:
        raise ValueError(
            f"KB parse FAILED for version {version!r}: {what} fenced block "
            f"({start_marker} … {end_marker}) not found as standalone marker lines in the KB. {note}"
        )
    return ref_lines[si + 1:ei]


def load_tenet_glosses(version: str = "v2") -> "dict[str, str]":
    """Emergent-Patterns tenet cash-out glosses, parsed VERBATIM from the KB's TENET-GLOSSES fenced
    block (Ledger 24: KB-owned, authoritative — the tool holds no copy). Parsed once from the loaded
    reference, memoized per version. Raises loudly if the block is missing or any of the eight
    canonical Tenets is absent — a parse miss must be visible, never a silent blank."""
    cached = _tenet_gloss_cache.get(version)
    if cached is not None:
        return cached
    block = "\n".join(_fenced_block_lines(   # parse ONLY within the fences
        version, _GLOSS_BLOCK_START, _GLOSS_BLOCK_END, "TENET-GLOSSES",
        "The eight glosses are read from this block (Ledger 24) — do not render without it."))
    glosses = {m.group(1).upper(): m.group(2).strip() for m in _GLOSS_LINE_RX.finditer(block)}
    missing = [t for t in _CANON_TENETS if t not in glosses]
    if missing:
        raise ValueError(
            f"KB gloss parse FAILED for version {version!r}: no gloss for {missing} in the "
            f"TENET-GLOSSES block. Expected `- less <Tenet>: \"<gloss>\"` lines (Ledger 24)."
        )
    _tenet_gloss_cache[version] = glosses
    return glosses


# ── Runtime provenance stamps (RELAY B): facts the tool can verify at runtime, never hardcoded ──
_kb_file_sha_cache: "dict[str, str]" = {}


def kb_file_sha256(version: str = "v2") -> str:
    """First 8 hex of sha256 of the KB FILE actually loaded for this version — computed from the
    file bytes (matches `sha256sum <file>`), memoized per process. Never hardcoded, never derived
    from the version label; changes when the KB file changes."""
    if version not in _ANALYSIS_REFERENCE_PATHS:
        version = "v2"
    cached = _kb_file_sha_cache.get(version)
    if cached is None:
        cached = _kb_file_sha_cache[version] = hashlib.sha256(
            _ANALYSIS_REFERENCE_PATHS[version].read_bytes()
        ).hexdigest()[:8]
    return cached


_build_sha_cache: "list" = []  # one-slot memo: [] = not computed, [value_or_None] = computed


def build_sha() -> "str | None":
    """git short-sha (8) of the running code — from a build/deploy-provided env var if present, else
    a live `git rev-parse` when a repo is reachable. Returns None if neither is available (the caller
    stamps 'unavailable' and the deploy must expose one of the env vars). Memoized per process."""
    if _build_sha_cache:
        return _build_sha_cache[0]
    val = None
    for _var in ("RAILWAY_GIT_COMMIT_SHA", "GIT_COMMIT", "GIT_SHA", "SOURCE_COMMIT",
                 "SOURCE_VERSION", "HEROKU_SLUG_COMMIT", "VERCEL_GIT_COMMIT_SHA"):
        _v = os.environ.get(_var)
        if _v and _v.strip():
            val = _v.strip()[:8]
            break
    if val is None:
        try:
            import subprocess
            _out = subprocess.run(
                ["git", "rev-parse", "--short=8", "HEAD"],
                cwd=str(Path(__file__).resolve().parents[2]),
                capture_output=True, text=True, timeout=2,
            )
            if _out.returncode == 0 and _out.stdout.strip():
                val = _out.stdout.strip()[:8]
        except Exception:
            val = None
    _build_sha_cache.append(val)
    return val


# ── Assessability digest (Ledger 26): per-Trap observability floor, KB-owned, read at runtime ──
# Ascending artifact-class scale — the floor is the MINIMUM class at which a Trap is observable AT ALL.
ARTIFACT_CLASS_RANK: "dict[str, int]" = {
    "static-screenshot": 0,
    "disconnected-screens": 1,
    "flow": 2,
    "live": 3,
    "code": 4,
}
_DIGEST_BLOCK_START = "<!-- ASSESSABILITY-DIGEST:START -->"
_DIGEST_BLOCK_END = "<!-- ASSESSABILITY-DIGEST:END -->"
# `- <TRAP>: <floor> [partial]` — trap may hold `(S)`/spaces; floor is a lowercase-hyphen token.
_DIGEST_LINE_RX = re.compile(r'-\s*(.+?)\s*:\s*([a-z][a-z-]*)\s*(partial)?\s*$')
_assessability_digest_cache: "dict[str, dict]" = {}


def load_assessability_digest(version: str = "v2") -> "dict[str, tuple]":
    """Per-Trap observability floors, parsed VERBATIM from the KB's ASSESSABILITY-DIGEST fenced block
    (Ledger 26: KB-owned, authoritative — the tool holds no copy). Returns
    {UPPER_TRAP: (floor_rank, floor_name, is_partial)}. Parsed once from the loaded reference, memoized
    per version. Raises loudly if the block is missing, empty, or names a floor outside the class scale
    — a parse miss must be visible, never a silent blank (the disposition gate reads this)."""
    cached = _assessability_digest_cache.get(version)
    if cached is not None:
        return cached
    digest: "dict[str, tuple]" = {}
    for raw in _fenced_block_lines(   # parse ONLY within the fences
            version, _DIGEST_BLOCK_START, _DIGEST_BLOCK_END, "ASSESSABILITY-DIGEST",
            "The disposition gate (Ledger 26) reads floors from this block — do not gate without it."):
        stripped = raw.strip()
        if not stripped:
            continue                                       # blank spacer lines are allowed
        m = _DIGEST_LINE_RX.match(stripped)
        if not m:
            # Between the fence markers every non-blank line must be a `- <TRAP>: <floor> [partial]`
            # row. A line that fails the shape (asterisk bullet, trailing comment, typo'd floor) would
            # otherwise be SILENTLY dropped — that Trap loses its floor and the gate quietly downgrades
            # its verdicts. Fail loud instead: the contract promises "a parse miss must be visible."
            raise ValueError(
                f"KB assessability parse FAILED for version {version!r}: line {raw!r} inside the "
                f"ASSESSABILITY-DIGEST block does not match the `- <TRAP>: <floor> [partial]` shape "
                f"(Ledger 26). Fix the line or move it outside the fence."
            )
        trap = re.sub(r"\s+", " ", m.group(1).strip()).upper()
        floor_name = m.group(2).strip()
        if floor_name not in ARTIFACT_CLASS_RANK:
            raise ValueError(
                f"KB assessability parse FAILED for version {version!r}: Trap {trap!r} names floor "
                f"{floor_name!r}, which is not on the artifact-class scale "
                f"{list(ARTIFACT_CLASS_RANK)}. Fix the digest line or the scale."
            )
        digest[trap] = (ARTIFACT_CLASS_RANK[floor_name], floor_name, bool(m.group(3)))
    if not digest:
        raise ValueError(
            f"KB assessability parse FAILED for version {version!r}: ASSESSABILITY-DIGEST block found "
            f"but no `- <TRAP>: <floor> [partial]` lines parsed from it (Ledger 26)."
        )
    _assessability_digest_cache[version] = digest
    return digest


# ── Scoped-coverage strings (Ledger 27): per-partial-Trap sub-scope line, KB-owned, read at runtime ──
_SCOPED_BLOCK_START = "<!-- SCOPED-COVERAGE:START -->"
_SCOPED_BLOCK_END = "<!-- SCOPED-COVERAGE:END -->"
# `- <TRAP>: "<string>"` — the string is double-quoted (no embedded double-quotes in the KB strings).
_SCOPED_LINE_RX = re.compile(r'-\s*(.+?)\s*:\s*"(.+)"\s*$')
_scoped_coverage_cache: "dict[str, dict]" = {}


def load_scoped_coverage(version: str = "v2") -> "dict[str, str]":
    """Per-Trap scoped-coverage strings for partial-floored Traps, parsed VERBATIM from the KB's
    SCOPED-COVERAGE fenced block (Ledger 27: KB-owned, authoritative — the tool holds no copy and
    NEVER synthesizes scope language). Returns {UPPER_TRAP: scoped-coverage string}. Parsed once from
    the loaded reference, memoized per version. The disposition gate renders this string when a partial
    Trap is cleared only within its floor-supported sub-scope (Option-3 scoped clearance). Fail-loud: a
    malformed line, an empty/unauthored string, or a `partial` Trap (per ASSESSABILITY-DIGEST) missing
    its string all raise — a parse miss must be visible, never a silent blank that drops the scoped line."""
    cached = _scoped_coverage_cache.get(version)
    if cached is not None:
        return cached
    scoped: "dict[str, str]" = {}
    for raw in _fenced_block_lines(   # parse ONLY within the fences
            version, _SCOPED_BLOCK_START, _SCOPED_BLOCK_END, "SCOPED-COVERAGE",
            "The disposition gate (Ledger 27) reads partial-Trap scoped strings from this block."):
        stripped = raw.strip()
        if not stripped:
            continue                                       # blank spacer lines are allowed
        m = _SCOPED_LINE_RX.match(stripped)
        if not m:
            # Every non-blank in-fence line must be `- <TRAP>: "<string>"`. A line failing the shape
            # (unquoted TODO-author sentinel, stray bullet) would otherwise be silently dropped — the
            # gate would then find no scoped string for that Trap. Fail loud, per the parse-miss contract.
            raise ValueError(
                f"KB scoped-coverage parse FAILED for version {version!r}: line {raw!r} inside the "
                f"SCOPED-COVERAGE block does not match the `- <TRAP>: \"<string>\"` shape (Ledger 27). "
                f"Fix the line or move it outside the fence."
            )
        trap = re.sub(r"\s+", " ", m.group(1).strip()).upper()
        text = m.group(2).strip()
        if not text or text == "TODO-author":
            raise ValueError(
                f"KB scoped-coverage parse FAILED for version {version!r}: Trap {trap!r} has an empty or "
                f"unauthored (TODO-author) scoped-coverage string (Ledger 27)."
            )
        scoped[trap] = text
    if not scoped:
        raise ValueError(
            f"KB scoped-coverage parse FAILED for version {version!r}: SCOPED-COVERAGE block found but "
            f"no `- <TRAP>: \"<string>\"` lines parsed from it (Ledger 27)."
        )
    # Integrity cross-check: every `partial`-floored Trap in the ASSESSABILITY-DIGEST MUST carry a
    # scoped string — the gate looks these up by partial Trap and cannot render a scoped clearance
    # without one. A partial Trap missing here is a KB drift between the two blocks; fail loud.
    _partials = {t for t, (_, _, is_partial) in load_assessability_digest(version).items() if is_partial}
    _missing = sorted(_partials - set(scoped))
    if _missing:
        raise ValueError(
            f"KB scoped-coverage parse FAILED for version {version!r}: partial-floored Traps {_missing} "
            f"have no scoped-coverage string — every `partial` Trap in the digest needs one (Ledger 27)."
        )
    _scoped_coverage_cache[version] = scoped
    return scoped


_V1_TAXONOMY_HEADER = "## TENETS AND THEIR TRAPS"
_v1_trap_tenet_cache: "dict[str, str] | None" = None


def load_v1_trap_tenet_map() -> "dict[str, str]":
    """The v1 trap→Tenet map, parsed from the FROZEN v1.0 card deck's `## TENETS AND THEIR TRAPS`
    section (`+ TENET` headers, `- Trap` members). ONE source of truth: the KB. Parsed once from the
    loaded v1 reference, memoized. Raises loudly if the section is absent or yields no groupings."""
    global _v1_trap_tenet_cache
    if _v1_trap_tenet_cache is not None:
        return _v1_trap_tenet_cache
    lines = load_analysis_reference("v1").splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == _V1_TAXONOMY_HEADER)
    except StopIteration:
        raise ValueError(
            f"v1 taxonomy parse FAILED: '{_V1_TAXONOMY_HEADER}' section not found in the v1.0 KB. "
            f"The v1 tenet map reads from this section — do not render v1 without it."
        )
    mapping, cur = {}, None
    for line in lines[start + 1:]:
        s = line.strip()
        if s.startswith("## "):          # next top-level section → end of taxonomy block
            break
        if s.startswith("+ "):
            cur = s[2:].strip().upper()
        elif s.startswith("- ") and cur:
            mapping[re.sub(r"\s+", " ", s[2:].strip()).upper()] = cur
    if not mapping:
        raise ValueError(
            f"v1 taxonomy parse FAILED: '{_V1_TAXONOMY_HEADER}' found but no `+ Tenet / - Trap` "
            f"groupings parsed from the v1.0 KB."
        )
    _v1_trap_tenet_cache = mapping
    return mapping


# ---------------------------------------------------------------------------
# PDF extraction helpers
# ---------------------------------------------------------------------------

def _trap_name_to_slug(name: str) -> str:
    return name.lower().replace(" ", "_")


# v1 folders use a numeric prefix for easy sorting — must match book_images/v1/ on disk
# 26 traps: same as v2 minus INCORRECT INFORMATION; UNNECESSARY STEP is singular
_V1_SLUG_MAP: dict[str, str] = {
    "INVISIBLE ELEMENT":              "01_invisible_element",
    "EFFECTIVELY INVISIBLE ELEMENT":  "02_effectively_invisible_element",
    "DISTRACTION":                    "03_distraction",
    "UNCOMPREHENDED ELEMENT":         "04_uncomprehended_element",
    "INVITING DEAD END":              "05_inviting_dead_end",
    "POOR GROUPING":                  "06_poor_grouping",
    "FORCED SYNTAX":                  "07_forced_syntax",
    "MEMORY CHALLENGE":               "08_memory_challenge",
    "FEEDBACK FAILURE":               "09_feedback_failure",
    "PHYSICAL CHALLENGE":             "10_physical_challenge",
    "ACCIDENTAL ACTIVATION":          "11_accidental_activation",
    "SLOW OR NO RESPONSE":            "12_slow_or_no_response",
    "CAPTIVE WAIT":                   "13_captive_wait",
    "UNNECESSARY STEP":               "14_unnecessary_step",
    "UNNECESSARY STEP(S)":            "14_unnecessary_step",
    "INFORMATION OVERLOAD":           "15_information_overload",
    "SYSTEM AMNESIA":                 "16_system_amnesia",
    "BAD PREDICTION":                 "17_bad_prediction",
    "IRREVERSIBLE ACTION":            "18_irreversible_action",
    "UNWANTED DISCLOSURE":            "19_unwanted_disclosure",
    "DATA LOSS":                      "20_data_loss",
    "GRATUITOUS REDUNDANCY":          "21_gratuitous_redundancy",
    "VARIABLE OUTCOME":               "22_variable_outcome",
    "WANDERING ELEMENT":              "23_wandering_element",
    "INCONSISTENT APPEARANCE":        "24_inconsistent_appearance",
    "AMBIGUOUS HOME":                 "25_ambiguous_home",
    "POOR AESTHETIC":                 "26_poor_aesthetic",
}

# v2 folders use a numeric prefix for easy sorting — must match book_images/v2/ on disk
_V2_SLUG_MAP: dict[str, str] = {
    "INVISIBLE ELEMENT":              "01_invisible_element",
    "EFFECTIVELY INVISIBLE ELEMENT":  "02_effectively_invisible_element",
    "DISTRACTION":                    "03_distraction",
    "UNCOMPREHENDED ELEMENT":         "04_uncomprehended_element",
    "INVITING DEAD END":              "05_inviting_dead_end",
    "POOR GROUPING":                  "06_poor_grouping",
    "FORCED SYNTAX":                  "07_forced_syntax",
    "MEMORY CHALLENGE":               "08_memory_challenge",
    "FEEDBACK FAILURE":               "09_feedback_failure",
    "PHYSICAL CHALLENGE":             "10_physical_challenge",
    "ACCIDENTAL ACTIVATION":          "11_accidental_activation",
    "SLOW OR NO RESPONSE":            "12_slow_or_no_response",
    "CAPTIVE WAIT":                   "13_captive_wait",
    "UNNECESSARY STEP(S)":            "14_unnecessary_steps",
    "INFORMATION OVERLOAD":           "15_information_overload",
    "SYSTEM AMNESIA":                 "16_system_amnesia",
    "INCORRECT INFORMATION":          "17_incorrect_information",
    "BAD PREDICTION":                 "18_bad_prediction",
    "IRREVERSIBLE ACTION":            "19_irreversible_action",
    "UNWANTED DISCLOSURE":            "20_unwanted_disclosure",
    "DATA LOSS":                      "21_data_loss",
    "GRATUITOUS REDUNDANCY":          "22_gratuitous_redundancy",
    "VARIABLE OUTCOME":               "23_variable_outcome",
    "WANDERING ELEMENT":              "24_wandering_element",
    "INCONSISTENT APPEARANCE":        "25_inconsistent_appearance",
    "AMBIGUOUS HOME":                 "26_ambiguous_home",
    "POOR AESTHETIC":                 "27_poor_aesthetic",
}


def _extract_pdf_content(pdf_path: Path) -> Tuple[str, Dict[str, List[bytes]]]:
    """
    Extract text and images from a PDF, organizing images by trap section.

    Returns:
        (full_text, trap_images) where trap_images maps trap_name -> list of raw image bytes
    """
    import pypdf

    reader = pypdf.PdfReader(str(pdf_path))
    skip = {"[page intentionally blank]", "[COVER PAGE]", "[FRONT MATTER]"}

    pages_text: List[str] = []
    current_trap: Optional[str] = None
    trap_images: Dict[str, List[bytes]] = {}
    seen_hashes: set = set()

    for page in reader.pages:
        page_text = (page.extract_text() or "").strip()

        if page_text in skip or len(page_text) <= 10:
            continue

        pages_text.append(page_text)

        # Detect if this page starts a new trap section (trap name as standalone line)
        for line in page_text.split('\n'):
            if line.strip() in TRAP_NAMES:
                current_trap = line.strip()
                break

        # Collect images from pages that belong to a trap section
        if current_trap:
            try:
                for img_obj in page.images:
                    img_data = img_obj.data
                    if len(img_data) < MIN_IMAGE_BYTES:
                        continue
                    img_hash = hashlib.md5(img_data).hexdigest()
                    if img_hash in seen_hashes:
                        continue
                    seen_hashes.add(img_hash)

                    if current_trap not in trap_images:
                        trap_images[current_trap] = []
                    if len(trap_images[current_trap]) < MAX_IMAGES_PER_TRAP:
                        trap_images[current_trap].append(img_data)
            except Exception:
                pass  # Image extraction is non-critical

    full_text = "\n\n".join(pages_text)
    bib_idx = full_text.find("\nBibliography\n")
    if bib_idx != -1:
        full_text = full_text[:bib_idx].rstrip()

    n_images = sum(len(v) for v in trap_images.values())
    print(f"[UITraps] Extracted {len(pages_text)} pages, {n_images} images across {len(trap_images)} traps")
    return full_text, trap_images


def _save_trap_images(trap_images: Dict[str, List[bytes]]) -> None:
    """Save extracted trap images to disk as PNGs, organized by trap name slug."""
    try:
        from PIL import Image
        import io as _io
        pillow_available = True
    except ImportError:
        pillow_available = False

    BOOK_IMAGES_DIR.mkdir(exist_ok=True)

    for trap_name, images in trap_images.items():
        trap_dir = BOOK_IMAGES_DIR / _trap_name_to_slug(trap_name)
        trap_dir.mkdir(exist_ok=True)

        # Remove stale images before writing new ones
        for old in trap_dir.glob("img_*"):
            old.unlink()

        for i, img_data in enumerate(images):
            out_path = trap_dir / f"img_{i + 1:03d}.png"
            try:
                if pillow_available:
                    img = Image.open(_io.BytesIO(img_data))
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGBA' if 'A' in img.getbands() else 'RGB')
                    img.save(str(out_path), "PNG", optimize=True)
                else:
                    out_path.write_bytes(img_data)
            except Exception as e:
                print(f"[UITraps] Warning: could not save image {i + 1} for {trap_name}: {e}")

    total = sum(
        1 for t in trap_images
        for _ in (BOOK_IMAGES_DIR / _trap_name_to_slug(t)).glob("img_*.png")
    )
    print(f"[UITraps] Saved {total} book images to {BOOK_IMAGES_DIR.relative_to(Path(__file__).parent.parent.parent)}")


def _write_training_file(pdf_text: str) -> None:
    """Write extracted PDF text to UI_Tenets_Traps.txt, preserving the header."""
    header = ""
    if FULL_BOOK_PATH.exists():
        existing = FULL_BOOK_PATH.read_text(encoding="utf-8")
        kb_idx = existing.find("## KNOWLEDGE BASE")
        if kb_idx != -1:
            header = existing[:kb_idx].rstrip() + "\n\n"

    new_content = header + "## KNOWLEDGE BASE\n\n" + pdf_text + "\n"
    FULL_BOOK_PATH.write_text(new_content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------

def _sync_book_from_source() -> bool:
    """
    If BOOK_SOURCE_PATH points to a PDF that is newer than UI_Tenets_Traps.txt,
    auto-extract text and images and regenerate the training file.
    Returns True if the training file was updated.
    """
    global _full_book_cache

    source = os.environ.get("BOOK_SOURCE_PATH", "").strip()
    if not source:
        return False

    source_path = Path(source)
    if "*" in source_path.name:
        # Glob pattern — pick the highest version number found
        import re as _re
        candidates = list(source_path.parent.glob(source_path.name))
        if not candidates:
            return False
        def _version_key(p: Path) -> int:
            m = _re.search(r'v(\d+)', p.stem, _re.IGNORECASE)
            return int(m.group(1)) if m else 0
        source_path = max(candidates, key=_version_key)
        print(f"[UITraps] Using book: {source_path.name}")

    if not source_path.exists():
        return False

    if FULL_BOOK_PATH.exists():
        if source_path.stat().st_mtime <= FULL_BOOK_PATH.stat().st_mtime:
            return False

    try:
        import pypdf  # noqa: F401
    except ImportError:
        return False

    print(f"[UITraps] Extracting from {source_path.name}…")
    pdf_text, _ = _extract_pdf_content(source_path)
    _write_training_file(pdf_text)
    # Images in book_images/v2/ are managed manually — never overwrite them on sync.

    _full_book_cache = None
    return True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_full_book() -> str:
    """
    Load the full book manuscript (Pass 2 knowledge base).
    Auto-syncs from BOOK_SOURCE_PATH if the local PDF is newer.
    Cached after first load.
    """
    global _full_book_cache
    _sync_book_from_source()
    if _full_book_cache is None:
        if not FULL_BOOK_PATH.exists():
            raise FileNotFoundError(
                f"Full book not found at {FULL_BOOK_PATH}. "
                f"Ensure UI_Tenets_Traps.txt is in the data/ directory."
            )
        _full_book_cache = FULL_BOOK_PATH.read_text(encoding="utf-8")
    return _full_book_cache


def extract_trap_sections(trap_names: List[str]) -> Dict[str, str]:
    """
    Extract the book sections for a list of trap names.

    For each trap name, finds its section in the full book and returns
    the text from that section header until the next trap section begins.

    Args:
        trap_names: List of trap names to extract (e.g. ["INVISIBLE ELEMENT", "POOR GROUPING"])

    Returns:
        Dict mapping trap_name -> extracted book section text.
        Traps not found in the book are omitted from the result.
    """
    book_text = load_full_book()
    sections = {}

    for trap_name in trap_names:
        section = _extract_single_section(trap_name, book_text)
        if section:
            sections[trap_name] = section

    return sections


_EXAMPLE_LABEL_RE = re.compile(r'^(\d+\.\d+)\.png$', re.IGNORECASE)


def extract_trap_images(trap_names: List[str], version: str = "v1") -> Dict[str, List[tuple]]:
    """
    Load saved example images for the specified traps.

    Args:
        trap_names: List of trap names to load images for
        version: "v1" or "v2" — selects the versioned image directory

    Returns:
        Dict mapping trap_name -> list of (label, base64) tuples.
        label is "Example X.Y" when the filename matches X.Y.png, else "".
        Traps with no saved images are omitted.
    """
    result: Dict[str, List[tuple]] = {}

    images_dir = BOOK_IMAGES_DIR_V2 if version == "v2" else BOOK_IMAGES_DIR_V1
    if not images_dir.exists():
        return result

    for trap_name in trap_names:
        if version == "v2":
            slug = _V2_SLUG_MAP.get(trap_name.upper(), _trap_name_to_slug(trap_name))
        else:
            slug = _V1_SLUG_MAP.get(trap_name.upper(), _trap_name_to_slug(trap_name))
        trap_dir = images_dir / slug
        if not trap_dir.exists():
            continue

        images = []
        for img_file in sorted(trap_dir.glob("*.png")):
            m = _EXAMPLE_LABEL_RE.match(img_file.name)
            label = f"Example {m.group(1)}" if m else ""
            b64 = base64.b64encode(img_file.read_bytes()).decode("utf-8")
            images.append((label, b64))

        if images:
            result[trap_name] = images

    return result


def extract_and_save_book(pdf_path: Path) -> bool:
    """
    Extract text and images from a PDF, update the training file, and save images.
    Called by update_training.py when pushing a new book version to the repo.

    Args:
        pdf_path: Path to the source PDF

    Returns:
        True on success, False if the PDF was not found or extraction failed.
    """
    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        return False

    try:
        import pypdf  # noqa: F401
    except ImportError:
        print("ERROR: pypdf not installed. Run: pip install pypdf[image]")
        return False

    pdf_text, trap_images = _extract_pdf_content(pdf_path)
    _write_training_file(pdf_text)
    _save_trap_images(trap_images)
    return True


def _extract_single_section(trap_name: str, book_text: str) -> str:
    """
    Extract a single trap's section from the book text.

    The book structure uses:
        TRAPS
        TRAP_NAME
        <content...>

    Trap names appear multiple times (table of contents, inline references,
    and the actual chapter). We identify the chapter occurrence by finding the
    trap name preceded by "TRAPS" within ~60 characters, then capture content
    until the next chapter-level trap name appears.
    """
    escaped = re.escape(trap_name)
    standalone = re.compile(rf'(?im)^[ \t]*{escaped}[ \t]*$')
    all_matches = list(standalone.finditer(book_text))

    if not all_matches:
        return ""

    # Find the chapter occurrence: preceded by "TRAPS" within ~60 chars
    chapter_match = None
    for m in all_matches:
        preceding = book_text[max(0, m.start() - 60):m.start()]
        if re.search(r'TRAPS\s*$', preceding, re.IGNORECASE):
            chapter_match = m
            break

    # Fall back to the last occurrence if the chapter pattern isn't found
    if chapter_match is None:
        chapter_match = all_matches[-1]

    section_start = chapter_match.start()
    search_from = chapter_match.end()
    earliest_end = len(book_text)

    # Find the end: next chapter-level trap name (preceded by TRAPS, or 500+ chars away)
    for other_trap in TRAP_NAMES:
        if other_trap == trap_name:
            continue
        other_escaped = re.escape(other_trap)
        other_standalone = re.compile(rf'(?im)^[ \t]*{other_escaped}[ \t]*$')
        for om in other_standalone.finditer(book_text, search_from):
            preceding = book_text[max(0, om.start() - 60):om.start()]
            if re.search(r'TRAPS\s*$', preceding, re.IGNORECASE) or \
               (om.start() - section_start) > 500:
                if om.start() < earliest_end:
                    earliest_end = om.start()
                break

    section_text = book_text[section_start:earliest_end].strip()

    # Truncate if the section is very long to keep tokens manageable
    if len(section_text) > MAX_SECTION_CHARS:
        section_text = section_text[:MAX_SECTION_CHARS] + "\n[...section truncated for brevity...]"

    return section_text


def get_trap_definitions(version: str = "v2") -> dict[str, str]:
    """
    Parse the KB file and return a dict mapping trap name (uppercase) to
    its verbatim one-sentence definition.

    Looks for:
      # CHUNK: TRAP NAME
      ...
      ## Definition (verbatim)
      <first non-empty line is the definition>
    """
    import re as _re
    if version == "v1":
        kb_path = ANALYSIS_REFERENCE_PATH_V1
    else:
        kb_path = ANALYSIS_REFERENCE_PATH

    if not kb_path.exists():
        return {}

    text = kb_path.read_text(encoding="utf-8")
    definitions: dict[str, str] = {}

    # Split into chunks on '# CHUNK:' lines
    chunks = _re.split(r'\n(?=# CHUNK:)', text)
    for chunk in chunks:
        lines = chunk.strip().split('\n')
        if not lines or not lines[0].startswith('# CHUNK:'):
            continue
        trap_name = lines[0][len('# CHUNK:'):].strip().upper()
        # Skip tenet-level chunks (they start with 'TENET —') or framework overview
        if trap_name.startswith('TENET') or trap_name == 'FRAMEWORK OVERVIEW':
            continue
        # Find '## Definition (verbatim)' and take the next non-empty line
        in_def = False
        for line in lines[1:]:
            if line.strip().startswith('## Definition'):
                in_def = True
                continue
            if in_def and line.strip():
                definitions[trap_name] = line.strip()
                break
            if in_def and line.startswith('## '):
                # Hit another section without finding definition text
                break

    return definitions


def collect_found_trap_names(report: dict) -> List[str]:
    """
    Extract all unique trap names from a Pass 1 report.

    Collects from critical_issues, moderate_issues, minor_issues, and potential_issues.

    Args:
        report: Pass 1 structured report dict

    Returns:
        Deduplicated list of trap names found in the report
    """
    found = set()
    for severity in ("critical_issues", "moderate_issues", "minor_issues", "potential_issues"):
        for issue in report.get(severity, []):
            trap_name = issue.get("trap_name")
            if trap_name:
                found.add(trap_name)
    return list(found)
