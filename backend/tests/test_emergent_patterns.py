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
    assert "two navigation bars split site navigation" in seg  # lc-first of a named finding


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
