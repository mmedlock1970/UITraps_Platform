"""
Regression tests for the reliability/validity quality pass:
  - scorecard vs card confidence consistency (blank/off-vocab → "Low" in both)
  - By-Trap severity backfilled from the source array when severity_label is missing
  - By-Trap scorecard honestly labelled "instances", not "Traps"
  - task→finding matching prefers exact/longest (no short-name stealing)
  - mutual exclusivity: a trap raised as an issue is dropped from "did not find" coverage
  - truncated (partial) by-trap tool output coerces instead of raising a 500
"""
from unittest.mock import Mock, MagicMock

from PIL import Image

from src.formatters import format_issues_report_as_html, format_bytrap_report_as_html
from src.analyzer import UITrapsAnalyzer
from src.schema import get_ui_issues_schema
from src.prompts import build_system_prompt


def _issues_report(**issue_over):
    issue = {"severity_label": "High", "confidence": "High", "headline": "x",
             "problem": "p", "recommendation": "r",
             "traps": [{"trap_name": "DISTRACTION", "tenet": "UNDERSTANDABLE", "relationship": "root_cause"}]}
    issue.update(issue_over)
    return {"summary_headline": "h", "summary_narrative": "n", "issues": [issue],
            "potential_issues": [], "traps_checked_not_found": [], "positive_observations": []}


def _bytrap_report(**crit_over):
    crit = {"trap_name": "DISTRACTION", "tenet": "UNDERSTANDABLE", "headline": "x",
            "problem": "p", "recommendation": "r", "severity_label": "High", "confidence": "High"}
    crit.update(crit_over)
    return {"summary_headline": "h", "summary_narrative": "n", "critical_issues": [crit],
            "moderate_issues": [], "minor_issues": [], "traps_checked_not_found": [], "positive_observations": []}


_ISS_SET = {"kb_version": "v2.1", "report_style": "issues"}
_TRAP_SET = {"kb_version": "v2.1", "report_style": "trap"}


# ── confidence: card must agree with the scorecard bucket (blank → Low) ───────────────────────

def test_byissue_blank_confidence_renders_low_matching_scorecard():
    html = format_issues_report_as_html(_issues_report(confidence=""), {"design_name": "X"}, _ISS_SET)
    assert "c-low'>Low" in html  # card shows the same "Low" the matrix counts blank confidence as


def test_bytrap_blank_confidence_renders_low_matching_scorecard():
    html = format_bytrap_report_as_html(_bytrap_report(confidence=""), {"design_name": "X"}, _TRAP_SET)
    assert "c-low'>Low" in html


# ── By-Trap severity backfill from source array ───────────────────────────────────────────────

def test_bytrap_missing_severity_label_backfills_from_array():
    # A finding in critical_issues with NO severity_label must render High (from its array),
    # not silently collapse to "Medium".
    rep = _bytrap_report()
    rep["critical_issues"][0].pop("severity_label")
    html = format_bytrap_report_as_html(rep, {"design_name": "X"}, _TRAP_SET)
    assert ">High</span>" in html        # severity readout shows High
    assert ">Medium</span>" not in html  # would appear iff severity silently defaulted to Medium


# ── By-Trap scorecard label honesty ─────────────────────────────────────────────────────────

def test_bytrap_scorecard_labeled_instances_not_traps():
    html = format_bytrap_report_as_html(_bytrap_report(), {"design_name": "X"}, _TRAP_SET)
    assert "Number of instances found" in html
    assert "Number of Traps found" not in html


# ── task matching: longest/exact, no short-name stealing ──────────────────────────────────────

