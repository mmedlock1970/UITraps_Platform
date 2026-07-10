"""
Haiku dropped — the backend enforces Sonnet-only. A non-Sonnet model request is HARD-REJECTED at
the analyze_design chokepoint (which every path — image, flow, multi-screen — passes through):
no silent fallback to Sonnet, no API call, no token spend. Rationale: a report's config line must
never claim a model the run didn't use, so a silent fallback would make that line lie. Sonnet, an
explicit "sonnet", None, and "" all proceed normally (None/"" default to Sonnet downstream).
"""
from unittest.mock import Mock

import pytest
from PIL import Image

from src.analyzer import UITrapsAnalyzer

_CTX = {"users": "first-time visitors", "tasks": "buy a sofa", "format": "app", "content_type": "website"}


def _img(tmp_path):
    p = tmp_path / "t.png"
    Image.new("RGB", (400, 300), "#ddd").save(p)
    return str(p)


def _analyzer():
    def cap(**kw):
        m = Mock()
        m.content = [Mock(type="tool_use", name="ui_analysis_report", input={
            "summary_headline": "h", "summary_narrative": "n",
            "critical_issues": [], "moderate_issues": [], "minor_issues": []})]
        m.stop_reason = "tool_use"
        m.usage = Mock(input_tokens=10, output_tokens=5, cache_creation_input_tokens=0, cache_read_input_tokens=0)
        return m
    a = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    a.client = Mock()
    a.client.messages.create.side_effect = cap
    a.model = "m"
    a.enrich_model = "e"
    a.use_caching = True
    return a


@pytest.mark.parametrize("bad", ["haiku", "Haiku", " haiku ", "opus", "gpt-4o", "claude-haiku-4-5"])
def test_non_sonnet_is_hard_rejected_before_any_call(tmp_path, bad):
    a = _analyzer()
    with pytest.raises(ValueError, match="model not available"):
        a.analyze_design(design_file=_img(tmp_path), user_context=_CTX, kb_version="v2", pass1_model=bad)
    a.client.messages.create.assert_not_called()  # rejected before token spend; never falls back


@pytest.mark.parametrize("ok", ["sonnet", "Sonnet", " sonnet ", None, ""])
def test_sonnet_or_default_proceeds(tmp_path, ok):
    a = _analyzer()
    res = a.analyze_design(design_file=_img(tmp_path), user_context=_CTX, kb_version="v2",
                           pass1_model=ok, mode="single", profile="default")
    assert res["status"] == "success"
