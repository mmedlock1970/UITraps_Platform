"""
Flow-path (analyze_flow_diagram) PARITY tests.

The flow path now delegates to analyze_design, so a Figma run must honor the same axes as the
image path: coaching lock (profile), report_style, pass-count (single vs two-pass), and the
single-call cross-screen routing. These tests mock ONLY the Anthropic client — `_pass1`,
`build_system_prompt`, the deprecation guard, schema/tool selection, and the multi-screen
message assembly all run for real (the previous suite patched `_pass1` out, so none of that
was covered).

Call-count contract used below:
  • a "report pass" calls the client WITH `tools` (structured tool output);
  • the two-pass DETECTION pass calls the client WITHOUT `tools` (a text candidate list);
  • new-KB enrichment is skipped (Pass-1 authoritative), so single-pass = exactly one report call.
"""
from unittest.mock import Mock

import pytest
from PIL import Image

from src.analyzer import UITrapsAnalyzer, MAX_FLOW_SCREENS


# ── fixtures / helpers ───────────────────────────────────────────────────────

def _frames(tmp_path, n):
    frames = []
    for i in range(n):
        p = tmp_path / f"frame{i}.png"
        Image.new("RGB", (400, 300), "#ddd").save(p)
        frames.append({"id": f"f{i}", "name": f"Screen {i}", "image_path": str(p)})
    return frames


_ISSUES = {
    "summary_headline": "h", "summary_narrative": "n",
    "issues": [{"severity_label": "High", "confidence": "High", "headline": "Icon unclear",
                "problem": "A bare glyph in the toolbar.", "recommendation": "Label it",
                "traps": [{"trap_name": "UNCOMPREHENDED ELEMENT", "tenet": "UNDERSTANDABLE",
                           "relationship": "root_cause"}]}],
    "potential_issues": [], "traps_checked_not_found": [], "positive_observations": [],
}
_TRAP = {
    "summary_headline": "h", "summary_narrative": "n",
    "critical_issues": [{"trap_name": "UNCOMPREHENDED ELEMENT", "tenet": "UNDERSTANDABLE",
                         "headline": "Icon unclear", "problem": "A bare glyph in the toolbar.",
                         "recommendation": "Label it", "severity_label": "High", "confidence": "High"}],
    "moderate_issues": [], "minor_issues": [], "traps_checked_not_found": [], "positive_observations": [],
}

_UC = {"users": "first-time visitors", "tasks": "buy a sofa", "format": "app", "content_type": "website"}


def _analyzer(report_for_tool):
    """Analyzer whose Anthropic client is a Mock recording every call. Report passes (tools
    present) return `report_for_tool`; detection passes (no tools) return a text candidate line."""
    calls = []

    def cap(**kw):
        calls.append(kw)
        m = Mock()
        if "tools" in kw:
            m.content = [Mock(type="tool_use", name="ui_report", input=report_for_tool)]
            m.stop_reason = "tool_use"
        else:
            m.content = [Mock(type="text", text="UNCOMPREHENDED ELEMENT | Screen 0 | icon | unclear")]
            m.stop_reason = "end_turn"
        m.usage = Mock(input_tokens=100, output_tokens=50,
                       cache_creation_input_tokens=0, cache_read_input_tokens=0)
        return m

    a = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    a.client = Mock()
    a.client.messages.create.side_effect = cap
    a.model = "m"
    a.enrich_model = "e"
    a.use_caching = True
    return a, calls


def _tool_calls(calls):
    return [kw for kw in calls if "tools" in kw]


def _detection_calls(calls):
    return [kw for kw in calls if "tools" not in kw]


def _count_images(kw):
    msgs = kw.get("messages") or []
    content = msgs[0]["content"] if msgs else []
    return sum(1 for b in content if isinstance(b, dict) and b.get("type") == "image")


# ── (a) v1.0 flow resolves to self-serve and does NOT trip the deprecation guard ─────────────

def test_flow_v1_selfserve_does_not_trip_guard(tmp_path):
    a, calls = _analyzer(_ISSUES)
    result = a.analyze_flow_diagram(
        frames=_frames(tmp_path, 2), user_context=_UC,
        kb_version="v1", profile="self-serve", report_style="issues", mode="single",
    )
    assert result["status"] == "success" and result.get("html")
    # self-serve injects the raw KB as REFERENCE MATERIAL — proof the self-serve prompt (not the
    # coached scaffold, which would have raised the v1 guard) was the one actually built.
    sys_texts = " ".join(b.get("text", "") for kw in calls for b in (kw.get("system") or []))
    assert "REFERENCE MATERIAL" in sys_texts


def test_flow_v1_default_profile_still_trips_guard(tmp_path):
    # Regression: the guard is real. A coached (default) v1 flow MUST raise — only the locked
    # self-serve profile (above) avoids it. This is the exact leak that was reported.
    a, _ = _analyzer(_TRAP)
    with pytest.raises(ValueError, match="deprecated for version 'v1'"):
        a.analyze_flow_diagram(frames=_frames(tmp_path, 2), user_context=_UC,
                               kb_version="v1", profile="default", report_style="trap", mode="single")


