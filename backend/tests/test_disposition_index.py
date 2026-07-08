"""
Trap Disposition Index — the By-Issue report's accounting ledger.

One row per taxonomy trap, disposition derived purely from data the model already emits
(issues[].traps[].relationship + coverage). Every trap resolves to exactly one of: found
as an issue (primary → linked; secondary → linked with its relationship), noted under a
coverage bucket, or — appearing nowhere structured — "Not accounted for" (the diagnostic
that catches a trap raised only in an issue's prose). No new model output.
"""
import pytest

from src.formatters import format_issues_report_as_html
from src.schema import _valid_trap_names


def _render(issues_report, kb_version="v2.1"):
    return format_issues_report_as_html(
        issues_report, {"design_name": "Test"}, {"kb_version": kb_version, "report_style": "issues"}
    )


def _base_report():
    return {
        "summary_headline": "h",
        "summary_narrative": "n",
        "issues": [
            {   # Issue 01: primary Distraction + secondary co-occurring Poor Grouping
                "headline": "no starting point",
                "severity_label": "High", "confidence": "High",
                "traps": [
                    {"trap_name": "DISTRACTION", "relationship": "root_cause"},
                    {"trap_name": "POOR GROUPING", "relationship": "co-occurring"},
                ],
                "description": "d", "recommendation": "r",
            },
            {   # Issue 02: single primary
                "headline": "unlabeled icon",
                "severity_label": "High", "confidence": "High",
                "traps": [{"trap_name": "UNCOMPREHENDED ELEMENT", "relationship": "root_cause"}],
                "description": "d", "recommendation": "r",
            },
        ],
        "traps_checked_not_found": [
            {"trap_name": "INVISIBLE ELEMENT", "coverage_status": "not_present"},
            {"trap_name": "SYSTEM AMNESIA", "coverage_status": "not_assessable_artifact"},
            {"trap_name": "INVITING DEAD END", "coverage_status": "not_assessable_context"},
            {"trap_name": "PHYSICAL CHALLENGE", "coverage_status": "partially_assessed"},
        ],
        "positive_observations": [],
    }


@pytest.mark.parametrize("version", ["v2.1"])
def test_index_lists_every_taxonomy_trap_once(version):
    html = _render(_base_report(), kb_version=version)
    assert "Trap disposition index" in html
    # The section renders one pill per taxonomy trap (order is the canonical scan order).
    section = html.split("Trap disposition index", 1)[1]
    for trap in _valid_trap_names(version):
        assert f">{trap}</span>" in section, f"{trap} missing from disposition index"


def test_worth_a_closer_look_renders_between_issues_and_coverage():
    # Guards the By-Issue potential_issues wiring (schema field + formatter section) — the
    # section was historically missing end-to-end in the issues path.
    report = _base_report()
    report["potential_issues"] = [{
        "trap_name": "FORCED SYNTAX", "tenet": "UNDERSTANDABLE", "location": "nav bar",
        "observation": "No visible kids filter.", "why_it_matters": "The kids goal needs a browse path.",
        "why_uncertain": "Dropdown contents are not shown.",
        "check": "Open the TV shows dropdown.", "check_cost": "one click",
        "implication_if_confirmed": "Kids can browse via a sub-filter.",
        "implication_if_ruled_out": "No kids path exists at all.",
    }]
    html = _render(report)
    assert "<div class='section-eyebrow'>Worth a closer look</div>" in html
    assert "Open the TV shows dropdown." in html and "one click" in html
    assert "If confirmed:" in html and "If ruled out:" in html
    # Ordered: Issues → Worth a closer look → Coverage notes.
    assert html.index("Issues identified") < html.index("Worth a closer look") < html.index("Coverage notes")


def test_worth_a_closer_look_absent_when_empty():
    # No potential_issues → no empty section header.
    html = _render(_base_report())
    assert "Worth a closer look" not in html


def test_disposition_index_accounts_for_potential_issues():
    # A trap that appears ONLY as a Worth-a-closer-look entry must resolve to "Worth a closer
    # look" in the index, NOT "Not accounted for" (the prior bug read issues + coverage only).
    report = _base_report()
    report["potential_issues"] = [{
        "trap_name": "BAD PREDICTION", "tenet": "ACCURATE", "location": "search box",
        "observation": "o", "why_it_matters": "w", "check": "c", "check_cost": "one click",
    }]
    html = _render(report)
    section = html.split("Trap disposition index", 1)[1]
    # Find BAD PREDICTION's row and confirm its disposition cell.
    row = section.split(">BAD PREDICTION</span>", 1)[1].split("</tr>", 1)[0]
    assert "Worth a closer look" in row, "BAD PREDICTION should be accounted for via potential_issues"
    assert "Not accounted for" not in row


