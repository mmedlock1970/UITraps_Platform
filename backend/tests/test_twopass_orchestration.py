"""
Phase 2b: two-pass orchestration in the analyzer, with the Anthropic client mocked.

Verifies the wiring without spending on the API:
  - detection call goes out with NO tool (free-text candidate list) and the detection pack,
  - candidates are matched and only their chunks (+ core pack) reach the adjudication call,
  - the adjudication call reuses the report schema/tool and its system prompt is sliced,
  - usage is summed across both passes and _twopass provenance is recorded.
"""
import types

import pytest

from src.analyzer import UITrapsAnalyzer
from src import pack_generator as pg


def _usage(inp=100, out=50):
    return types.SimpleNamespace(
        input_tokens=inp, output_tokens=out,
        cache_read_input_tokens=0, cache_creation_input_tokens=0,
    )


def _text_response(text):
    block = types.SimpleNamespace(type="text", text=text)
    return types.SimpleNamespace(content=[block], stop_reason="end_turn", usage=_usage())


def _tool_response(report):
    block = types.SimpleNamespace(type="tool_use", input=report)
    return types.SimpleNamespace(content=[block], stop_reason="end_turn", usage=_usage(200, 300))


VALID_REPORT = {
    "summary_headline": "A headline about the design and its stated goal here now.",
    "summary_narrative": "A short narrative about user experience implications.",
    "critical_issues": [],
    "moderate_issues": [],
    "minor_issues": [],
    "positive_observations": [],
    "potential_issues": [],
    "traps_checked_not_found": [],
}


@pytest.fixture
def analyzer():
    return UITrapsAnalyzer(api_key="test-key-not-used", use_caching=True)


def test_twopass_orchestration_end_to_end(analyzer, monkeypatch):
    manifest = pg.ensure_current("v2")
    names = [t["trap"] for t in manifest["traps"]]
    trap_a, trap_b = names[0], names[3]

    # Detection returns two matched candidates (one as a markdown table row) + one bogus line.
    detection_text = (
        f"{trap_a} | login | submit button | disabled with no explanation\n"
        f"| {trap_b} | cart | quantity field | silently caps at 10\n"
        "SOMETHING NOT A TRAP | x | y | z\n"
    )

    calls = []

    def fake_create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return _text_response(detection_text)
        return _tool_response(dict(VALID_REPORT))

    # Patch the analyzer's model-call seam (which routes create vs stream) so the test never hits
    # the real API regardless of the max_tokens streaming threshold.
    monkeypatch.setattr(analyzer, "_create_message", fake_create)

    fake_image = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "x"}}
    report = analyzer._twopass(
        design_file="dummy.png",
        user_context={"users": "u", "tasks": "t", "format": "PNG"},
        kb_version="v2",
        preloaded_image=fake_image,
    )

    # Two API calls: detection then adjudication.
    assert len(calls) == 2
    det_call, adj_call = calls

    # Detection call: no tool, budget >= 4000.
    assert "tools" not in det_call or not det_call.get("tools")
    assert det_call["max_tokens"] >= 4000

    # Adjudication call: forces the report tool, budget >= 8000.
    assert adj_call["tools"][0]["name"] == "ui_analysis_report"
    assert adj_call["tool_choice"]["name"] == "ui_analysis_report"
    assert adj_call["max_tokens"] >= 8000

    # Adjudication system prompt is sliced: contains the matched chunks. The variable
    # chunks live in their own uncached trailing block; mechanics + core stay cached.
    adj_system_text = " ".join(b["text"] for b in adj_call["system"])
    assert "### TRAP:" in adj_system_text
    assert adj_call["system"][-1].get("cache_control") is None      # chunks block uncached
    assert adj_call["system"][0].get("cache_control")               # mechanics cached
    # Raw detection output is forwarded verbatim (nothing dropped), and the loaded-note
    # names the matched traps.
    user_text = " ".join(
        b["text"] for b in adj_call["messages"][0]["content"] if b.get("type") == "text"
    )
    assert trap_a in user_text and trap_b in user_text
    assert "SOMETHING NOT A TRAP" in user_text        # unmatched line preserved, not dropped
    assert "matched traps" in user_text               # loaded-note present

    # Provenance + summed usage (detection 100/50 + adjudication 200/300).
    meta = report.get("_twopass_meta")
    assert meta and set(meta["candidates_matched"]) == {trap_a, trap_b}
    assert meta["candidates_unmatched"]  # the bogus line surfaced, not dropped
    assert meta["kb_master_sha256"] == pg.master_hash("v2")
    u = report["_usage_last"]
    assert u["input"] == 300 and u["output"] == 350


def test_twopass_zero_candidates_still_adjudicates(analyzer, monkeypatch):
    pg.ensure_current("v2")
    calls = []

    def fake_create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return _text_response("NONE")
        return _tool_response(dict(VALID_REPORT))

    # Patch the analyzer's model-call seam (which routes create vs stream) so the test never hits
    # the real API regardless of the max_tokens streaming threshold.
    monkeypatch.setattr(analyzer, "_create_message", fake_create)
    fake_image = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "x"}}
    report = analyzer._twopass(
        design_file="dummy.png",
        user_context={"users": "u", "tasks": "t", "format": "PNG"},
        kb_version="v2",
        preloaded_image=fake_image,
    )
    # Adjudication still runs (coverage notes must be produced even with no candidates).
    assert len(calls) == 2
    assert report["_twopass_meta"]["candidates_matched"] == []
    # No chunks loaded, so the adjudication system prompt has the core pack but no TRAP chunk.
    adj_system_text = " ".join(b["text"] for b in calls[1]["system"])
    assert "### TRAP:" not in adj_system_text


def test_twopass_rejects_legacy_kb(analyzer):
    with pytest.raises(ValueError, match="only supported for new KBs"):
        analyzer._twopass(
            design_file="dummy.png",
            user_context={"users": "u", "tasks": "t", "format": "PNG"},
            kb_version="v1",
            preloaded_image={"type": "image", "source": {}},
        )
