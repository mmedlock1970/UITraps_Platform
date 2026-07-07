"""
Render the By-Issue HTML report from a saved fixture — no API call.

Feeds a representative issues_report JSON straight through the REAL production
formatter (`format_issues_report_as_html`, which applies the same boundary
escaping and routes v2.1 to the new-KB renderer), so the output is byte-identical
to what a live analysis would produce. Iterate on formatters.py, re-run this, refresh.

Usage:
    python tools/render_sample.py                       # default fixture + settings
    python tools/render_sample.py --fixture path.json   # custom issues_report
    python tools/render_sample.py --out path.html       # custom output path
"""
import argparse
import base64
import io
import json
import os
import sys

# Make `src` importable when run from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.formatters import format_issues_report_as_html  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FIXTURE = os.path.join(_HERE, "sample_issues_report.json")
DEFAULT_OUT = os.path.join(_HERE, "sample_report.html")

# Mirrors the settings a real two-pass v2.1 By-Issue run attaches (see analyzer.py
# _analysis_settings + metadata.usage). Numbers taken from the last real run log so
# the header meta row reads realistically.
DEFAULT_SETTINGS = {
    "kb_version": "v2.1",
    "mode": "twopass",
    "thorough_mode": False,
    "verbosity": "brief",
    "pass1_model": "sonnet",
    "report_style": "issues",
    "elapsed_seconds": 140.47,
    "truncated": False,
    "usage": {
        "input": 30777,
        "output": 6590,
        "cache_read": 0,
        "cache_creation": 18975,
        "cost": 0.2623,
    },
}

DEFAULT_USER_CONTEXT = {
    "design_name": "PV Web Home Screen",
    "users": ("Family members include adults and children. "
              "Experience with product: Mostly returning users. "
              "Tech savviness: Low — limited tech experience. "
              "Experience with similar interfaces: Some."),
    "tasks": "Get an understanding of what the site offers; Find new releases that are free; Find kids shows",
    "task_list": [
        {"description": "Get an understanding of what the site offers"},
        {"description": "Find new releases that are free"},
        {"description": "Find kids shows"},
    ],
}


def _placeholder_crop_b64() -> str:
    """A wireframe-ish PNG standing in for a region crop (two stacked nav bars)."""
    from PIL import Image, ImageDraw
    w, hgt = 760, 190
    im = Image.new("RGB", (w, hgt), "#f4f5f7")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, hgt - 1], outline="#d2d7de")
    # top bar (retail)
    d.rectangle([0, 0, w, 74], fill="#1b1e24")
    for i, x in enumerate(range(24, 560, 92)):
        d.rectangle([x, 30, x + 70, 44], fill="#3a3f47")
    d.rectangle([600, 24, 736, 50], outline="#565d68", fill="#23282f")
    # bottom bar (prime video)
    d.rectangle([0, 92, w, 156], fill="#2a2f6a")
    for i, x in enumerate(range(24, 520, 86)):
        c = "#ffffff" if i == 0 else "#c9ccdd"
        d.rectangle([x, 118, x + 62, 130], fill=c)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default=DEFAULT_FIXTURE)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    with open(args.fixture, "r", encoding="utf-8") as f:
        issues_report = json.load(f)

    # Inject a placeholder screenshot into the first issue so the crop layout renders
    # (a real fixture has no image bytes). Mockup-only; production supplies real crops.
    _issues = issues_report.get("issues") or []
    if _issues and not _issues[0].get("region_image_b64"):
        _issues[0]["region_image_b64"] = _placeholder_crop_b64()

    html = format_issues_report_as_html(
        issues_report,
        DEFAULT_USER_CONTEXT,
        DEFAULT_SETTINGS,
    )

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)

    n_issues = len(issues_report.get("issues", []))
    n_cov = len(issues_report.get("traps_checked_not_found", []))
    print(f"Rendered {n_issues} issues + {n_cov} coverage notes")
    print(f"  fixture: {args.fixture}")
    print(f"  output:  {args.out}")
    print(f"  open:    file:///{args.out.replace(os.sep, '/')}")


if __name__ == "__main__":
    main()