def test_task_matching_no_short_name_steal():
    uc = {"design_name": "X", "task_list": [{"description": "Search"},
                                            {"description": "Search and filter results"}]}
    rep = {"summary_headline": "h", "summary_narrative": "n",
           "critical_issues": [
               {"trap_name": "DISTRACTION", "tenet": "UNDERSTANDABLE", "headline": "a", "problem": "p",
                "recommendation": "r", "severity_label": "High", "confidence": "High", "task": "Search"},
               {"trap_name": "MEMORY CHALLENGE", "tenet": "UNDERSTANDABLE", "headline": "b", "problem": "p",
                "recommendation": "r", "severity_label": "High", "confidence": "High",
                "task": "Search and filter results"}],
           "moderate_issues": [], "minor_issues": [], "traps_checked_not_found": [], "positive_observations": []}
    html = format_bytrap_report_as_html(rep, uc, _TRAP_SET)
    # If "Search" (listed first) stole the longer-named finding, the Task 2 group would be empty
    # and its header absent.
    assert "Task 1: Search" in html
    assert "Task 2: Search and filter results" in html


# ── mutual exclusivity: issue XOR coverage (except partially_assessed) ────────────────────────

def test_coverage_drops_trap_already_raised_as_issue():
    rep = _issues_report()
    rep["traps_checked_not_found"] = [
        {"trap_name": "DISTRACTION", "coverage_status": "not_present", "detail": ""},          # contradiction
        {"trap_name": "MEMORY CHALLENGE", "coverage_status": "partially_assessed", "detail": "x"},  # legit
    ]
    html = format_issues_report_as_html(rep, {"design_name": "X"}, _ISS_SET)
    assert "Did not find" not in html      # the contradictory DISTRACTION coverage entry was dropped
    assert "Partially evaluated" in html   # a genuine partially_assessed entry is retained


# ── truncation: partial by-trap tool output coerces, does not 500 ─────────────────────────────

def _mk_analyzer(tool_report):
    def cap(**kw):
        m = Mock()
        m.content = [Mock(type="tool_use", name="ui_analysis_report", input=tool_report)]
        m.stop_reason = "max_tokens"  # simulate truncation
        m.usage = Mock(input_tokens=100, output_tokens=50, cache_creation_input_tokens=0, cache_read_input_tokens=0)
        return m
    a = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    a.client = Mock(); a.client.messages.create.side_effect = cap
    a.model = "m"; a.enrich_model = "e"; a.use_caching = True
    return a


def test_bytrap_truncated_partial_dict_does_not_raise(tmp_path):
    # A truncated tool_use returns a dict missing moderate_issues/minor_issues → must coerce to
    # empty and return, not raise "Missing required field" → 500.
    partial = {"summary_headline": "h", "summary_narrative": "n",
               "critical_issues": [{"trap_name": "DISTRACTION", "tenet": "UNDERSTANDABLE",
                                     "headline": "x", "problem": "p", "recommendation": "r",
                                     "severity_label": "High", "confidence": "High"}]}
    img = tmp_path / "t.png"
    Image.new("RGB", (400, 300), "#ddd").save(img)
    a = _mk_analyzer(partial)
    result = a.analyze_design(
        design_file=str(img),
        user_context={"users": "first-time visitors", "tasks": "buy a sofa",
                       "format": "app", "content_type": "website"},
        kb_version="v2.1", report_style="trap", mode="single", profile="default",
    )
    assert result["status"] == "success"
    assert result.get("html")


# ── By-Issue multi-task grouping: schema + prompt now enable it (coached v2.1 only) ───────────

def _issue_props(schema):
    return schema["properties"]["issues"]["items"]["properties"]


def test_byissue_coached_schema_has_task_field():
    # v2.1 Prompting+KB by-issue: the model can now emit `task` so the report groups by task.
    assert "task" in _issue_props(get_ui_issues_schema("v2.1", self_serve=False))


def test_byissue_selfserve_schema_has_no_task_field():
    # v1 KB-only stays ungrouped by design — no task field in the bare self-serve issues schema.
    assert "task" not in _issue_props(get_ui_issues_schema("v1", self_serve=True))


