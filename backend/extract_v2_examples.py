"""
extract_v2_examples.py
One-time script to extract trap example images from the v2 Examples PDF
and save them to backend/data/book_images/v2/<trap_slug>/

Handles single-page PDFs by using text+image positions to assign each
image to the trap header immediately above it.

Usage:
    python extract_v2_examples.py <path_to_pdf>

Requirements:
    pip install pdfplumber Pillow
"""
import io
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Name normalization — maps PDF header text -> canonical KB slug
# ---------------------------------------------------------------------------
_SLUG_MAP = {
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
    "UNNECESSARY STEPS":              "14_unnecessary_steps",
    "UNNECESSARY STEP":               "14_unnecessary_steps",
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

MAX_IMAGES_PER_TRAP = 6
MIN_IMAGE_BYTES = 500   # skip tiny decorative icons

# Canonical v2 trap names — sorted longest-first so "EFFECTIVELY INVISIBLE ELEMENT"
# matches before "INVISIBLE ELEMENT"
_CANONICAL_TRAPS = sorted([
    "INVISIBLE ELEMENT", "EFFECTIVELY INVISIBLE ELEMENT", "DISTRACTION",
    "UNCOMPREHENDED ELEMENT", "INVITING DEAD END", "POOR GROUPING", "FORCED SYNTAX",
    "MEMORY CHALLENGE", "FEEDBACK FAILURE", "PHYSICAL CHALLENGE", "ACCIDENTAL ACTIVATION",
    "SLOW OR NO RESPONSE", "CAPTIVE WAIT", "UNNECESSARY STEP(S)", "INFORMATION OVERLOAD",
    "SYSTEM AMNESIA", "BAD PREDICTION", "INCORRECT INFORMATION", "IRREVERSIBLE ACTION",
    "UNWANTED DISCLOSURE", "DATA LOSS", "GRATUITOUS REDUNDANCY", "VARIABLE OUTCOME",
    "WANDERING ELEMENT", "INCONSISTENT APPEARANCE", "AMBIGUOUS HOME", "POOR AESTHETIC",
], key=len, reverse=True)


def _trap_name_to_slug(name: str) -> str:
    return _SLUG_MAP.get(name.upper().strip(), re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_"))


def _normalize_header_text(text: str) -> str:
    """Collapse internal whitespace — handles garbled PDF text like 'UNNECESS AR Y'."""
    return re.sub(r"\s+", " ", text).strip()


def _match_canonical(raw_name: str) -> str | None:
    """Return canonical trap name if raw_name starts with one, else None.
    Falls back to difflib fuzzy match to handle garbled PDF text (e.g. VARIABLE OUTCOME)."""
    upper = raw_name.upper().strip()
    for canonical in _CANONICAL_TRAPS:
        if upper == canonical or upper.startswith(canonical + " ") or upper.startswith(canonical + "-"):
            return canonical
    # Fuzzy fallback — handles font-garbled names like "VARIABCLoEn tOacUt uTsCOME"
    from difflib import get_close_matches
    # Only compare the first N chars of raw_name (proportional to canonical length)
    for canonical in _CANONICAL_TRAPS:
        candidate = upper[:len(canonical) + 10]
        matches = get_close_matches(canonical, [candidate], n=1, cutoff=0.55)
        if matches:
            return canonical
    return None


def _find_trap_headers(words: list) -> list:
    """
    Scan word list for 'TRAP <NAME>' patterns, returning list of
    (canonical_trap_name, y_top) sorted by vertical position.
    Skips headers that don't match a canonical trap name.
    """
    headers = []
    seen_traps: set = set()
    i = 0
    while i < len(words):
        word_text = _normalize_header_text(words[i]["text"])
        if word_text == "TRAP":
            trap_y = words[i]["top"]
            name_parts = []
            j = i + 1
            while j < len(words) and abs(words[j]["top"] - trap_y) < 5:
                name_parts.append(_normalize_header_text(words[j]["text"]))
                j += 1
            if name_parts:
                raw_name = " ".join(name_parts)
                canonical = _match_canonical(raw_name)
                if canonical:
                    if trap_y < 0:
                        # Negative y = reference/cover section at top of PDF — skip
                        pass
                    elif canonical not in seen_traps:
                        headers.append((canonical, trap_y))
                        seen_traps.add(canonical)
                i = j
                continue
        i += 1
    return headers


def extract_v2_examples(pdf_path: Path, output_dir: Path) -> None:
    try:
        import pdfplumber
    except ImportError:
        print("ERROR: pdfplumber not installed. Run: pip install pdfplumber")
        sys.exit(1)

    try:
        from PIL import Image as PilImage
        pillow_available = True
    except ImportError:
        print("WARNING: Pillow not installed — images saved as raw bytes.")
        print("         Run: pip install Pillow")
        pillow_available = False

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[v2 Examples] Processing {pdf_path.name}...")

    trap_images: dict[str, list[bytes]] = {}
    seen_hashes: set = set()

    with pdfplumber.open(str(pdf_path)) as pdf:
        print(f"[v2 Examples] PDF has {len(pdf.pages)} page(s)")

        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words()
            headers = _find_trap_headers(words)

            if not headers:
                print(f"  Page {page_num + 1}: no trap headers found")
                continue

            print(f"  Page {page_num + 1}: found {len(headers)} trap header(s)")
            for name, y in headers:
                slug = _trap_name_to_slug(name)
                print(f"    y={y:.0f}  TRAP {name}  ->  {slug}/")

            # Build sorted list of (y_position, trap_name) boundaries
            # Last trap extends to bottom of page
            boundaries = [(y, name) for name, y in sorted(headers, key=lambda h: h[1])]
            boundaries.append((page.height, None))  # sentinel

            # Extract images from page using pypdf (pdfplumber wraps pypdf)
            # pdfplumber page.images gives dicts with x0, y0 (bottom-left in PDF coords)
            # Convert to top-down: top = page.height - y1 (where y1 is the PDF top of image)
            raw_images = page.images  # list of dicts with x0, y0, x1, y1, stream

            if not raw_images:
                print(f"  Page {page_num + 1}: no images found")
                continue

            print(f"  Page {page_num + 1}: {len(raw_images)} image(s) to assign")

            for img in raw_images:
                # pdfplumber image dicts: top = distance from page top
                img_top = img.get("top", img.get("y0", 0))

                # Find which trap this image belongs to (trap header immediately above)
                assigned_trap = None
                for k in range(len(boundaries) - 1):
                    trap_y, trap_name = boundaries[k]
                    next_y, _ = boundaries[k + 1]
                    if trap_y <= img_top < next_y:
                        assigned_trap = trap_name
                        break

                if assigned_trap is None:
                    # Above the first trap header — skip
                    continue

                # Extract raw image bytes
                try:
                    img_stream = img.get("stream")
                    if img_stream is None:
                        continue
                    img_data = img_stream.get_data()
                except Exception:
                    continue

                if len(img_data) < MIN_IMAGE_BYTES:
                    continue

                img_hash = hash(img_data)
                if img_hash in seen_hashes:
                    continue
                seen_hashes.add(img_hash)

                slug = _trap_name_to_slug(assigned_trap)
                existing = trap_images.get(slug, [])
                if len(existing) >= MAX_IMAGES_PER_TRAP:
                    continue

                trap_images.setdefault(slug, []).append(img_data)

        # Second pass: for any trap that got 0 images, render the page section directly.
        # This captures vector graphics and composite elements that pypdf can't extract.
        traps_with_no_images = [
            (name, y) for name, y in headers
            if _trap_name_to_slug(name) not in trap_images
        ]
        if traps_with_no_images:
            print(f"\n  Rendering {len(traps_with_no_images)} section(s) with no extracted images...")
            for name, y in traps_with_no_images:
                slug = _trap_name_to_slug(name)
                # Find the y-range for this trap section
                section_start = y
                section_end = page.height
                for k in range(len(boundaries) - 1):
                    if boundaries[k][1] == name and boundaries[k + 1][1] is not None:
                        section_end = boundaries[k + 1][0]
                        break

                try:
                    cropped = page.crop((0, section_start, page.width, section_end))
                    rendered = cropped.to_image(resolution=150)
                    buf = io.BytesIO()
                    rendered.save(buf, format="PNG")
                    img_data = buf.getvalue()
                    trap_images[slug] = [img_data]
                    print(f"    Rendered section for {name}  ({section_end - section_start:.0f}pt tall)")
                except Exception as e:
                    print(f"    WARNING: could not render section for {name}: {e}")

    # Save images to disk
    total_saved = 0
    for slug, images in sorted(trap_images.items()):
        trap_dir = output_dir / slug
        trap_dir.mkdir(exist_ok=True)

        # Remove stale images
        for old in trap_dir.glob("img_*.png"):
            old.unlink()

        for i, img_data in enumerate(images):
            out_path = trap_dir / f"img_{i + 1:03d}.png"
            if pillow_available:
                try:
                    from PIL import Image as PilImage
                    img = PilImage.open(io.BytesIO(img_data))
                    img.save(str(out_path), "PNG")
                    total_saved += 1
                except Exception as e:
                    print(f"    WARNING: could not save image for {slug}: {e}")
            else:
                out_path.write_bytes(img_data)
                total_saved += 1

    print(f"\n[v2 Examples] Complete -- {total_saved} images saved across {len(trap_images)} traps.")
    print(f"Output: {output_dir}\n")
    for slug, images in sorted(trap_images.items()):
        print(f"  {slug:45s} {len(images)} image(s)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_v2_examples.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        sys.exit(1)

    output_dir = Path(__file__).parent / "data" / "book_images" / "v2"
    extract_v2_examples(pdf_path, output_dir)
