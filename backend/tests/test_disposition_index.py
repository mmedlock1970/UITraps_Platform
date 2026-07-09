"""
Trap Disposition Index — the By-Trap report's accounting ledger.

One row per taxonomy trap, disposition derived purely from data the by-trap report already
carries. Every trap resolves to EXACTLY ONE of: reported as a per-trap finding ("Reported
above"), bound only as a secondary within an issue_groups issue ("Within an issue (<rel>)"),
raised solely as a Worth-a-closer-look entry ("Worth a closer look"), noted under a coverage
bucket, or — appearing nowhere structured — "Not accounted for" (the diagnostic that catches
a trap raised only in prose). Precedence: finding > secondary > worth-a-closer-look > coverage.
No new model output.
"""
import pytest

from src.formatters import format_bytrap_report_as_html
from src.schema import _valid_trap_names


def _render(report, kb_version="v2.1"):
    return format_bytrap_report_as_html(
        report, {"design_name": "Test"}, {"kb_version": kb_version, "report_style": "trap"}
    )


def _finding(trap, sev="High"):
    return {"trap_name": trap, "tenet": "UNDERSTANDABLE", "headline": f"{trap} h",
            "problem": "d", "recommendation": "r", "severity_label": sev, "confidence": "High"}


def _base_report():
    return {
        "summary_headline": "h",
        "summary_narrative": "n",
        # Two per-trap findings → both should read "Reported above".
        "critical_issues": [_finding("DISTRACTION"), _finding("UNCOMPREHENDED ELEMENT")],
        "moderate_issues": [],
        "minor_issues": [],
        # DISTRACTION is ALSO bound here (but it's a finding → finding wins). POOR GROUPING is
        # bound ONLY here with no finding of its own → secondary "Within an issue (co-occurring)".
        "issue_groups": [
            {"location": "hero", "traps": [
                {"trap_name": "DISTRACTION", "relationship": "root_cause"},
                {"trap_name": "POOR GROUPING", "relationship": "co_occurring"},
            ]},
        ],
        "traps_checked_not_found": [
            {"trap_name": "INVISIBLE ELEMENT", "coverage_status": "not_present", "detail": "x"},
            {"trap_name": "SYSTEM AMNESIA", "coverage_status": "not_assessable_artifact", "detail": "x"},
            {"trap_name": "INVITING DEAD END", "coverage_status": "not_assessable_context", "detail": "x"},
            {"trap_name": "PHYSICAL CHALLENGE", "coverage_status": "partially_assessed", "detail": "x"},
        ],
        "positive_observations": [],
    }


def _disp_section(html):
    assert "Trap disposition index" in html
    return html.split("Trap disposition index", 1)[1]


def _row(section, trap):
    return section.split(f">{trap}</span>", 1)[1].split("</tr>", 1)[0]


@pytest.mark.parametrize("version", ["v2.1"])
def test_index_lists_every_taxonomy_trap_once(version):
    section = _disp_section(_render(_base_report(), kb_version=version))
    # One pill per taxonomy trap, in canonical scan order.
    for trap in _valid_trap_names(version):
        assert f">{trap}</span>" in section, f"{trap} missing from disposition index"


def test_finding_shows_reported_above():
    section = _disp_section(_render(_base_report()))
    for trap in ("DISTRACTION", "UNCOMPREHENDED ELEMENT"):
        assert "Reported above" in _row(section, trap), f"{trap} should read 'Reported above'"


def test_secondary_bound_trap_names_the_relationship():
    section = _disp_section(_render(_base_report()))
    # POOR GROUPING is co-occurring in an issue with no finding of its own.
    row = _row(section, "POOR GROUPING")
    assert "Within an issue" in row
    assert "co-occurring" in row


def test_finding_wins_over_secondary_binding():
    # DISTRACTION is a finding AND bound in issue_groups → precedence gives "Reported above",
    # never "Within an issue" (guards the exactly-once invariant).
    row = _row(_disp_section(_render(_base_report())), "DISTRACTION")
    assert "Reported above" in row
    assert "Within an issue" not in row


def test_potential_issue_shows_worth_a_closer_look():
    # A trap raised ONLY as a Worth-a-closer-look entry resolves to that bucket (linked),
    # NOT "Not accounted for".
    report = _base_report()
    report["potential_issues"] = [{
        "trap_name": "BAD PREDICTION", "tenet": "ACCURATE", "location": "search box",
        "observation": "o", "why_it_matters": "w", "check": "c", "check_cost": "one click",
    }]
    row = _row(_disp_section(_render(report)), "BAD PREDICTION")
    assert "Worth a closer look" in row
    assert "Not accounted for" not in row


def test_uncovered_trap_falls_to_its_coverage_bucket():
    section = _disp_section(_render(_base_report()))
    for trap, label in [("INVISIBLE ELEMENT", "Did not find"),
                        ("SYSTEM AMNESIA", "Couldn't evaluate"),
                        ("INVITING DEAD END", "Couldn't evaluate"),
                        ("PHYSICAL CHALLENGE", "Partially evaluated")]:
        assert label in _row(section, trap), f"{trap} should show coverage bucket {label!r}"


def test_structurally_absent_trap_flagged_not_accounted():
    """A trap in no finding, no issue_groups binding, no potential_issue, and no coverage bucket
    is the diagnostic case — it renders 'Not accounted for'."""
    section = _disp_section(_render(_base_report()))
    # INFORMATION OVERLOAD appears in none of the structured buckets here.
    assert "Not accounted for" in _row(section, "INFORMATION OVERLOAD")


def test_fully_accounted_report_has_no_diagnostic_flag():
    """When every non-finding trap is covered, no row is 'Not accounted for'."""
    report = _base_report()
    accounted = {"DISTRACTION", "UNCOMPREHENDED ELEMENT", "POOR GROUPING"}
    accounted |= {c["trap_name"] for c in report["traps_checked_not_found"]}
    for trap in _valid_trap_names("v2.1"):
        if trap not in accounted:
            report["traps_checked_not_found"].append(
                {"trap_name": trap, "coverage_status": "not_present", "detail": "x"})
    section = _disp_section(_render(report))
    assert "Not accounted for" not in section


@pytest.mark.parametrize("report", [
    {"critical_issues": None, "moderate_issues": None, "minor_issues": None,
     "issue_groups": None, "traps_checked_not_found": None, "positive_observations": None},
    {"critical_issues": [{"trap_name": None, "headline": None}],
     "moderate_issues": [], "minor_issues": []},
    {"issue_groups": [{"location": "x", "traps": None}]},
    {"issue_groups": [{"traps": [{"trap_name": None, "relationship": "root_cause"}]}]},
    {"traps_checked_not_found": [{"trap_name": None, "coverage_status": "not_present"}]},
])
def test_null_fields_do_not_crash_the_report(report):
    """A present-but-null list field or a null trap_name must not crash the render —
    `.get(k) or []` and `_normalize_trap_name(None)` must tolerate it."""
    html = _render(report)
    assert "</body>" in html
