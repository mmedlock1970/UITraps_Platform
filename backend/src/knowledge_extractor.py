"""
Knowledge Base Extractor for Two-Pass Analysis

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework

Manages loading and extraction from two knowledge sources:
- UI_Traps_Analysis_Reference.md  →  Pass 1 (detection, condensed, AI-optimized)
- UI_Tenets_Traps.txt             →  Pass 2 (enrichment, full book content)

Book images are extracted from the source PDF and stored in data/book_images/
organized by trap name for use in Pass 2 enrichment.
"""
import os
import re
import json
import base64
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Paths relative to this file
_DATA_DIR = Path(__file__).parent.parent / "data"
ANALYSIS_REFERENCE_PATH = _DATA_DIR / "UI_Traps_Analysis_Reference.md"
FULL_BOOK_PATH = _DATA_DIR / "UI_Tenets_Traps.txt"
BOOK_IMAGES_DIR = _DATA_DIR / "book_images"

# Local-only cache files (not committed to git)
_BOOK_CACHE_PDF = _DATA_DIR / ".book_source_cache.pdf"
_BOOK_CACHE_META = _DATA_DIR / ".book_cache_meta.json"

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
    "UNNECESSARY STEP",
    "INFORMATION OVERLOAD",
    "SYSTEM AMNESIA",
    "BAD PREDICTION",
    "INCORRECT INFO",
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

# Module-level caches — loaded once per process
_analysis_reference_cache: str | None = None
_full_book_cache: str | None = None


def load_analysis_reference() -> str:
    """
    Load the condensed AI analysis reference (Pass 1 knowledge base).
    Cached after first load.
    """
    global _analysis_reference_cache
    if _analysis_reference_cache is None:
        if not ANALYSIS_REFERENCE_PATH.exists():
            raise FileNotFoundError(
                f"Analysis reference not found at {ANALYSIS_REFERENCE_PATH}. "
                f"Ensure UI_Traps_Analysis_Reference.md is in the data/ directory."
            )
        _analysis_reference_cache = ANALYSIS_REFERENCE_PATH.read_text(encoding="utf-8")
    return _analysis_reference_cache


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _trap_name_to_slug(name: str) -> str:
    return name.lower().replace(" ", "_")


def _download_google_drive(url: str, dest: Path) -> bool:
    """Download a file from a Google Drive share link using requests."""
    try:
        import requests
    except ImportError:
        print("[UITraps] requests library not available for Drive download")
        return False

    m = re.search(r'(?:file/d/|open\?id=|/d/)([a-zA-Z0-9_-]{20,})', url)
    if not m:
        print(f"[UITraps] Could not extract Drive file ID from URL")
        return False

    file_id = m.group(1)
    base_url = f"https://drive.google.com/uc?id={file_id}&export=download"

    try:
        session = requests.Session()
        response = session.get(base_url, stream=True, timeout=60)

        # Large files trigger a virus scan warning page
        if 'text/html' in response.headers.get('Content-Type', ''):
            # Try modern confirm=t approach first
            response = session.get(
                f"{base_url}&confirm=t",
                stream=True, timeout=120
            )
            # Fall back to cookie-based confirmation token
            if 'text/html' in response.headers.get('Content-Type', ''):
                token = next(
                    (v for k, v in session.cookies.items() if 'download_warning' in k),
                    None
                )
                if token:
                    response = session.get(
                        base_url, params={'confirm': token},
                        stream=True, timeout=120
                    )

        if response.status_code != 200:
            print(f"[UITraps] Drive download failed: HTTP {response.status_code}")
            return False

        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(32768):
                if chunk:
                    f.write(chunk)

        print(f"[UITraps] Downloaded {dest.stat().st_size / 1024:.0f} KB from Drive")
        return True

    except Exception as e:
        print(f"[UITraps] Drive download error: {e}")
        return False


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

def _sync_from_local_path(source_path: Path) -> bool:
    """
    Sync training file and images from a local PDF.
    Only re-extracts if the source file is newer than the training file.
    Returns True if the training file was updated.
    """
    global _full_book_cache

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
    pdf_text, trap_images = _extract_pdf_content(source_path)
    _write_training_file(pdf_text)
    _save_trap_images(trap_images)

    _full_book_cache = None
    return True


def _sync_from_url(url: str) -> bool:
    """
    Sync training file and images from a Google Drive URL.
    Re-downloads if the cached copy is older than BOOK_SYNC_INTERVAL_HOURS (default 24).
    Returns True if the training file was updated.
    """
    interval_hours = float(os.environ.get("BOOK_SYNC_INTERVAL_HOURS", "24"))

    meta: dict = {}
    if _BOOK_CACHE_META.exists():
        try:
            meta = json.loads(_BOOK_CACHE_META.read_text())
        except Exception:
            pass

    last_checked: float = meta.get("last_checked", 0)
    cached_url: str = meta.get("source_url", "")
    stale = (time.time() - last_checked) > (interval_hours * 3600)

    # Use the cached PDF if it exists and is fresh
    if not stale and cached_url == url and _BOOK_CACHE_PDF.exists():
        return _sync_from_local_path(_BOOK_CACHE_PDF)

    # (Re-)download from Drive
    print(f"[UITraps] Checking for updated book from Drive (last checked {int((time.time() - last_checked) / 3600)}h ago)…")
    if not _download_google_drive(url, _BOOK_CACHE_PDF):
        # Fall back to existing cached PDF if download fails
        if _BOOK_CACHE_PDF.exists():
            return _sync_from_local_path(_BOOK_CACHE_PDF)
        return False

    # Stamp the download time
    _BOOK_CACHE_META.write_text(json.dumps({"source_url": url, "last_checked": time.time()}))

    return _sync_from_local_path(_BOOK_CACHE_PDF)


def _sync_book_from_source() -> bool:
    """
    Auto-sync training file and images from the configured source.
    Checks BOOK_SOURCE_URL (Google Drive) first, then BOOK_SOURCE_PATH (local file).
    Returns True if the training file was updated.
    """
    source_url = os.environ.get("BOOK_SOURCE_URL", "").strip()
    if source_url:
        return _sync_from_url(source_url)

    source_local = os.environ.get("BOOK_SOURCE_PATH", "").strip()
    if source_local:
        return _sync_from_local_path(Path(source_local))

    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_full_book() -> str:
    """
    Load the full book manuscript (Pass 2 knowledge base).
    Auto-syncs from BOOK_SOURCE_URL or BOOK_SOURCE_PATH if newer.
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


def extract_trap_images(trap_names: List[str]) -> Dict[str, List[str]]:
    """
    Load saved book images for the specified traps.

    Args:
        trap_names: List of trap names to load images for

    Returns:
        Dict mapping trap_name -> list of base64-encoded PNG strings.
        Traps with no saved images are omitted.
    """
    result: Dict[str, List[str]] = {}

    if not BOOK_IMAGES_DIR.exists():
        return result

    for trap_name in trap_names:
        trap_dir = BOOK_IMAGES_DIR / _trap_name_to_slug(trap_name)
        if not trap_dir.exists():
            continue

        images = [
            base64.b64encode(img_file.read_bytes()).decode("utf-8")
            for img_file in sorted(trap_dir.glob("img_*.png"))
        ]
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
        print("ERROR: pypdf not installed. Run: pip install pypdf")
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
