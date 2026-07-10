"""
Two-pass pack generator.

Splits a KB master (trap_kb_v2.md / trap_kb_v1.1.md / any future master) into the
derived two-pass artifacts the analyzer's twopass mode consumes:

    <master>_twopass/
        pass1_detection_pack.md   detection procedures + the G-rules/context pass 1 needs
        pass2_core_pack.md        full global rules + severity/confidence + context + taxonomy
        chunks/<slug>.md          one full ### TRAP: chunk per trap
        manifest.json             trap→chunk map, master hash, verbatim_definitions

Design contract (see ALIGNMENT CONTRACT §5): the split is keyed on STRUCTURAL HEADINGS,
not hard-coded trap counts or label lists, so it works across masters with different
layouts. Evaluation content is never altered — only sliced and copied. Sections the KB
marks "never loaded" are excluded (verbatim definitions, authoring standards, open items).

The generator is deterministic: same master in → same packs out. `manifest.json` records
a sha256 of the master so twopass mode can refuse to run against stale packs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from pathlib import Path

# Per-version regeneration locks — so concurrent requests (now possible since the API
# handlers run analysis off the event loop) regenerate a version's packs once, not N times.
_REGEN_LOCKS: "dict[str, threading.Lock]" = {}
_REGEN_LOCKS_GUARD = threading.Lock()


def _version_lock(version: str) -> threading.Lock:
    with _REGEN_LOCKS_GUARD:
        lk = _REGEN_LOCKS.get(version)
        if lk is None:
            lk = _REGEN_LOCKS[version] = threading.Lock()
        return lk


def _atomic_write_text(path: Path, text: str) -> None:
    """Write via a temp file + os.replace so a reader never sees a half-written file."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)  # atomic on the same filesystem

_DATA_DIR = Path(__file__).parent.parent / "data"

# Master file per version (mirrors knowledge_extractor._ANALYSIS_REFERENCE_PATHS).
_MASTERS = {
    "v1.1": _DATA_DIR / "trap_kb_v1.1.md",
    "v2": _DATA_DIR / "trap_kb_v2.md",
}

# G-rules that belong in the pass-1 detection pack (per §5b). G6 carries a pass-2
# clearance clause but is shipped whole — it's cheap and inert in pass one.
_PASS1_G_RULES = ("G1", "G2", "G6", "G7")

# Fixed harness role headers (tool-owned mechanics, not KB content).
_PASS1_ROLE_HEADER = (
    "**Role of this pass:** permissive detection. Run every procedure below against the "
    "artifact. Flag every candidate with named evidence. Do NOT filter, do NOT weigh "
    "disconfirmation, do NOT assign severity — over-reporting at this stage is correct "
    "behavior. Adjudication happens in pass two with different materials.\n\n"
    "**Harness guidance (not KB content):** for speed, instruct the model to emit candidates "
    "in a terse line format — `TRAP | screen | element(s) | triggering condition(s)` — one "
    "line per candidate, no prose. Decode time scales with output length; adjudication needs "
    "the evidence, not an essay."
)
_PASS2_ROLE_HEADER = (
    "**Role of this pass:** adjudication. Load this pack PLUS the full chunk file for each Trap "
    "flagged in pass one (see manifest.json). The Taxonomy Index below permits re-routing a "
    "finding to a non-candidate Trap; when a Boundary clause routes there, load that Trap's "
    "chunk too. Apply, in order: Boundary & Disconfirmation → G3 one-problem-one-issue → "
    "G4/G5 assessability → Severity & Confidence → G8 report assembly."
)


