"""
rev6 BY-TRAP report wiring — the live dispatch renders `_format_new_kb_bytrap_html` for a
trap-style analysis on a new KB (v2 Prompting+KB) or the self-serve profile (v1.0 KB-only),
through a public entry that escapes settings. Task grouping reads each finding's `task` (the
field the live model actually fills, per the user-turn attribution) with `task_context` as a
tolerated alias; the KB-only bare schema omits both and stays flat.
"""
import json
from unittest.mock import Mock

import pytest
from PIL import Image

from src.formatters import format_bytrap_report_as_html
from src.schema import get_ui_analysis_schema
from src.analyzer import UITrapsAnalyzer


def _trap_report():
    return {
        "summary_headline": "h", "summary_narrative": "n",
        "critical_issues": [{"trap_name": "UNCOMPREHENDED ELEMENT", "tenet": "UNDERSTANDABLE",
                             "headline": "Unlabeled icon", "problem": "In the toolbar, a bare glyph.",
                             "recommendation": "Label it", "severity_label": "High", "confidence": "High",
                             "task_context": "Find kids shows"}],
        "moderate_issues": [{"trap_name": "DISTRACTION", "tenet": "UNDERSTANDABLE",
                             "headline": "Hero autoplays", "problem": "The hero pulls focus.",
                             "recommendation": "Pause it", "severity_label": "Medium", "confidence": "High"}],
        "minor_issues": [], "traps_checked_not_found": [], "positive_observations": [],
    }


# ── public entry ────────────────────────────────────────────────────────────

def test_bytrap_entry_renders_rev6_and_escapes_settings():
    html = format_bytrap_report_as_html(
        _trap_report(), {"design_name": "X"},
        # a hostile settings value must be escaped, not injected
        analysis_settings={"kb_version": "v2", "report_style": "trap", "verbosity": "<script>x</script>"},
    )
    assert "UI Traps — By Trap" in html and "trap-card-img" in html  # rev6 chrome
    assert "<script>x</script>" not in html  # escaped at the boundary
    assert "UNCOMPREHENDED ELEMENT" in html and "DISTRACTION" in html


def _multi_task_uc():
    return {"design_name": "X", "task_list": [{"description": "Find kids shows"},
                                              {"description": "Find new releases"}]}


def test_bytrap_entry_groups_by_task_when_task_context_present():
    # Alias path: a finding carrying `task_context` still groups (back-compat).
    uc = _multi_task_uc()
    html = format_bytrap_report_as_html(_trap_report(), uc, {"kb_version": "v2", "report_style": "trap"})
    assert "task-group-label" in html
    assert "Find kids shows" in html          # the task heading
    assert "General" in html                   # the untagged DISTRACTION finding


def test_bytrap_groups_by_task_field_the_model_emits():
    # REGRESSION: the live model fills `task` (not `task_context`). Grouping must fire on it —
    # this is the exact real-world path that previously fell back to a flat list.
    rep = _trap_report()
    rep["critical_issues"][0].pop("task_context", None)
    rep["critical_issues"][0]["task"] = "Find kids shows"
    html = format_bytrap_report_as_html(rep, _multi_task_uc(), {"kb_version": "v2", "report_style": "trap"})
    assert "task-group-label" in html
    assert "Find kids shows" in html          # the task heading
    assert "General" in html                   # the untagged DISTRACTION finding


# ── schema ──────────────────────────────────────────────────────────────────

def test_v21_trap_schema_has_task_context_bare_does_not():
    assert "task_context" in json.dumps(get_ui_analysis_schema("v2"))
    assert "task_context" not in json.dumps(get_ui_analysis_schema("v1", self_serve=True))


# ── live dispatch ────────────────────────────────────────────────────────────

def _run(kb, profile, mode, tmp_path):
    img = tmp_path / "t.png"
    Image.new("RGB", (400, 300), "#ddd").save(img)

    def cap(**kw):
        m = Mock()
        if "tools" in kw:
            m.content = [Mock(type="tool_use", name="ui_analysis_report", input=_trap_report())]
            m.stop_reason = "tool_use"
        else:
            m.content = [Mock(type="text", text="DISTRACTION | home | hero | x")]
            m.stop_reason = "end_turn"
        m.usage = Mock(input_tokens=100, output_tokens=50, cache_creation_input_tokens=0, cache_read_input_tokens=0)
        return m

    a = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    a.client = Mock(); a.client.messages.create.side_effect = cap
    a.model = "m"; a.enrich_model = "e"; a.use_caching = True
    return a.analyze_design(
        design_file=str(img),
        user_context={"users": "first-time visitors", "tasks": "find kids shows", "format": "app", "content_type": "website"},
        kb_version=kb, profile=profile, mode=mode, report_style="trap",
    )


@pytest.mark.parametrize("kb,profile,mode", [("v2", "default", "twopass"), ("v1", "self-serve", "single")])
def test_live_bytrap_renders_rev6_not_legacy(kb, profile, mode, tmp_path):
    html = _run(kb, profile, mode, tmp_path)["html"]
    assert "UI Traps — By Trap" in html and "trap-card-img" in html   # rev6
    assert "FINDING 1" not in html                               # not the legacy formatter

