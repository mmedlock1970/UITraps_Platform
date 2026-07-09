"""
Emergent Patterns (KB G8 / Ledger 22) — render-time DERIVATION over the retained issue_groups
substrate + fired findings' Tenets. No model call. Failure-side, observation register, descriptive
only. Two independent axes (both may fire); neither → one-line most-consequential fallback.

Three fixtures lock the behavior most likely to be wrong — the gate:
  • trap-fest      → BOTH axes fire
  • thin           → NEITHER fires → one-liner
  • near-threshold → axis (b) correctly DECLINES a marginal plurality (margin < +2 AND top < 50%)
"""
import re

import pytest

from src.formatters import format_bytrap_report_as_html, _emergent_patterns_html

_SET = {"kb_version": "v2.1", "report_style": "trap"}


def _f(trap, tenet, sev_arr, headline):
    return {"trap_name": trap, "tenet": tenet, "headline": headline, "problem": "p",
            "recommendation": "r", "severity_label": {"critical": "High",
            "moderate": "Medium", "minor": "Low"}[sev_arr], "confidence": "High"}


# ── fixture 1: trap-fest — dual-nav region binds 3 Traps; findings cluster on Habituating ──
def _trapfest():
    return {
        "summary_headline": "h", "summary_narrative": "n",
        "critical_issues": [
            _f("POOR GROUPING", "HABITUATING", "critical",
               "Two navigation bars split site navigation into competing sets"),
            _f("UNCOMPREHENDED ELEMENT", "UNDERSTANDABLE", "critical",
               "An unlabeled toolbar icon gives no hint of its function"),
        ],
        "moderate_issues": [
            _f("AMBIGUOUS HOME", "HABITUATING", "moderate",
               "Two different home affordances compete for 'where am I'"),
            _f("GRATUITOUS REDUNDANCY", "HABITUATING", "moderate",
               "The same links appear twice across the stacked bars"),
        ],
        "minor_issues": [
            _f("INCONSISTENT APPEARANCE", "HABITUATING", "minor",
               "One control is styled two different ways"),
        ],
        "traps_checked_not_found": [], "positive_observations": [],
        "issue_groups": [
            {"location": "the two stacked navigation bars", "traps": [
                {"trap_name": "POOR GROUPING", "relationship": "root_cause"},
                {"trap_name": "AMBIGUOUS HOME", "relationship": "consequence"},
                {"trap_name": "GRATUITOUS REDUNDANCY", "relationship": "co_occurring"},
            ]},
        ],
    }


# ── fixture 2: thin — two isolated findings, different regions, different tenets ──
def _thin():
    return {
        "summary_headline": "h", "summary_narrative": "n",
        "critical_issues": [
            _f("UNCOMPREHENDED ELEMENT", "UNDERSTANDABLE", "critical",
               "An unlabeled toolbar icon gives first-time users no way to tell what it does"),
        ],
        "moderate_issues": [], "minor_issues": [
            _f("DISTRACTION", "EFFICIENT", "minor",
               "An autoplaying hero pulls focus from the primary task"),
        ],
        "traps_checked_not_found": [], "positive_observations": [], "issue_groups": [],
    }


# ── fixture 3: near-threshold — Habituating 3, Understandable 2, + 2 lone tenets (total 7) ──
# top = 3/7 = 43% (< 50%), margin 3 vs 2 = +1 (< +2), no region binds ≥2 → axis (b) must DECLINE.
def _near():
    return {
        "summary_headline": "h", "summary_narrative": "n",
        "critical_issues": [
            _f("POOR GROUPING", "HABITUATING", "critical",
               "Primary actions are scattered across three unrelated zones"),
            _f("AMBIGUOUS HOME", "HABITUATING", "critical",
               "Two elements both look like the way back home"),
            _f("UNCOMPREHENDED ELEMENT", "UNDERSTANDABLE", "critical",
               "A gear icon with no label hides the only settings entry"),
        ],
        "moderate_issues": [
            _f("INCONSISTENT APPEARANCE", "HABITUATING", "moderate",
               "The same button appears in two different styles"),
            _f("FORCED SYNTAX", "UNDERSTANDABLE", "moderate",
               "The date field rejects everything but one hidden format"),
            _f("DISTRACTION", "EFFICIENT", "moderate",
               "An autoplaying trailer competes with the sign-in form"),
        ],
        "minor_issues": [
            _f("UNATTRACTIVE APPEARANCE", "BEAUTIFUL", "minor",
               "Mismatched fonts undercut the premium framing"),
        ],
        "traps_checked_not_found": [], "positive_observations": [],
        "issue_groups": [  # each region binds only ONE trap → axis (a) cannot fire
            {"location": "the header", "traps": [{"trap_name": "POOR GROUPING", "relationship": "root_cause"}]},
        ],
    }