def test_byissue_system_prompt_instructs_task_attribution():
    blocks = build_system_prompt(version="v2.1", report_style="issues", profile="default")
    text = " ".join(b.get("text", "") for b in blocks)
    assert "`task`" in text  # the issues[] output contract now names the task field


# ── streaming helper: streams when a real context-manager stream exists, else create() ─────────

def _bare_analyzer():
    a = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    a.client = Mock()
    return a


def test_create_message_streams_when_stream_is_a_context_manager():
    a = _bare_analyzer()
    final = object()
    cm = MagicMock()                                   # MagicMock supports the with-protocol
    cm.__enter__.return_value.get_final_message.return_value = final
    a.client.messages.stream.return_value = cm
    out = a._create_message(model="m", max_tokens=16000, system=[], messages=[])
    assert out is final
    a.client.messages.create.assert_not_called()       # took the streaming path


def test_create_message_falls_back_to_create_under_plain_mock():
    a = _bare_analyzer()                                # plain Mock: stream() has no __enter__ on its type
    sentinel = object()
    a.client.messages.create.return_value = sentinel
    out = a._create_message(model="m", max_tokens=16000, system=[], messages=[])
    assert out is sentinel                             # degraded to create()
    a.client.messages.create.assert_called_once()


def test_create_message_small_max_tokens_never_streams():
    a = _bare_analyzer()
    sentinel = object()
    a.client.messages.create.return_value = sentinel
    out = a._create_message(model="m", max_tokens=3000, system=[], messages=[])
    assert out is sentinel
    a.client.messages.stream.assert_not_called()       # below the streaming threshold


# ── By-Trap parity + coverage catch-all (3rd-pass validity fixes) ─────────────────────────────

def test_bytrap_renders_worth_a_closer_look():
    # By-Trap previously dropped potential_issues entirely (By-Issue rendered them). Parity now.
    rep = _bytrap_report()
    rep["potential_issues"] = [{"trap_name": "FORCED SYNTAX", "tenet": "UNDERSTANDABLE",
                                "location": "search box", "observation": "a bare field",
                                "why_it_matters": "users may mistype", "check": "try a query",
                                "check_cost": "one query"}]
    html = format_bytrap_report_as_html(rep, {"design_name": "X"}, _TRAP_SET)
    assert "Worth a closer look" in html
    assert "try a query" in html          # the check text is actually rendered


def test_bytrap_empty_coverage_shows_none_reported():
    # By-Trap now shows the Coverage-notes section with "None reported" instead of omitting it.
    html = format_bytrap_report_as_html(_bytrap_report(), {"design_name": "X"}, _TRAP_SET)
    assert "Coverage notes" in html
    assert "None reported" in html


def test_coverage_offenum_status_is_not_dropped():
    # An off-enum / unexpected coverage_status must stay visible (folded into "Couldn't evaluate"),
    # not silently vanish from the report.
    rep = _bytrap_report()
    rep["traps_checked_not_found"] = [
        {"trap_name": "MEMORY CHALLENGE", "coverage_status": "weird_status", "detail": "d"}]
    html = format_bytrap_report_as_html(rep, {"design_name": "X"}, _TRAP_SET)
    assert "MEMORY CHALLENGE" in html
    assert "Couldn't evaluate" in html


# ── header: Tool coaching + green view label removed from both report styles ──────────────────

def test_header_omits_tool_coaching_and_view_label():
    iss = format_issues_report_as_html(_issues_report(), {"design_name": "X"}, _ISS_SET)
    trap = format_bytrap_report_as_html(_bytrap_report(), {"design_name": "X"}, _TRAP_SET)
    for html in (iss, trap):
        assert "r-view" not in html          # green view label element + its dead CSS both gone
        assert "Tool coaching" not in html   # coaching meta entry removed
    # the report-style value still tells the reader the view
    assert "UI Traps — By Issue" in iss and "By Issue" in iss
    assert "UI Traps — By Trap" in trap and "By Trap" in trap
