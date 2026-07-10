"""
Task 1 (new-KB integration) verification — no API calls.

Covers the four Task-1 behaviors for the sole surviving Prompting+KB config
(v2). The legacy Prompting+KB pathway (v1 / v2) is deprecated and now raises,
so its regression tests are removed; v1 survives only as a KB-only (self-serve)
version, exercised via the schema/formatter predicates below (is_new_kb=False):

1. Wiring: single-mode detection loads each version's own master file.
2. Prompt: the new-KB system prompt is mechanics-only (no false-alarm priority,
   disconfirmation-first ordering, Tier vocabulary, or `testable` mechanism) and
   speaks the new vocabulary (High/Medium/Low severity & confidence, coverage_status, G8).
3. Schema: new-KB output schema uses the new confidence enum, adds severity_label,
   swaps `testable` for `coverage_status`, and drops the tier-only buckets.
4. Formatter: new-KB reports render Issues / Coverage notes with the new labels,
   while legacy (v1 KB-only) reports still render Traps Found / Traps Not Found.
"""
import sys
from pathlib import Path

import pytest

# Allow `import src...` when run from the backend/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.knowledge_extractor import load_analysis_reference
from src.prompts import build_system_prompt, build_user_message
from src.schema import (
    get_ui_analysis_schema,
    is_new_kb,
    UI_ANALYSIS_SCHEMA,
    NEW_KB_CONFIDENCE_LEVELS,
)
from src.formatters import format_report_as_html


NEW_KBS = ["v2"]
LEGACY_KBS = ["v1"]  # v1 survives only as a KB-only version; v1.1/v2 retired from the test matrix

# Strings that must NOT appear in a new-KB system prompt (Task 1 removals).
FORBIDDEN_IN_NEW_PROMPT = [
    "false alarm",
    "minimize false",
    "PENALTY FOR FALSE",
    "Tier 1",
    "Tier 2",
    "Tier 3",
    "testable",
    "disconfirmation",  # the meta-instruction was reworded to avoid this token
]


# ── 1. Wiring ────────────────────────────────────────────────────────────────

def test_each_version_loads_its_own_master():
    v1 = load_analysis_reference("v1")
    v21 = load_analysis_reference("v2")
    # Distinct content per surviving config — v1 (KB-only) vs v2 (Prompting+KB).
    assert v1 != v21
    assert "v2" in v21.splitlines()[0]
    # The new master carries the new global-rules structure.
    assert "GLOBAL RULES" in v21


def test_unknown_version_falls_back_to_v21():
    # v2.0 support was removed; the analysis-reference fallback is now v2.
    assert load_analysis_reference("bogus") == load_analysis_reference("v2")


# ── 2. Prompt (mechanics-only) ───────────────────────────────────────────────

@pytest.mark.parametrize("version", NEW_KBS)
def test_new_kb_prompt_is_clean_of_legacy_vocab(version):
    system_text = build_system_prompt(version=version)[0]["text"]
    lowered = system_text.lower()
    for bad in FORBIDDEN_IN_NEW_PROMPT:
        assert bad.lower() not in lowered, f"{bad!r} leaked into {version} system prompt"


@pytest.mark.parametrize("version", NEW_KBS)
def test_new_kb_prompt_speaks_new_vocabulary(version):
    system_text = build_system_prompt(version=version)[0]["text"]
    for token in ("coverage_status", "severity_label", "confidence"):
        assert token in system_text
    # Confidence & severity now use a unified High/Medium/Low scale.
    assert '"High", "Medium", "Low"' in system_text
    # The retired confidence vocabulary must not reappear.
    for dead in ("Confirmed", "Probable", "Flagged"):
        assert dead not in system_text, f"dead token {dead!r} leaked into {version} system prompt"
    # G8 section language present (headers are upper-cased in the prompt).
    lowered = system_text.lower()
    assert "coverage notes" in lowered
    assert "worth a closer look" in lowered


@pytest.mark.parametrize("version", NEW_KBS)
def test_new_kb_prompt_loads_matching_master(version):
    blocks = build_system_prompt(version=version)
    kb_block = blocks[1]["text"]
    assert version in kb_block  # the master's own header names the version


def test_new_kb_trap_name_sets():
    v21 = build_system_prompt(version="v2")[0]["text"]
    # v2 uses the 27-trap set (POOR AESTHETIC + INCORRECT INFORMATION).
    assert "POOR AESTHETIC" in v21 and "INCORRECT INFORMATION" in v21


# ── 2b. Legacy Prompting+KB is deprecated ────────────────────────────────────