def _ep_section(report):
    # EP prose is folded into the Summary above the scorecard as bare <p class='narrative ep-line'>
    # paragraphs — no subtitle. Isolate those to assert on the derived lines.
    html = format_bytrap_report_as_html(report, {"design_name": "T"}, _SET)
    seg = " ".join(re.findall(r"<p class='narrative ep-line'>(.*?)</p>", html))
    return html, seg


# ── trap-fest: BOTH axes ──
def test_trapfest_axis_a_regional_root_cause():
    _, seg = _ep_section(_trapfest())
    assert ("Three Traps concentrate on the two stacked navigation bars; the adjudication finds "
            "one is the root cause of the others, so that region is a single locus of risk "
            "despite surfacing as several Traps below.") in seg


def test_trapfest_axis_b_tenet_habituating_verbatim_cashout():
    _, seg = _ep_section(_trapfest())
    assert ("Most of what's wrong here makes the interface less Habituating — hard to predict and "
            "master because things behave and appear inconsistently — because") in seg
    # 4 Habituating findings → first three named + "among others"
    assert "among others." in seg
    assert "Two navigation bars split site navigation" in seg  # headline verbatim, not lowercased


def test_emergent_gloss_is_read_from_kb_verbatim():
    # DRIFT-GUARD: the gloss the render prints must equal the gloss parsed from the KB AND appear
    # verbatim in trap_kb_v2.1.md — proving the tool reads the KB (Ledger 23), holds no hardcoded
    # copy. If a tool-side copy is ever reintroduced and diverges from the KB, this fails.
    from pathlib import Path
    from src.knowledge_extractor import load_tenet_glosses
    kb_text = (Path(__file__).resolve().parents[1] / "data" / "trap_kb_v2.1.md").read_text(encoding="utf-8")
    _, seg = _ep_section(_trapfest())  # fires axis (b) "less Habituating"
    m = re.search(r"less Habituating — (.+?) — because", seg)
    assert m, "no Habituating gloss in the rendered Emergent Patterns line"
    rendered_gloss = m.group(1)
    assert rendered_gloss == load_tenet_glosses("v2.1")["HABITUATING"], "render != KB-parsed gloss"
    assert rendered_gloss in kb_text, "rendered gloss not present verbatim in trap_kb_v2.1.md (drift!)"


def test_gloss_loader_matches_fenced_block_exactly_eight():
    # DRIFT-GUARD: independently parse the TENET-GLOSSES fenced block from the KB file and confirm
    # the loader matches it exactly and yields all eight (Ledger 24 contract). Parse ONLY within the
    # fences so the Ledger 23 prose that quotes glosses is not matched.
    from pathlib import Path
    from src.knowledge_extractor import load_tenet_glosses
    kb_lines = (Path(__file__).resolve().parents[1] / "data" / "trap_kb_v2.1.md").read_text(encoding="utf-8").splitlines()
    si = next(i for i, l in enumerate(kb_lines) if l.strip() == "<!-- TENET-GLOSSES:START -->")
    ei = next(i for i in range(si + 1, len(kb_lines)) if kb_lines[i].strip() == "<!-- TENET-GLOSSES:END -->")
    block = "\n".join(kb_lines[si + 1:ei])
    parsed = {k.upper(): v for k, v in re.findall(r'-\s*less\s+([A-Za-z]+)\s*:\s*"([^"]+)"', block)}
    assert len(parsed) == 8, f"expected 8 glosses in the fenced block, parsed {len(parsed)}"
    assert load_tenet_glosses("v2.1") == parsed, "loader drifted from the TENET-GLOSSES fenced block"


def test_trapfest_no_imperative_no_positive():
    _, seg = _ep_section(_trapfest())
    for banned in ("should", "simplify", "consider ", "recommend", "well done", "works well"):
        assert banned.lower() not in seg.lower(), f"register violation: {banned!r}"


# ── thin: NEITHER axis → one-liner ──
def test_thin_falls_back_to_single_most_consequential():
    _, seg = _ep_section(_thin())
    assert ("The single most consequential issue: An unlabeled toolbar icon gives first-time "
            "users no way to tell what it does") in seg
    assert "concentrate on" not in seg          # axis (a) did not fire
    assert "Most of what's wrong here" not in seg  # axis (b) did not fire