# ── (d) frames route through the SINGLE-call preloaded_images path ───────────────────────────

def test_flow_single_call_carries_all_screens(tmp_path):
    a, calls = _analyzer(_TRAP)
    a.analyze_flow_diagram(frames=_frames(tmp_path, 3), user_context=_UC,
                           kb_version="v2", profile="default", report_style="trap", mode="single")
    tcs = _tool_calls(calls)
    assert len(tcs) == 1                 # ONE cross-screen call — not 3 stitched per-frame calls
    assert _count_images(tcs[0]) == 3    # all three screens in that one call (_n_screens == 3)


# ── (c) one-pass vs two-pass pass-count is observably different ──────────────────────────────

def test_flow_single_pass_is_one_report_call(tmp_path):
    a, calls = _analyzer(_TRAP)
    a.analyze_flow_diagram(frames=_frames(tmp_path, 2), user_context=_UC,
                           kb_version="v2", profile="default", report_style="trap", mode="single")
    assert len(_tool_calls(calls)) == 1
    assert len(_detection_calls(calls)) == 0  # no detection pass in single-pass


def test_flow_twopass_runs_detection_then_adjudication(tmp_path):
    a, calls = _analyzer(_TRAP)
    a.analyze_flow_diagram(frames=_frames(tmp_path, 2), user_context=_UC,
                           kb_version="v2", profile="default", report_style="trap", mode="twopass")
    assert len(_detection_calls(calls)) == 1  # detection pass (candidate list, no tools)
    assert len(_tool_calls(calls)) == 1       # adjudication pass (tool output)
    # both passes carry the full multi-screen artifact
    assert _count_images(_detection_calls(calls)[0]) == 2
    assert _count_images(_tool_calls(calls)[0]) == 2


# ── (b) report_style drives the tool/schema and the rendered report shape ────────────────────

# (By-Issue report style retired — the by-issue-mode render test was removed; By Trap below is the
# sole rendered style.)


def test_flow_report_style_trap_drives_tool_and_render(tmp_path):
    a, calls = _analyzer(_TRAP)
    r = a.analyze_flow_diagram(frames=_frames(tmp_path, 2), user_context=_UC,
                               kb_version="v2", profile="default", report_style="trap", mode="single")
    assert "UI Traps — By Trap" in r["html"]
    names = [t["name"] for kw in _tool_calls(calls) for t in kw["tools"]]
    assert "ui_analysis_report" in names


# ── unchanged contract: no exportable frames is a clear error ────────────────────────────────

def test_flow_no_exportable_frames_raises(tmp_path):
    a, _ = _analyzer(_TRAP)
    with pytest.raises(ValueError, match="No exportable frames"):
        a.analyze_flow_diagram(frames=[{"id": "x", "name": "x", "image_path": None}],
                               user_context=_UC, kb_version="v2")


# ── item 6: >6-frame file truncates-with-notice (NOT hard-reject / 400) ───────────────────────

def test_flow_over_cap_truncates_with_notice(tmp_path):
    # Simulates app.py exporting the first 6 of a 23-frame file. The run SUCCEEDS (no 400) and
    # the report discloses BOTH counts so an un-analyzed-frame miss reads as truncation, not a KB gap.
    a, calls = _analyzer(_TRAP)
    r = a.analyze_flow_diagram(frames=_frames(tmp_path, MAX_FLOW_SCREENS), user_context=_UC,
                               kb_version="v2", profile="default", report_style="trap",
                               mode="single", total_frames=23)
    assert r["status"] == "success"
    assert len(_tool_calls(calls)) == 1               # still ONE cross-screen call over the 6 frames
    assert "Analyzed 6 of 23 frames" in r["html"]
    assert "17 frames were not analyzed" in r["html"]


# (The by-issue truncation-notice test was retired with the By-Issue report style; the notice is
# covered on the sole by-trap path by test_flow_over_cap_truncates_with_notice above.)


def test_flow_within_cap_has_no_notice(tmp_path):
    # total == analyzed (nothing skipped) → no partial-coverage banner. Same when total is unset.
    a, _ = _analyzer(_TRAP)
    r = a.analyze_flow_diagram(frames=_frames(tmp_path, 3), user_context=_UC, kb_version="v2",
                               profile="default", report_style="trap", mode="single", total_frames=3)
    assert "Partial coverage" not in r["html"]
    a2, _ = _analyzer(_TRAP)
    r2 = a2.analyze_flow_diagram(frames=_frames(tmp_path, 3), user_context=_UC, kb_version="v2",
                                 profile="default", report_style="trap", mode="single")
    assert "Partial coverage" not in r2["html"]
