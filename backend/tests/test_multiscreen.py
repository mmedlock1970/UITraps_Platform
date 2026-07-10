"""
Multi-screen (flow-aware) analysis — construction-level coverage (no API calls).

Covers the plumbing that turns N screenshots into ONE flow-aware analysis:
1. build_multi_screen_blocks labels + interleaves screens (0-based, matching screen_index).
2. Both surviving trap schemas expose regions[] with a screen_index (per-instance G6 shape).
3. _crop_findings_regions crops each regions[] entry against the screen its screen_index names.
4. The rev6 by-trap formatter renders one crop per regions[] entry (multi-screen findings show several).
"""
import base64
import io

import pytest
from PIL import Image, ImageDraw

from src.prompts import build_multi_screen_blocks, build_system_prompt
from src.schema import get_ui_analysis_schema
from src.analyzer import UITrapsAnalyzer, MAX_FLOW_SCREENS
from src.formatters import format_bytrap_report_as_html


# ── 1. Screen labeling ───────────────────────────────────────────────────────

def test_multi_screen_blocks_are_labeled_and_interleaved():
    imgs = [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": c}}
            for c in ("A", "B", "C")]
    blocks = build_multi_screen_blocks(imgs)
    texts = [b["text"] for b in blocks if b["type"] == "text"]
    # 0-based labels matching screen_index, one per screen.
    for i in range(3):
        assert f"[SCREEN {i}]" in texts
    assert any("SINGLE user flow" in t for t in texts)          # framed as one flow
    # Each image is immediately preceded by its label.
    for i, b in enumerate(blocks):
        if b.get("type") == "image":
            assert blocks[i - 1]["text"].startswith("[SCREEN ")
    assert sum(1 for b in blocks if b["type"] == "image") == 3


def test_system_prompt_multi_screen_note_gated_and_cache_safe():
    single = build_system_prompt(version="v2", image_count=1)
    multi = build_system_prompt(version="v2", image_count=3)
    _has = lambda bl: any("MULTI-SCREEN ANALYSIS" in b.get("text", "") for b in bl)
    assert not _has(single), "single-screen must not get the multi-screen note"
    assert _has(multi), "multi-screen must get the note"
    assert "[SCREEN 2]" in " ".join(b.get("text", "") for b in multi)  # 0-based last index of 3
    # The cached scaffold prefix must be identical → cache still hits across single/multi runs.
    assert single[0]["text"] == multi[0]["text"]


# ── 2. Schema shape ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("get_schema,arr,self_serve", [
    (lambda: get_ui_analysis_schema("v2"), "critical_issues", False),          # coached By-Trap
    (lambda: get_ui_analysis_schema("v1", self_serve=True), "critical_issues", True),   # self-serve trap
])
def test_regions_field_shape(get_schema, arr, self_serve):
    schema = get_schema()
    item = schema["properties"][arr]["items"]["properties"]
    assert "region" not in item and "regions" in item, "region must be replaced by regions[]"
    regions = item["regions"]
    assert regions["type"] == "array"
    box = regions["items"]["properties"]
    for f in ("screen_index", "x", "y", "width", "height", "caption"):
        assert f in box, f
    assert regions["items"]["required"] == ["screen_index", "x", "y", "width", "height"]
    # self-serve stays bare (no usage-guidance prose on the array or its box fields).
    if self_serve:
        assert "description" not in regions
        assert "description" not in box["x"]


# ── 3. Per-screen cropping ───────────────────────────────────────────────────

def _screen_png(tmp_path, name, box_xy):
    """A white PNG with a black square drawn at box_xy (fractional) — gives crops contrast so
    the near-blank guard doesn't skip them, and lets us tell screens apart."""
    img = Image.new("RGB", (200, 200), "white")
    d = ImageDraw.Draw(img)
    x, y = int(box_xy[0] * 200), int(box_xy[1] * 200)
    d.rectangle([x, y, x + 50, y + 50], fill="black")
    p = tmp_path / name
    img.save(p)
    return str(p)