@pytest.mark.parametrize("version", LEGACY_KBS)
def test_legacy_promptingkb_pathway_raises(version):
    # The legacy (non-new-KB) Prompting+KB scaffold was removed; building a
    # Prompting+KB system prompt for a legacy version must now raise. v1's only
    # supported route is KB-only (self-serve), which does not call this.
    with pytest.raises(ValueError, match="deprecated"):
        build_system_prompt(version=version)


# ── 2c. User message (the OTHER prompt sent to the model) ────────────────────
# build_user_message is shared and reaches new-KB runs; it must not re-inject the
# legacy detection philosophy the new-KB system prompt was cleaned of.

_IMG = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "x"}}
_CTX = {"users": "shoppers", "tasks": "buy a deck", "format": "PNG", "content_type": "website"}


def _user_text(version):
    blocks = build_user_message(_CTX, _IMG, verbosity="standard", version=version)
    return " ".join(b.get("text", "") for b in blocks if b.get("type") == "text")


@pytest.mark.parametrize("version", NEW_KBS)
def test_new_kb_user_message_is_clean(version):
    text = _user_text(version)
    for bad in ("Tier 1", "Tier 2", "Tier 3", "Critical/Moderate/Minor",
                "gated decision procedure", "RESPECT PAGE ROLES", "testable",
                "Confirmed", "Probable", "Flagged"):
        assert bad not in text, f"{bad!r} leaked into {version} user message"
    assert "High / Medium / Low" in text
    assert "severity_label" in text


def test_trap_count_per_version():
    # v2 (Prompting+KB) is the only config whose user message runs this path.
    assert "Check all 27 Traps" in _user_text("v2")


# ── 3. Schema ────────────────────────────────────────────────────────────────

def test_is_new_kb_membership():
    assert all(is_new_kb(v) for v in NEW_KBS)
    assert not any(is_new_kb(v) for v in LEGACY_KBS)


@pytest.mark.parametrize("version", NEW_KBS)
def test_new_kb_schema_vocabulary(version):
    schema = get_ui_analysis_schema(version)
    item = schema["properties"]["critical_issues"]["items"]["properties"]
    assert item["confidence"]["enum"] == NEW_KB_CONFIDENCE_LEVELS
    assert "severity_label" in item
    tcnf = schema["properties"]["traps_checked_not_found"]["items"]
    assert tcnf["required"] == ["trap_name", "coverage_status", "detail"]  # detail is mandatory G6 evidence
    assert "coverage_status" in tcnf["properties"]
    # "Worth a closer look" (potential_issues) carries the richer entry, no confidence.
    pot = schema["properties"]["potential_issues"]["items"]
    assert "confidence" not in pot["properties"]
    for f in ("why_it_matters", "check", "check_cost", "implication_if_confirmed", "implication_if_ruled_out"):
        assert f in pot["properties"], f
    # Tier-only buckets are dropped from the new-KB schema.
    assert "flagged_for_human_review" not in schema["properties"]
    assert "incomplete_flow_findings" not in schema["properties"]


@pytest.mark.parametrize("version", LEGACY_KBS + [None, "bogus"])
def test_legacy_schema_is_the_untouched_object(version):
    # Legacy versions get the exact same schema object (no vocabulary changes).
    assert get_ui_analysis_schema(version) is UI_ANALYSIS_SCHEMA
    conf = UI_ANALYSIS_SCHEMA["properties"]["critical_issues"]["items"]["properties"]["confidence"]
    assert conf["enum"] == ["high", "medium", "low"]


# ── 4. Formatter ─────────────────────────────────────────────────────────────

