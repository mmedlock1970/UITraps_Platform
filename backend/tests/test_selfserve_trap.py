"""
KB-only (self-serve) BY-TRAP analysis — Phase 1.

Enables a By-Trap analysis that draws on nothing but the selected raw KB: one API call,
system = stripped KB + a minimal trap output-contract instruction, a bare trap schema, no
coaching, no enrichment pass. These tests lock in the isolation (no leakage) and the wiring,
and confirm the default (Prompting+KB) trap path is untouched.
"""
import json
from unittest.mock import Mock

import pytest
from PIL import Image

from src.schema import get_ui_analysis_schema, UI_ANALYSIS_SCHEMA, _self_serve_trap_schema
from src.prompts import (
    build_system_prompt,
    _build_self_serve_trap_instruction,
)
from src.analyzer import UITrapsAnalyzer


# ── schema ────────────────────────────────────────────────────────────────────

def test_selfserve_trap_schema_is_bare():
    s = get_ui_analysis_schema("v1", self_serve=True)
    blob = json.dumps(s)
    # container the legacy formatter renders
    for arr in ("critical_issues", "moderate_issues", "minor_issues"):
        assert arr in s["properties"]
    item = s["properties"]["critical_issues"]["items"]
    props = item["properties"]
    # no enum on trap_name (names come from the injected KB), only a trap name required
    assert "enum" not in props["trap_name"]
    assert item["required"] == ["trap_name"]
    # NONE of the guidance vocabulary the coaching schema carries
    for leak in ("coverage_status", "relationship", "definition", "tenet", "root_cause",
                 "traps_checked_not_found", "potential_issues"):
        assert leak not in blob, f"self-serve trap schema leaks {leak!r}"
    # no field-level descriptions (bare)
    assert "description" not in props["trap_name"]
    assert s["additionalProperties"] is True


def test_selfserve_trap_schema_is_cached_and_lineage_aware():
    a = get_ui_analysis_schema("v1", self_serve=True)
    b = get_ui_analysis_schema("v1", self_serve=True)  # cached → same object
    assert a is b
    # A different lineage yields a distinct cached object.
    assert get_ui_analysis_schema("v2.1", self_serve=True) is not a


def test_default_trap_schema_unchanged():
    # self_serve defaults False; legacy v1 still returns the untouched legacy schema object.
    assert get_ui_analysis_schema("v1") is UI_ANALYSIS_SCHEMA
    # new-KB trap schema still carries its coaching (enum + coverage taxonomy)
    v21 = json.dumps(get_ui_analysis_schema("v2.1"))
    assert "coverage_status" in v21 and "INVISIBLE ELEMENT" in v21


# ── instruction ───────────────────────────────────────────────────────────────

def test_selfserve_trap_instruction_is_minimal_and_artifact_neutral():
    instr = _build_self_serve_trap_instruction()
    assert "submitted artifact" in instr and "screenshot" not in instr
    assert "grouped by trap" in instr and "ui_analysis_report" in instr
    # carries the output contract only — no evaluation guidance
    low = instr.lower()
    for leak in ("disconfirm", "severity ladder", "promotion path", "whole-interface",
                 "g3", "g4", "g8", "root cause", "tier 1", "coverage_status", "page role"):
        assert leak not in low, f"trap instruction leaks guidance: {leak!r}"


def test_build_system_prompt_selfserve_trap_routes_trap_instruction():
    blocks = build_system_prompt(version="v1", profile="self-serve", report_style="trap")
    assert len(blocks) == 2  # [stripped KB, minimal instruction]
    instr = blocks[1]["text"]
    assert "grouped by trap" in instr and "ui_analysis_report" in instr


# ── analyzer wiring / isolation ────────────────────────────────────────────────

def _trap_tool_response():
    m = Mock()
    m.content = [Mock(type="tool_use", name="ui_analysis_report", input={
        "summary_headline": "h", "summary_narrative": "n",
        "critical_issues": [{"trap_name": "INVISIBLE ELEMENT", "headline": "x", "location": "l",
                             "problem": "p", "recommendation": "r", "severity_label": "High",
                             "confidence": "High"}],
        "moderate_issues": [], "minor_issues": []})]
    m.usage = Mock(input_tokens=100, output_tokens=50, cache_creation_input_tokens=0, cache_read_input_tokens=0)
    m.stop_reason = "tool_use"
    return m


def _mk_analyzer(capture):
    a = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    a.client = Mock()
    a.client.messages.create.side_effect = capture
    a.model = "m"; a.enrich_model = "e"; a.use_caching = True
    return a