def test_primary_links_to_its_issue():
    html = _render(_base_report())
    section = html.split("Trap disposition index", 1)[1]
    # DISTRACTION is the primary (root cause) of Issue 01 → a bare link, no relationship label.
    assert "href='#issue-1'>Issue 01</a>" in section
    # UNCOMPREHENDED ELEMENT is the sole trap of Issue 02.
    assert "href='#issue-2'>Issue 02</a>" in section
    # The issue card carries the matching anchor id so the link resolves.
    assert "id='issue-1'" in html and "id='issue-2'" in html


def test_secondary_link_names_the_relationship():
    html = _render(_base_report())
    section = html.split("Trap disposition index", 1)[1]
    # POOR GROUPING is co-occurring in Issue 01 — linked AND relationship-named.
    row = section.split("POOR GROUPING", 1)[1].split("</tr>", 1)[0]
    assert "href='#issue-1'>Issue 01</a>" in row
    assert "co-occurring" in row


def test_uncovered_trap_falls_to_its_coverage_bucket():
    html = _render(_base_report())
    section = html.split("Trap disposition index", 1)[1]
    for trap, label in [("INVISIBLE ELEMENT", "Did not find"),
                        ("SYSTEM AMNESIA", "Couldn't evaluate"),
                        ("INVITING DEAD END", "Couldn't evaluate"),
                        ("PHYSICAL CHALLENGE", "Partially evaluated")]:
        row = section.split(f">{trap}</span>", 1)[1].split("</tr>", 1)[0]
        assert label in row, f"{trap} should show coverage bucket {label!r}"


def test_prose_only_trap_flagged_not_accounted():
    """A trap in neither an issue's traps[] nor coverage is the diagnostic case — it appears
    only in prose, so it renders 'Not accounted for' (the Information Overload scenario)."""
    html = _render(_base_report())
    section = html.split("Trap disposition index", 1)[1]
    # INFORMATION OVERLOAD is absent from issues[].traps[] and coverage here.
    row = section.split("INFORMATION OVERLOAD", 1)[1].split("</tr>", 1)[0]
    assert "Not accounted for" in row


def test_same_trap_twice_in_one_issue_collapses():
    """A trap listed twice in the same issue must render one appearance, not 'Issue 01 · Issue 01'."""
    report = _base_report()
    report["issues"][0]["traps"] = [
        {"trap_name": "DISTRACTION", "relationship": "root_cause"},
        {"trap_name": "DISTRACTION", "relationship": "co-occurring"},  # duplicate, model error
    ]
    html = _render(report)
    section = html.split("Trap disposition index", 1)[1]
    row = section.split(">DISTRACTION</span>", 1)[1].split("</tr>", 1)[0]
    assert row.count("Issue 01") == 1  # collapsed
    assert "co-occurring" not in row   # primary wins over the duplicate's relationship


@pytest.mark.parametrize("report", [
    {"issues": None, "traps_checked_not_found": None, "positive_observations": None},
    {"issues": [{"headline": None, "traps": None, "severity_label": None, "confidence": None}]},
    {"issues": [{"headline": "h", "traps": [{"trap_name": None, "relationship": "root_cause"}]}]},
    {"issues": [], "traps_checked_not_found": [{"trap_name": None, "coverage_status": "not_present"}]},
])
def test_null_fields_do_not_crash_the_report(report):
    """A present-but-null list field or trap_name (`{"traps": null}`) must not crash the whole
    render — `.get(k, [])` returns None for a null value, and `_normalize_trap_name(None)` must
    tolerate it. Regression guard for the null-hardening pass."""
    html = _render(report)
    assert "</body>" in html


def test_fully_accounted_report_has_no_diagnostic_flag():
    """When every non-issue trap is covered, no row is 'Not accounted for'."""
    report = _base_report()
    accounted = {"DISTRACTION", "POOR GROUPING", "UNCOMPREHENDED ELEMENT"}
    accounted |= {c["trap_name"] for c in report["traps_checked_not_found"]}
    for trap in _valid_trap_names("v2.1"):
        if trap not in accounted:
            report["traps_checked_not_found"].append(
                {"trap_name": trap, "coverage_status": "not_present"})
    html = _render(report)
    section = html.split("Trap disposition index", 1)[1]
    assert "Not accounted for" not in section