def _slug(name: str) -> str:
    """Lowercase; collapse non-alphanumeric runs to single underscores; trim edges."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _gen_comment(master_name: str) -> str:
    return f"<!-- GENERATED from {master_name} — do not edit; regenerate on any master edit -->"


def _sections(text: str) -> list[tuple[str, str]]:
    """
    Split the master into top-level (``## ``) sections. Returns a list of
    (heading_line, section_text) where section_text includes the heading and runs to
    just before the next ``## `` heading. Content before the first ``## `` (the H1 title)
    is dropped — it never belongs in a pack.
    """
    out: list[tuple[str, str]] = []
    cur_heading: str | None = None
    cur: list[str] = []
    for line in text.split("\n"):
        if line.startswith("## "):
            if cur_heading is not None:
                out.append((cur_heading, "\n".join(cur).rstrip()))
            cur_heading = line
            cur = [line]
        elif cur_heading is not None:
            cur.append(line)
    if cur_heading is not None:
        out.append((cur_heading, "\n".join(cur).rstrip()))
    return out


def _find_section(sections: list[tuple[str, str]], prefix: str) -> str:
    """Return the full text of the first section whose heading (after '## ') starts with prefix."""
    for heading, body in sections:
        if heading[3:].strip().upper().startswith(prefix.upper()):
            return body
    raise ValueError(f"master is missing a '## {prefix}...' section")


def _g_rule_blocks(global_rules_body: str) -> dict[str, str]:
    """Map 'G1'..'G8' → the bold-labelled block text (from '**Gn.' to just before the next '**G')."""
    lines = global_rules_body.split("\n")
    blocks: dict[str, str] = {}
    cur_key: str | None = None
    cur: list[str] = []
    g_re = re.compile(r"^\*\*(G\d)\.")
    for line in lines:
        m = g_re.match(line)
        if m:
            if cur_key:
                blocks[cur_key] = "\n".join(cur).rstrip()
            cur_key = m.group(1)
            cur = [line]
        elif cur_key:
            cur.append(line)
    if cur_key:
        blocks[cur_key] = "\n".join(cur).rstrip()
    return blocks


# Taxonomy / verbatim line: '- **Name** — definition', optionally with a provenance
# parenthetical between the name and the em-dash — '- **Name** (card N) — definition' —
# which the v1 lineage uses to tie each definition to its physical card. The parenthetical
# is deliberate lineage, not noise: tolerate it (don't capture it into the name).
_TAX_LINE = re.compile(r"^-\s+\*\*(.+?)\*\*\s*(?:\([^)]*\)\s*)?—\s+(.+)$")


def _taxonomy(taxonomy_body: str) -> "dict[str, tuple[str, str]]":
    """
    Parse the Taxonomy Index into {UPPER_NAME: (Title Name, one-liner)} in document order
    (dict preserves insertion order). Only '- **Name** — text' lines are entries; tenet
    headers and the sibling-note paragraph are ignored.
    """
    tax: dict[str, tuple[str, str]] = {}
    for line in taxonomy_body.split("\n"):
        m = _TAX_LINE.match(line.strip())
        if m:
            title, oneliner = m.group(1).strip(), m.group(2).strip()
            tax[title.upper()] = (title, oneliner)
    return tax


# Heading = '### TRAP: <NAME>' plus an optional trailing '*(...)*' annotation. The annotation
# varies by master ('*(draft-grade)*' in v2, '*(card 1 — mechanically templated...)*' in
# v1.1), so capture the name without it and pull the grade out separately.
_CHUNK_HEADING = re.compile(r"^### TRAP:\s+(.+?)\s*(\*\(.*\)\*)?\s*$")
_GRADE_RE = re.compile(r"(\w+)-grade")


def _chunks(text: str) -> list[dict]:
    """
    Extract every ### TRAP: chunk. Returns ordered list of
    {name_upper, grade, full_text}. A chunk runs from its '### TRAP:' heading to just
    before the next '### TRAP:' or the next '## ' section heading.
    """
    lines = text.split("\n")
    chunks: list[dict] = []
    cur: dict | None = None
    buf: list[str] = []

    def _flush():
        if cur is not None:
            body = "\n".join(buf).split("\n")
            # Drop the inter-chunk '---' horizontal rule (and trailing blanks) that sits
            # between this chunk and the next — it's a separator, not chunk content.
            while body and body[-1].strip() in ("", "---"):
                body.pop()
            cur["full_text"] = "\n".join(body)
            chunks.append(cur)

    for line in lines:
        h = _CHUNK_HEADING.match(line)
        if h:
            _flush()
            annotation = h.group(2) or ""
            gm = _GRADE_RE.search(annotation)
            cur = {"name_upper": h.group(1).strip().upper(), "grade": gm.group(1) if gm else ""}
            buf = [line]
        elif line.startswith("## "):
            # Left the TRAP CHUNKS territory — close any open chunk and stop collecting.
            _flush()
            cur = None
            buf = []
        elif cur is not None:
            buf.append(line)
    _flush()
    return chunks


def _detection_slice(chunk_full: str) -> str:
    """
    The pass-1 slice: from the line beginning '**Detection procedure' up to (excluding) the
    line beginning '**Disconfirmation'. Prefix-matched, tolerant of parenthetical suffixes.
    """
    lines = chunk_full.split("\n")
    start = end = None
    for i, line in enumerate(lines):
        if start is None and line.startswith("**Detection procedure"):
            start = i
        elif start is not None and line.startswith("**Disconfirmation"):
            end = i
            break
    if start is None:
        return ""
    return "\n".join(lines[start:end]).rstrip()


def _assessability_block(chunk_full: str) -> str:
    """
    Extract a chunk's assessability declaration — the bold-labelled block whose label
    contains 'assessab' (case-insensitive). This catches both the standard
    '**Assessability & Confidence.**' block and Poor Aesthetic's
    '**Boundary & assessability warning (read first).**', without hard-coding either label.
    The block runs from that label to just before the NEXT line-start bold label (the next
    '**...**' section — colon- or period-terminated, any case), or to end of chunk. Returned
    verbatim, incl. its label. Matching only a line-start bold run (`[^*]*` can't cross a '*')
    means an 'assessab' mention inside a paragraph's prose never triggers capture.
    """
    lines = chunk_full.split("\n")
    out: list[str] = []
    cap = False
    for ln in lines:
        if not cap and re.match(r"^\*\*[^*]*assessab", ln, re.I):
            cap = True
            out = [ln]
            continue
        # End at the next section label. Match ANY line-start bold run — not just
        # uppercase+period — so a colon-terminated label (e.g. '**Escalators:**') or a
        # lowercase-led one still bounds the block instead of being swallowed into it.
        if cap and re.match(r"^\*\*[^*]+\*\*", ln):
            break
        if cap:
            out.append(ln)
    return "\n".join(out).strip()


def _digest_line(name: str, block: str) -> str:
    """One digest bullet for a trap: strip the block's own '**...**' label (the digest
    header already frames these as assessability notes) and collapse to a single line so the
    section is one-line-per-trap. Text is otherwise verbatim — no summarizing, no authoring."""
    body = re.sub(r"^\*\*[^*]+\.\*\*\s*", "", block)  # drop leading bold label
    body = " ".join(body.split())                      # collapse all whitespace to one line
    return f"- **{name}** — {body}"


def _verbatim_defs(sections: list[tuple[str, str]]) -> dict[str, str]:
    """{Title Name: definition} parsed from the '## VERBATIM DEFINITIONS' section, if present."""
    for heading, body in sections:
        if heading[3:].strip().upper().startswith("VERBATIM DEFINITIONS"):
            defs: dict[str, str] = {}
            for line in body.split("\n"):
                m = _TAX_LINE.match(line.strip())
                if m:
                    defs[m.group(1).strip()] = m.group(2).strip()
            return defs
    return {}


def generate(version: str) -> dict[str, str | dict]:
    """
    Build the derived artifacts for a KB version in memory. Returns
    {relative_path: content} where content is a str for .md files and a dict for the
    manifest. Does not touch disk.
    """
    if version not in _MASTERS:
        raise ValueError(f"no master registered for version {version!r}")
    master_path = _MASTERS[version]
    text = master_path.read_text(encoding="utf-8")
    master_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    gen = _gen_comment(master_path.name)

    sections = _sections(text)
    global_rules = _find_section(sections, "GLOBAL RULES")
    severity = _find_section(sections, "SEVERITY & CONFIDENCE")
    context_schema = _find_section(sections, "CONTEXT INTAKE SCHEMA")
    taxonomy_body = _find_section(sections, "TAXONOMY INDEX")

    g_blocks = _g_rule_blocks(global_rules)
    tax = _taxonomy(taxonomy_body)
    chunks = _chunks(text)
    verbatims = _verbatim_defs(sections)

    # ── Guardrails: refuse to ship a silently-degraded pack ─────────────────────
    # The split depends on exact heading/marker tokens; if a master's formatting drifts
    # these parsers quietly return empty/partial results. Turn that whole failure class
    # into one loud error at generation time instead of a half-empty pack reaching Claude.
    problems: list[str] = []
    if not chunks:
        problems.append("no '### TRAP:' chunks found — chunk heading format may have changed")
    missing_g = [g for g in _PASS1_G_RULES if g not in g_blocks]
    if missing_g:
        problems.append(f"missing global-rule block(s) {missing_g} — expected '**Gn.' markers")
    if not tax:
        # Non-fatal: the pass-1 pack falls back to title-cased trap names (no one-liners).
        # Surface it rather than shipping degradation silently, but don't block generation.
        print(f"[UITraps][pack_generator] WARNING: {version!r} taxonomy parsed empty — "
              "falling back to title-cased trap names (no one-liners in the detection pack)")
    if not verbatims:
        problems.append("empty verbatim_definitions — VERBATIM DEFINITIONS section missing or reformatted")
    for _name, _body in (("SEVERITY & CONFIDENCE", severity), ("CONTEXT INTAKE SCHEMA", context_schema),
                         ("TAXONOMY INDEX", taxonomy_body), ("GLOBAL RULES", global_rules)):
        if not (_body or "").strip():
            problems.append(f"section '{_name}' is empty")
    seen_slugs: dict[str, str] = {}
    for ch in chunks:
        if not _detection_slice(ch["full_text"]).strip():
            problems.append(f"trap '{ch['name_upper']}' has no detection slice — missing '**Detection procedure'")
        # Line-start match, matching _detection_slice's boundary test — a mid-line mention
        # would pass a substring check yet leave the slice's end unbounded (over-capture).
        if not any(_ln.startswith("**Disconfirmation") for _ln in ch["full_text"].split("\n")):
            problems.append(f"trap '{ch['name_upper']}' missing '**Disconfirmation' boundary — detection slice would over-capture")
        # Every trap must carry an assessability declaration — it's the source for the pass-2
        # per-trap assessability digest (so coverage for non-candidate traps is written informed).
        if not _assessability_block(ch["full_text"]).strip():
            problems.append(f"trap '{ch['name_upper']}' has no assessability block — expected a '**...assessab...**' section")
        title, _ = tax.get(ch["name_upper"], (ch["name_upper"].title(), ""))
        s = _slug(title)
        if s in seen_slugs:
            problems.append(f"slug collision '{s}' — '{seen_slugs[s]}' vs '{title}' would overwrite one chunk")
        seen_slugs[s] = title
    if problems:
        raise ValueError(
            f"pack generation for {version!r} produced a degraded result — refusing to ship:\n  - "
            + "\n  - ".join(problems)
        )

    # ── pass 1 ────────────────────────────────────────────────────────────────
    p1: list[str] = [gen, f"# PASS ONE — DETECTION PACK (KB {version}, two-pass structure)", "", _PASS1_ROLE_HEADER, ""]
    for g in _PASS1_G_RULES:
        if g in g_blocks:
            p1.append(g_blocks[g])
            p1.append("")
    p1 += ["---", "", context_schema, "", "---", "", f"## DETECTION PROCEDURES (all {len(chunks)} Traps)", ""]
    for ch in chunks:
        title, oneliner = tax.get(ch["name_upper"], (ch["name_upper"].title(), ""))
        p1.append(f"### {title}")
        if oneliner:
            p1.append(f"*{oneliner}*")
        p1.append("")
        slice_ = _detection_slice(ch["full_text"])
        if slice_:
            p1.append(slice_)
            p1.append("")
        p1.append("---")
        p1.append("")
    pass1 = "\n".join(p1).rstrip() + "\n"

    # ── per-trap assessability digest ─────────────────────────────────────────
    # Adjudication loads full chunks only for traps flagged in pass one; a trap with no
    # candidates never has its chunk seen, so its coverage line gets written blind (e.g.
    # Irreversible Action cleared as "Did not find" on a static screenshot when its own chunk
    # declares statics insufficient). This digest lifts each chunk's assessability declaration
    # verbatim — one line per trap — so coverage for non-candidate traps is written informed.
    # Pure assembly: the tool copies the KB's own words, authoring none.
    _digest = [
        "## PER-TRAP ASSESSABILITY DIGEST",
        "",
        "*(Harness reference, not new KB content.) Before writing a coverage line for any Trap "
        "whose chunk was NOT loaded this pass — i.e. one with no pass-one candidates — read its "
        "line below. Each is that Trap's own assessability declaration, verbatim, so a Trap is "
        "never cleared as \"Did not find\" when its chunk holds that the artifact cannot settle it. "
        "\"Not assessable from this artifact\" is a coverage note, not an absence.*",
        "",
    ]
    for ch in chunks:
        title, _ = tax.get(ch["name_upper"], (ch["name_upper"].title(), ""))
        _digest.append(_digest_line(title, _assessability_block(ch["full_text"])))
    assessability_digest = "\n".join(_digest)

    # ── pass 2 core ───────────────────────────────────────────────────────────
    p2 = [
        gen,
        f"# PASS TWO — ADJUDICATION CORE PACK (KB {version}, two-pass structure)",
        "",
        _PASS2_ROLE_HEADER,
        "",
        global_rules,
        "",
        severity,
        "",
        context_schema,   # §5b — included even though the stale shipped pack omitted it
        "",
        taxonomy_body,
        "",
        "---",
        "",
        assessability_digest,
    ]
    pass2 = "\n".join(p2).rstrip() + "\n"

    # ── chunks + manifest ─────────────────────────────────────────────────────
    out: dict[str, str | dict] = {
        "pass1_detection_pack.md": pass1,
        "pass2_core_pack.md": pass2,
    }
    manifest_traps = []
    for ch in chunks:
        title, _ = tax.get(ch["name_upper"], (ch["name_upper"].title(), ""))
        slug = _slug(title)
        out[f"chunks/{slug}.md"] = f"{gen}\n{ch['full_text']}\n"
        manifest_traps.append({"trap": title, "grade": ch["grade"], "chunk_file": f"chunks/{slug}.md"})

    out["manifest.json"] = {
        "kb_version": version,
        "structure": "two-pass",
        "source": master_path.name,
        "master_sha256": master_hash,
        "note": "regenerate all derived files on any master edit",
        "pass1": "pass1_detection_pack.md",
        "pass2_core": "pass2_core_pack.md",
        "traps": manifest_traps,
        "verbatim_definitions": verbatims,
    }
    return out


def _twopass_dir(version: str) -> Path:
    return _MASTERS[version].with_name(_MASTERS[version].stem + "_twopass")


def write(version: str) -> Path:
    """Generate and write the artifacts to <master>_twopass/. Returns that directory.

    generate() runs first and may raise (guardrails) — on failure nothing is written, so a
    bad master can never overwrite good packs. Files are written atomically, and the
    manifest is written LAST, so a concurrent reader never sees a fresh manifest pointing at
    packs that aren't on disk yet."""
    out = generate(version)
    dest = _twopass_dir(version)
    (dest / "chunks").mkdir(parents=True, exist_ok=True)
    manifest = out.pop("manifest.json", None)
    for rel, content in out.items():
        _atomic_write_text(dest / rel, content)
    if manifest is not None:
        _atomic_write_text(dest / "manifest.json", json.dumps(manifest, indent=1, ensure_ascii=False))
    return dest


_MASTER_HASH_CACHE: "dict[str, tuple]" = {}  # version -> (mtime_ns, sha256)


def master_hash(version: str) -> str:
    """sha256 of the current master — for the twopass staleness guard. Memoized by mtime so
    the several calls per analysis (ensure_current, def-injection, run-log kb_hash) don't each
    re-read+re-hash the large master file. A master edit changes mtime → cache miss → re-hash,
    so the staleness guard still detects new drops."""
    path = _MASTERS[version]
    try:
        mtime = path.stat().st_mtime_ns
    except OSError:
        mtime = None
    cached = _MASTER_HASH_CACHE.get(version)
    if cached is not None and mtime is not None and cached[0] == mtime:
        return cached[1]
    sha = hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    _MASTER_HASH_CACHE[version] = (mtime, sha)
    return sha


# ── Runtime: staleness guard + loaders + candidate matching ──────────────────

def load_manifest(version: str) -> dict:
    """Read the derived manifest.json (raises if the twopass dir hasn't been generated)."""
    path = _twopass_dir(version) / "manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"twopass packs for {version!r} not generated yet ({path})")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_manifest_or_none(version: str) -> "dict | None":
    """load_manifest, but a missing OR corrupt/truncated manifest yields None (→ regenerate)
    rather than an exception that would otherwise wedge every subsequent run."""
    try:
        return load_manifest(version)
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
        return None


# Per-process caches keyed by (version, master sha256). The master sha is mtime-cached (cheap), so
# a KB edit changes the sha → cache miss → fresh read of the regenerated packs — the "no restart for
# a KB swap" contract holds. This spares the DEFAULT two-pass path ~100 KB of file reads + a JSON
# parse per request (manifest + both packs are deterministic given the master).
_MANIFEST_CACHE: "dict[tuple, dict]" = {}
_PACK_TEXT_CACHE: "dict[tuple, str]" = {}
_CHUNK_TEXT_CACHE: "dict[tuple, str]" = {}   # (version, master_sha, chunk_file) -> chunk text


def ensure_current(version: str, regenerate: bool = True) -> dict:
    """
    Staleness guard. Compare the packs' recorded master hash against the current master.
    On mismatch (or a missing/legacy/corrupt manifest), regenerate the packs so twopass
    always runs against packs matching the live master — the KB Claude's "sha256 guard
    makes the swap automatic." Returns the current manifest.

    With regenerate=False, a mismatch raises instead of regenerating — the "refuse to run
    on hash-mismatched packs" safety net.
    """
    current = master_hash(version)
    cached = _MANIFEST_CACHE.get((version, current))
    if cached is not None:  # already validated fresh for this master this process
        return cached
    manifest = _load_manifest_or_none(version)
    if manifest is not None and manifest.get("master_sha256") == current:
        _MANIFEST_CACHE[(version, current)] = manifest
        return manifest
    if not regenerate:
        raise RuntimeError(
            f"twopass packs for {version!r} are stale or unreadable (master changed) and "
            f"regeneration is disabled — refusing to run against hash-mismatched packs."
        )
    # Serialize regeneration per version so concurrent requests regenerate once, not N times.
    with _version_lock(version):
        # Re-check under the lock: another thread may have just regenerated.
        manifest = _load_manifest_or_none(version)
        if manifest is not None and manifest.get("master_sha256") == current:
            _MANIFEST_CACHE[(version, current)] = manifest
            return manifest
        write(version)
        manifest = load_manifest(version)
        _MANIFEST_CACHE[(version, current)] = manifest
        return manifest


_PACK_FILES = {"pass1": "pass1_detection_pack.md", "pass2": "pass2_core_pack.md"}


def load_pack(version: str, which: str) -> str:
    """Read the 'pass1' (detection) or 'pass2' (adjudication core) pack text. Memoized by
    (version, which, master sha) so the default two-pass path does not re-read the packs every
    request; a master edit changes the sha → cache miss → fresh read of the regenerated pack."""
    try:
        fname = _PACK_FILES[which]
    except KeyError:
        raise ValueError(f"unknown pack {which!r}; expected one of {sorted(_PACK_FILES)}")
    key = (version, which, master_hash(version))
    cached = _PACK_TEXT_CACHE.get(key)
    if cached is None:
        cached = _PACK_TEXT_CACHE[key] = (_twopass_dir(version) / fname).read_text(encoding="utf-8")
    return cached


def load_chunks(version: str, trap_names: list[str], manifest: dict | None = None) -> str:
    """
    Concatenate the full chunk files for the given (canonical) trap names, in manifest
    order. Names are matched case-insensitively. Unknown names are skipped by the caller
    (they should already be canonical from match_candidates)."""
    manifest = manifest or load_manifest(version)
    wanted = {n.upper() for n in trap_names}
    parts = []
    dest = _twopass_dir(version)
    # Memoize each chunk's text by (version, master sha, chunk_file) — same staleness key as the packs,
    # so a KB edit changes the sha → cache miss → fresh read. Without this the matched chunk files are
    # re-read from disk on every two-pass request even though they are deterministic given the master.
    _sha = master_hash(version)
    for t in manifest.get("traps", []):               # manifest order, not caller order
        name, chunk_file = t.get("trap"), t.get("chunk_file")
        if name and chunk_file and name.upper() in wanted:
            _ck = (version, _sha, chunk_file)
            _txt = _CHUNK_TEXT_CACHE.get(_ck)
            if _txt is None:
                _txt = _CHUNK_TEXT_CACHE[_ck] = (dest / chunk_file).read_text(encoding="utf-8")
            parts.append(_txt)
    return "\n\n".join(parts)


def _norm_letters(s: str) -> str:
    """Normalize a name to letters only, lowercased — for tolerant matching."""
    return re.sub(r"[^a-z]", "", s.lower())


def match_candidates(raw_text: str, manifest: dict) -> tuple[list[str], list[str]]:
    """
    Parse pass-1 candidate output tolerantly and match against the manifest's trap names.

    Accepts lines like 'TRAP | screen | element | condition', markdown tables, bullets,
    numbering, or bold — the trap name is taken as the text before the first '|' (or the
    whole line) and compared on letters only. Longest manifest name wins first so
    'Effectively Invisible Element' isn't captured by 'Invisible Element'.

    Returns (matched_canonical_names in manifest order, unmatched_lines) — unmatched lines
    are surfaced by the caller, never silently dropped.
    """
    names = [t["trap"] for t in manifest["traps"]]
    norm_to_name = {_norm_letters(n): n for n in names}
    # Longest normalized names first for the containment fallback.
    norms_by_len = sorted(norm_to_name.keys(), key=len, reverse=True)

    matched: list[str] = []
    seen: set[str] = set()
    unmatched: list[str] = []
    for line in raw_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Take the first non-empty pipe-cell as the trap name. Handles bare lines,
        # 'TRAP | screen | ...' rows, and markdown '| TRAP | screen |' table rows alike.
        cells = [c.strip() for c in line.split("|") if c.strip()]
        head = cells[0] if cells else ""
        norm = _norm_letters(head)
        if not norm:
            continue
        canon = norm_to_name.get(norm)
        if canon is None:
            for n in norms_by_len:               # containment fallback, longest first
                if n and n in norm:
                    canon = norm_to_name[n]
                    break
        if canon is not None:
            if canon not in seen:
                seen.add(canon)
                matched.append(canon)
        else:
            unmatched.append(line)

    # Return matched in manifest order for stable chunk loading.
    ordered = [n for n in names if n in seen]
    return ordered, unmatched