def test_selfserve_trap_is_one_call_no_enrichment_renders_legacy(tmp_path):
    img = tmp_path / "t.png"
    Image.new("RGB", (400, 300), "#ddd").save(img)
    calls = []

    def cap(**kw):
        calls.append(kw)
        return _trap_tool_response()

    a = _mk_analyzer(cap)
    # Request twopass to prove self-serve forces a single call and never enriches.
    res = a.analyze_design(
        design_file=str(img),
        user_context={"users": "first-time family visitors", "tasks": "find kids shows", "format": "app", "content_type": "website"},
        kb_version="v1", profile="self-serve", mode="twopass", report_style="trap",
    )
    assert len(calls) == 1, "self-serve trap must be exactly one API call (no enrichment)"
    # the one call carries the bare trap tool + KB-only system, zero leakage
    call = calls[0]
    tools_blob = json.dumps(call["tools"])
    assert '"ui_analysis_report"' in tools_blob
    assert "coverage_status" not in tools_blob and "relationship" not in tools_blob
    sys_blocks = [b["text"] for b in call["system"]]
    assert "UNATTRACTIVE APPEARANCE" in sys_blocks[0]  # the v1 KB, verbatim
    assert "grouped by trap" in sys_blocks[1]
    # rendered via the legacy By-Trap formatter (not the by-issue renderer)
    assert res["html"] and "By Trap" in res["html"]
    # coverage complement was derived (26 v1 traps − 1 reported = 25), model never saw the vocab
    tcnf = res["report"]["traps_checked_not_found"]
    assert len(tcnf) == 25 and {c["coverage_status"] for c in tcnf} == {"not_present"}
    assert "INVISIBLE ELEMENT" not in {c["trap_name"] for c in tcnf}


def test_selfserve_trap_tenets_derived_upper_matching_v21():
    a = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    report = {"critical_issues": [{"trap_name": "DISTRACTION", "headline": "h"}],
              "moderate_issues": [], "minor_issues": []}
    a._fill_selfserve_trap_tenets(report)
    tenet = report["critical_issues"][0]["tenet"]
    # non-empty AND UPPER (same case the coached v2.1 trap schema emits from its enum)
    assert tenet and tenet == tenet.upper()


def test_selfserve_trap_coverage_carries_both_vocabularies():
    """Coverage must render under either formatter branch: new-KB reads coverage_status,
    legacy (v1/v2) reads the testable boolean."""
    a = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    report = {"critical_issues": [{"trap_name": "DISTRACTION"}], "moderate_issues": [], "minor_issues": []}
    a._derive_selfserve_trap_coverage(report, "v1")
    cov = report["traps_checked_not_found"]
    assert cov and all(c["coverage_status"] == "not_present" and c["testable"] is True for c in cov)
    assert "DISTRACTION" not in {c["trap_name"] for c in cov}  # reported trap excluded


@pytest.mark.parametrize("kbv", ["v1", "v2.1"])
def test_selfserve_trap_render_survives_malformed_findings(kbv, tmp_path):
    """A permissive bare schema can yield a stray non-dict finding. Drive the REAL analyze_design
    path (not a hand-rolled copy of the filter) so this proves PRODUCTION strips them before the
    formatter's per-finding .get() reads, for both legacy and new-KB lineages."""
    img = tmp_path / "t.png"
    Image.new("RGB", (400, 300), "#ddd").save(img)

    def cap(**kw):
        m = Mock()
        m.content = [Mock(type="tool_use", name="ui_analysis_report", input={
            "summary_headline": "h", "summary_narrative": "n",
            # deliberately malformed: a string and a None mixed with a real finding
            "critical_issues": [{"trap_name": None}, "junk", None,
                                {"trap_name": "DISTRACTION", "headline": "h"}],
            "moderate_issues": [], "minor_issues": []})]
        m.usage = Mock(input_tokens=100, output_tokens=50, cache_creation_input_tokens=0, cache_read_input_tokens=0)
        m.stop_reason = "tool_use"
        return m

    a = _mk_analyzer(cap)
    res = a.analyze_design(
        design_file=str(img),
        user_context={"users": "first-time visitors", "tasks": "find kids shows", "format": "app", "content_type": "website"},
        kb_version=kbv, profile="self-serve", report_style="trap",
    )
    assert res["html"] and "</body>" in res["html"]
    # the one real finding survived; the junk elements were stripped
    assert "DISTRACTION" in res["html"]
    assert all(isinstance(f, dict) for f in res["report"]["critical_issues"])