def _new_kb_report():
    return {
        "summary_headline": "Checkout entry points appear buried.",
        "summary_narrative": "The path to purchase appears indirect.",
        "critical_issues": [{
            "trap_name": "INVITING DEAD END", "tenet": "UNDERSTANDABLE",
            "headline": "CTA may lead somewhere unexpected", "location": "Screen 1",
            "problem": "The label suggests purchase but appears to open a form.",
            "recommendation": "Consider aligning label with destination.",
            "confidence": "High", "severity_label": "High",
        }],
        "moderate_issues": [{
            "trap_name": "MEMORY CHALLENGE", "tenet": "UNDERSTANDABLE",
            "headline": "Users may need to recall a code", "location": "Screen 3",
            "problem": "A code shown earlier is required later with no cue.",
            "recommendation": "Consider carrying the value forward.",
            "confidence": "Medium", "severity_label": "Medium",
        }],
        "minor_issues": [{
            "trap_name": "POOR AESTHETIC", "tenet": "BEAUTIFUL",
            "headline": "Dense chrome", "location": "Header",
            "problem": "The header is visually busy.", "recommendation": "Simplify.",
            "confidence": "Low", "severity_label": "Low",
        }],
        "positive_observations": ["Clear typography."],
        "potential_issues": [{
            "trap_name": "FORCED SYNTAX", "tenet": "UNDERSTANDABLE", "location": "nav bar",
            "observation": "No visible kids filter.",
            "why_it_matters": "The kids goal needs a browse path.",
            "why_uncertain": "Dropdown contents are not shown.",
            "check": "Open the TV shows dropdown.", "check_cost": "one click",
            "implication_if_confirmed": "Kids can browse via a sub-filter.",
            "implication_if_ruled_out": "No kids path exists at all (Invisible Element).",
        }],
        "traps_checked_not_found": [
            {"trap_name": "DATA LOSS", "coverage_status": "not_present", "detail": "No destructive actions shown"},
            {"trap_name": "SLOW OR NO RESPONSE", "coverage_status": "not_assessable_artifact", "detail": "a live product"},
            {"trap_name": "BAD PREDICTION", "coverage_status": "not_assessable_context", "detail": "the stated goal (C2)"},
        ],
    }


def _legacy_report():
    return {
        "summary_headline": "x", "summary_narrative": "y",
        "critical_issues": [{
            "trap_name": "DISTRACTION", "tenet": "UNDERSTANDABLE", "headline": "h",
            "location": "l", "problem": "p", "recommendation": "r", "confidence": "high",
        }],
        "moderate_issues": [], "minor_issues": [], "positive_observations": [],
        "potential_issues": [],
        "traps_checked_not_found": [
            {"trap_name": "DATA LOSS", "testable": True},
            {"trap_name": "SLOW OR NO RESPONSE", "testable": False},
        ],
    }


@pytest.mark.parametrize("version", NEW_KBS)
def test_new_kb_report_renders_new_sections(version):
    html = format_report_as_html(
        _new_kb_report(), {"users": "shoppers", "tasks": "buy", "format": "PNG"},
        analysis_settings={"kb_version": version},
    )
    assert "<h2>Issues</h2>" in html
    assert "<h2>Coverage notes</h2>" in html
    assert "<h2>Traps Not Found</h2>" not in html
    # New confidence + severity labels surface (both on a High/Medium/Low scale); the
    # retired confidence vocabulary must not appear.
    assert ">High<" in html and ">Medium<" in html
    assert "Confirmed" not in html and "Probable" not in html and "Flagged" not in html
    # G4 coverage labels surface with their detail.
    assert "Not assessable from this artifact" in html
    assert "Not assessable without user context" in html


def test_new_kb_worth_a_closer_look_section():
    html = format_report_as_html(
        _new_kb_report(), {"users": "kids", "tasks": "find kids shows", "format": "PNG"},
        analysis_settings={"kb_version": "v2"},
    )
    # Its own section, rendering the richer fields — not folded into Issues.
    assert "<h2>Worth a closer look</h2>" in html
    assert "Open the TV shows dropdown." in html
    assert "one click" in html
    assert "If confirmed:" in html and "If ruled out:" in html
    # The potential item renders AFTER the Issues section, not among the issue cards.
    assert html.index("FORCED SYNTAX") > html.index("POOR AESTHETIC")


def test_new_kb_scorecard_and_severity_order():
    html = format_report_as_html(
        _new_kb_report(), {"users": "kids", "tasks": "find kids shows", "format": "PNG"},
        analysis_settings={"kb_version": "v2"},
    )
    # Ladder scorecard (High/Medium/Low), not the rejected Critical or Moderate/Minor vocab.
    assert "Issues by severity" in html
    assert ">High<" in html and ">Low<" in html
    assert ">Critical<" not in html
    assert "Moderate Severity" not in html and "Minor Severity" not in html
    # Issues ordered by the severity ladder: High → Medium → Low.
    order = [html.index(t) for t in ("INVITING DEAD END", "MEMORY CHALLENGE", "POOR AESTHETIC")]
    assert order == sorted(order)


def test_legacy_report_renders_legacy_sections():
    html = format_report_as_html(
        _legacy_report(), {"users": "a", "tasks": "b", "format": "c"},
        analysis_settings={"kb_version": "v1"},
    )
    assert "<h2>Traps Found</h2>" in html
    assert "<h2>Traps Not Found</h2>" in html
    assert "<h2>Coverage notes</h2>" not in html
    assert "<h2>Issues</h2>" not in html