def test_crop_findings_regions_uses_the_named_screen(tmp_path):
    s0 = _screen_png(tmp_path, "s0.png", (0.05, 0.05))   # black box top-left
    s1 = _screen_png(tmp_path, "s1.png", (0.70, 0.70))   # black box bottom-right
    analyzer = UITrapsAnalyzer(api_key="test-key-not-used", use_caching=True)
    # Two boxes at the SAME coords (0.70, 0.70) but different screens. Screen 1 has its black box
    # there (→ non-blank crop); screen 0 is white there (→ near-blank, skipped). If screen_index
    # were ignored, both would behave identically — so this pins the attribution.
    findings = [{
        "trap_name": "INCONSISTENT APPEARANCE",
        "regions": [
            {"screen_index": 1, "x": 0.70, "y": 0.70, "width": 0.25, "height": 0.25},
            {"screen_index": 0, "x": 0.70, "y": 0.70, "width": 0.25, "height": 0.25},
        ],
    }]
    analyzer._crop_findings_regions(findings, [s0, s1])
    regs = findings[0]["regions"]
    assert regs[0].get("image_b64"), "screen_index=1 should crop screen 1's black box"
    assert "image_b64" not in regs[1], "screen_index=0 at the same coords is blank → skipped"


def test_screen_count_is_capped(tmp_path):
    # Over the cap → a clear ValueError raised BEFORE any API call, not silent truncation.
    s0 = _screen_png(tmp_path, "s0.png", (0.05, 0.05))
    analyzer = UITrapsAnalyzer(api_key="test-key-not-used")
    ctx = {"users": "first-time shoppers", "tasks": "buy a sofa", "format": "PNG"}
    with pytest.raises(ValueError, match=f"at most {MAX_FLOW_SCREENS} screens"):
        analyzer.analyze_design(s0, ctx, additional_design_files=[s0] * MAX_FLOW_SCREENS)
    # Exactly at the cap does NOT raise for the count reason (fails later, on the mocked API).
    assert MAX_FLOW_SCREENS == 6


def test_crop_out_of_range_screen_index_is_skipped(tmp_path):
    s0 = _screen_png(tmp_path, "s0.png", (0.05, 0.05))
    analyzer = UITrapsAnalyzer(api_key="test-key-not-used", use_caching=True)
    findings = [{"regions": [{"screen_index": 5, "x": 0.05, "y": 0.05, "width": 0.25, "height": 0.25}]}]
    analyzer._crop_findings_regions(findings, [s0])   # only screen 0 exists
    assert "image_b64" not in findings[0]["regions"][0]


# ── 4. Formatter renders one crop per regions[] entry ────────────────────────

_B64 = base64.standard_b64encode(b"fakepng-A").decode()
_B64B = base64.standard_b64encode(b"fakepng-B").decode()


def test_bytrap_formatter_renders_a_crop_per_region():
    report = {
        "summary_headline": "h", "summary_narrative": "n", "positive_observations": [],
        "traps_checked_not_found": [], "moderate_issues": [], "minor_issues": [],
        "critical_issues": [{
            "trap_name": "INCONSISTENT APPEARANCE", "tenet": "HABITUATING",
            "headline": "logo styled two ways", "severity_label": "Medium", "confidence": "Medium",
            "problem": "d", "recommendation": "r",
            "regions": [
                {"screen_index": 0, "x": 0, "y": 0, "width": 0.2, "height": 0.2, "caption": "home header", "image_b64": _B64},
                {"screen_index": 1, "x": 0, "y": 0, "width": 0.2, "height": 0.2, "caption": "results header", "image_b64": _B64B},
            ],
        }],
    }
    html = format_bytrap_report_as_html(report, {"design_name": "T"}, {"kb_version": "v2", "report_style": "trap"})
    assert html.count("<figure class='crop'>") == 2         # one crop per instance
    assert _B64 in html and _B64B in html
    assert "home header" in html and "results header" in html