# ── near-threshold: axis (b) DECLINES a marginal plurality ──
def test_near_threshold_axis_b_declines():
    _, seg = _ep_section(_near())
    assert "Most of what's wrong here" not in seg, "axis (b) fired on a marginal plurality"
    assert "concentrate on" not in seg, "axis (a) fired without a ≥2-trap region"
    # neither axis → one-liner fallback (highest severity is a critical)
    assert "The single most consequential issue:" in seg


# ── omitted entirely when there are no findings ──
def test_no_findings_omits_section():
    empty = {"summary_headline": "h", "summary_narrative": "n", "critical_issues": [],
             "moderate_issues": [], "minor_issues": [], "traps_checked_not_found": [],
             "positive_observations": [], "issue_groups": []}
    assert _emergent_patterns_html(empty, []) == []
    html = format_bytrap_report_as_html(empty, {"design_name": "T"}, _SET)
    assert "ep-line" not in html


# ── direct-unit gate checks (independent of full render) ──
def test_axis_b_fires_on_clear_majority():
    # 3 Habituating of 4 total (75% ≥ 50%) → fires even at +2-short margin (3 vs 1).
    rep = {"critical_issues": [_f("POOR GROUPING", "HABITUATING", "critical", "a"),
                               _f("AMBIGUOUS HOME", "HABITUATING", "critical", "b"),
                               _f("INCONSISTENT APPEARANCE", "HABITUATING", "critical", "c"),
                               _f("UNCOMPREHENDED ELEMENT", "UNDERSTANDABLE", "critical", "d")],
           "moderate_issues": [], "minor_issues": [], "issue_groups": []}
    out = " ".join(_emergent_patterns_html(rep, rep["critical_issues"]))
    assert "less Habituating" in out


@pytest.mark.parametrize("kbv", ["v1", "v1.1"])
def test_v1_suppresses_emergent_patterns_entirely(kbv):
    # Ledger 22 is v2.1-only material (fixed tenet glosses + concentration thresholds). A v1 run —
    # the clean control — renders NO Emergent Patterns section in ANY form (not empty, not a stub).
    rep = _trapfest()  # would fire both axes under v2.1
    html = format_bytrap_report_as_html(rep, {"design_name": "T"}, {"kb_version": kbv, "report_style": "trap"})
    assert "ep-line" not in html
    assert "concentrate on" not in html and "Most of what's wrong here" not in html
    assert "The single most consequential issue:" not in html


def test_v21_still_renders_emergent_patterns():
    rep = _trapfest()
    html = format_bytrap_report_as_html(rep, {"design_name": "T"}, {"kb_version": "v2.1", "report_style": "trap"})
    assert "ep-line" in html


def _cov(trap, tenet, status="not_assessable_artifact"):
    return {"trap_name": trap, "tenet": tenet, "coverage_status": status, "detail": "x"}


def test_stricter_drops_mostly_unassessable_tenet():
    # Protective fired twice but 3 of its Traps couldn't be evaluated (3 > 2) → mostly
    # un-inspectable → dropped from the tally. Without the drop it would fire "less Protective";
    # with it, only Habituating (1) remains → below ≥2 → axis (b) declines to the one-liner.
    rep = {"summary_headline": "h", "summary_narrative": "n",
           "critical_issues": [_f("BAD PREDICTION", "PROTECTIVE", "critical", "Prot problem one"),
                               _f("INVITING DEAD END", "PROTECTIVE", "critical", "Prot problem two"),
                               _f("POOR GROUPING", "HABITUATING", "critical", "Hab problem")],
           "moderate_issues": [], "minor_issues": [], "positive_observations": [], "issue_groups": [],
           "traps_checked_not_found": [_cov("A", "PROTECTIVE"), _cov("B", "PROTECTIVE"),
                                       _cov("C", "PROTECTIVE", "not_assessable_context")]}
    _, seg = _ep_section(rep)
    assert "less Protective" not in seg, "mostly-un-inspectable Tenet must not be named"
    assert "Most of what's wrong here" not in seg
    assert "The single most consequential issue:" in seg


