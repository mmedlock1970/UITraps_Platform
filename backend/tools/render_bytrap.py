"""
Render the By-Trap rev6 report from a saved fixture — no API call.

Mirrors production: injects each trap's verbatim definition from the manifest (as the analyzer
will), drops in a placeholder crop, escapes at the boundary, and renders through the real
`_format_new_kb_bytrap_html`. Iterate on formatters.py, re-run this, refresh.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.formatters import _format_new_kb_bytrap_html, _escape_html_deep  # noqa: E402
from src import pack_generator  # noqa: E402
import render_sample as rs  # reuse DEFAULT_USER_CONTEXT / DEFAULT_SETTINGS / placeholder crop  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(_HERE, "sample_bytrap_report.json")
OUT = os.path.join(_HERE, "sample_bytrap.html")


def _inject_definitions(report, kb_version):
    """Attach each finding's verbatim definition from the (same-lineage) manifest, as the
    analyzer will for By-Trap. v1/v2 fall back to v1.1/v2.1 (identical trap set)."""
    _v = {"v1": "v1.1", "v2": "v2.1"}.get(kb_version, kb_version)
    try:
        m = pack_generator.load_manifest(_v)
        by_upper = {k.upper(): v for k, v in (m.get("verbatim_definitions") or {}).items()}
    except Exception:
        by_upper = {}
    for arr in ("critical_issues", "moderate_issues", "minor_issues"):
        for f in report.get(arr, []):
            if isinstance(f, dict) and not f.get("definition"):
                d = by_upper.get(str(f.get("trap_name", "")).upper())
                if d:
                    f["definition"] = d


def main():
    report = json.load(open(FIXTURE, "r", encoding="utf-8"))
    settings = dict(rs.DEFAULT_SETTINGS)
    settings["report_style"] = "trap"
    _inject_definitions(report, settings.get("kb_version", "v2.1"))
    # placeholder crop on the first critical finding, to exercise the crop layout
    if report.get("critical_issues"):
        report["critical_issues"][0]["region_image_b64"] = rs._placeholder_crop_b64()
        report["critical_issues"][0]["region"] = {"caption": "Top-right toolbar — unlabeled gear glyph"}

    # Escape report, user_context AND settings at the boundary — the renderer assumes
    # pre-escaped input (its meta row interpolates settings values), exactly as the live
    # by-issue entry point does. Mirroring that here keeps the mockup honest about the contract.
    report_esc = _escape_html_deep(report)
    uc_esc = _escape_html_deep(rs.DEFAULT_USER_CONTEXT)
    settings_esc = _escape_html_deep(settings)
    html = _format_new_kb_bytrap_html(report_esc, uc_esc, settings_esc)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    n_traps = len({str(f.get("trap_name", "")).upper()
                   for a in ("critical_issues", "moderate_issues", "minor_issues")
                   for f in report.get(a, []) if isinstance(f, dict)})
    n_inst = sum(len(report.get(a, [])) for a in ("critical_issues", "moderate_issues", "minor_issues"))
    print(f"Rendered {n_traps} traps / {n_inst} instances + {len(report.get('traps_checked_not_found', []))} coverage")
    print(f"  open: file:///{OUT.replace(os.sep, '/')}")


if __name__ == "__main__":
    main()