def test_leash_counts_distinct_traps_not_instances():
    # One trap firing 3× is ONE distinct fired trap. With 2 of its Tenet's traps un-inspectable, the
    # Tenet is mostly un-inspectable (1 distinct fired < 2 un-inspectable) → must be DROPPED. Counting
    # fired INSTANCES (3) would defeat the leash (3 > 2) and fire the false concentration claim the
    # guard exists to suppress. (Regression for the instance-vs-distinct unit bug.)
    rep = {"summary_headline": "h", "summary_narrative": "n", "issue_groups": [],
           "moderate_issues": [], "minor_issues": [], "positive_observations": [],
           "critical_issues": [
               _f("IRREVERSIBLE ACTION", "PROTECTIVE", "critical", "delete has no undo"),
               _f("IRREVERSIBLE ACTION", "PROTECTIVE", "critical", "bulk purge is instant"),
               _f("IRREVERSIBLE ACTION", "PROTECTIVE", "critical", "reset wipes settings"),
               _f("POOR GROUPING", "HABITUATING", "critical", "actions are scattered"),
           ],
           "traps_checked_not_found": [_cov("UNWANTED DISCLOSURE", "PROTECTIVE"),
                                       _cov("DATA LOSS", "PROTECTIVE")]}
    _, seg = _ep_section(rep)
    assert "less Protective" not in seg, "leash must drop a Tenet with 1 distinct fired trap vs 2 un-inspectable"
    assert "Most of what's wrong here" not in seg  # PROTECTIVE dropped; HABITUATING has 1 distinct → no fire


def test_fire_gate_needs_two_distinct_traps_not_one_firing_twice():
    # One trap firing twice is a single trap type → ≥2 fire gate must NOT trip on it.
    rep = {"summary_headline": "h", "summary_narrative": "n", "issue_groups": [],
           "moderate_issues": [], "minor_issues": [], "positive_observations": [],
           "traps_checked_not_found": [],
           "critical_issues": [
               _f("DISTRACTION", "UNDERSTANDABLE", "critical", "hero autoplays"),
               _f("DISTRACTION", "UNDERSTANDABLE", "critical", "banner also autoplays"),
           ]}
    _, seg = _ep_section(rep)
    assert "Most of what's wrong here" not in seg  # 1 distinct trap → below the ≥2 gate → no fire


def test_fired_tenet_survives_when_mostly_inspectable():
    # Same 2 Protective findings, but only ONE couldn't-evaluate (1 < 2) → NOT dropped → fires.
    rep = {"summary_headline": "h", "summary_narrative": "n",
           "critical_issues": [_f("BAD PREDICTION", "PROTECTIVE", "critical", "Prot problem one"),
                               _f("INVITING DEAD END", "PROTECTIVE", "critical", "Prot problem two"),
                               _f("POOR GROUPING", "HABITUATING", "critical", "Hab problem")],
           "moderate_issues": [], "minor_issues": [], "positive_observations": [], "issue_groups": [],
           "traps_checked_not_found": [_cov("A", "PROTECTIVE")]}  # 1 couldn't-evaluate < 2 fired
    _, seg = _ep_section(rep)
    assert "less Protective" in seg


def test_assessed_absent_does_not_count_against_a_tenet():
    # not_present = the Trap was inspected and genuinely absent → successful inspection, must NOT
    # count as "couldn't evaluate". 2 Protective fired + 3 not_present → still fires.
    rep = {"summary_headline": "h", "summary_narrative": "n",
           "critical_issues": [_f("BAD PREDICTION", "PROTECTIVE", "critical", "Prot problem one"),
                               _f("INVITING DEAD END", "PROTECTIVE", "critical", "Prot problem two"),
                               _f("POOR GROUPING", "HABITUATING", "critical", "Hab problem")],
           "moderate_issues": [], "minor_issues": [], "positive_observations": [], "issue_groups": [],
           "traps_checked_not_found": [_cov("A", "PROTECTIVE", "not_present"),
                                       _cov("B", "PROTECTIVE", "not_present"),
                                       _cov("C", "PROTECTIVE", "not_present")]}
    _, seg = _ep_section(rep)
    assert "less Protective" in seg


def test_axis_b_tie_does_not_fire():
    rep = {"critical_issues": [_f("POOR GROUPING", "HABITUATING", "critical", "a"),
                               _f("AMBIGUOUS HOME", "HABITUATING", "critical", "b"),
                               _f("UNCOMPREHENDED ELEMENT", "UNDERSTANDABLE", "critical", "c"),
                               _f("FORCED SYNTAX", "UNDERSTANDABLE", "critical", "d")],
           "moderate_issues": [], "minor_issues": [], "issue_groups": []}
    out = " ".join(_emergent_patterns_html(rep, rep["critical_issues"]))
    assert "Most of what's wrong here" not in out  # 2–2 tie → no fire
