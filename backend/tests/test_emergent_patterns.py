"""
Priority statement (KB G8, d2bb63cb) — the opening synthesis line of the By-Trap summary.

Render-time DERIVATION, NO model call. Replaces the former Emergent-Patterns region lines and
tenet-characterization line (both removed with the per-render TENET-GLOSSES read). Names the <=3
highest-priority Traps, severity-led (High > Medium > Low) then root-cause-before-standalone among
ties, by short plain-language handle — no Trap numbers, no Tenet names, none of the forbidden
framework words. A cascade clause ("Fixing X also clears smaller issues") fires ONLY for a Trap that
is a root cause in a binding that ALSO holds a consequence Trap (a root cause with real dependents) —
never for an independent co-failure (KB line 34). Emitted whenever any Trap fired, as its own
ep-line paragraph beneath summary_narrative.
"""
import re

from src.formatters import format_bytrap_report_as_html, _emergent_patterns_html

_SET = {"kb_version": "v2", "report_style": "trap"}
# Output must never contain framework vocabulary — the forbidden words plus all eight Tenet names.
_FORBIDDEN = ("adjudication", "root cause", "region", "locus", "concentrate",
              "understandable", "habituating", "efficient", "accurate", "protective",
              "beautiful", "comfortable", "responsive")


def _f(trap, sev, handle, tenet="UNDERSTANDABLE", headline="a full descriptive headline sentence"):
    return {"trap_name": trap, "tenet": tenet, "severity_label": sev, "confidence": "High",
            "handle": handle, "headline": headline, "_src_sev": sev}


def _grp(*pairs, location="a shared area"):
    return {"location": location, "traps": [{"trap_name": t, "relationship": r} for t, r in pairs]}


def _ep(findings, groups=None):
    """Priority statement as plain text (tags stripped), via the render-time function directly."""
    rep = {"issue_groups": groups or [], "traps_checked_not_found": []}
    return " ".join(re.sub("<[^>]+>", "", l) for l in _emergent_patterns_html(rep, findings, "v2"))


# ── emit / lead / ordering ──────────────────────────────────────────────────────────────────

def test_single_trap_uses_singular_lead():
    assert _ep([_f("DISTRACTION", "High", "noisy hero")]) == "The priority here is noisy hero."


def test_multiple_traps_plural_lead_severity_ordered():
    out = _ep([_f("BAD PREDICTION", "Medium", "weak predictions"),
               _f("DISTRACTION", "High", "noisy hero"),
               _f("POOR GROUPING", "Low", "scattered nav")])
    assert out == "The priorities here, worst first, are noisy hero, weak predictions, and scattered nav."


def test_capped_at_three():
    out = _ep([_f("DISTRACTION", "High", "one"), _f("POOR GROUPING", "High", "two"),
               _f("BAD PREDICTION", "High", "three"), _f("AMBIGUOUS HOME", "High", "four")])
    named = [h for h in ("one", "two", "three", "four") if h in out]
    assert len(named) == 3 and "four" not in out


def test_always_emits_when_any_trap_fired():
    assert _ep([_f("DISTRACTION", "Low", "small thing")]).startswith("The priority here is")


def test_no_findings_emits_nothing():
    assert _ep([]) == ""


def test_distinct_traps_only_worst_severity_kept():
    # Same Trap firing twice (Low then High) counts once, at its worst severity.
    out = _ep([_f("DISTRACTION", "Low", "noisy hero"), _f("DISTRACTION", "High", "noisy hero")])
    assert out == "The priority here is noisy hero."


# ── tiebreak: root-cause before standalone at equal severity ────────────────────────────────

def test_tiebreak_root_cause_before_standalone():
    # Both High; POOR GROUPING is a root cause → ordered first though DISTRACTION was passed first.
    out = _ep([_f("DISTRACTION", "High", "noisy hero"), _f("POOR GROUPING", "High", "split nav")],
              [_grp(("POOR GROUPING", "root_cause"), ("AMBIGUOUS HOME", "consequence"))])
    assert out.index("split nav") < out.index("noisy hero")


# ── cascade clause: STRICT gate — root cause WITH a dependent consequence only ───────────────

def test_cascade_clause_fires_for_root_cause_with_consequence():
    out = _ep([_f("POOR GROUPING", "High", "split nav"), _f("AMBIGUOUS HOME", "Medium", "two homes")],
              [_grp(("POOR GROUPING", "root_cause"), ("AMBIGUOUS HOME", "consequence"))])
    assert "Fixing split nav also clears smaller issues." in out


def test_no_cascade_for_independent_co_failure():
    # POOR GROUPING is labelled root_cause, but its group holds only a co_occurring trap — NO
    # consequence. That is an independent co-failure: the cascade clause MUST NOT fire (KB line 34).
    out = _ep([_f("POOR GROUPING", "High", "split nav"), _f("DISTRACTION", "Medium", "noisy hero")],
              [_grp(("POOR GROUPING", "root_cause"), ("DISTRACTION", "co_occurring"))])
    assert "also clears smaller issues" not in out


def test_no_cascade_for_standalone_traps():
    out = _ep([_f("DISTRACTION", "High", "noisy hero"),
               _f("BAD PREDICTION", "Medium", "weak predictions")])
    assert "also clears smaller issues" not in out


def test_loose_root_cause_still_orders_but_makes_no_cascade_claim():
    # A root_cause-with-no-consequence Trap still wins the tiebreak (loose set) but gets no cascade
    # clause (strict set) — ordering and claim are decoupled.
    out = _ep([_f("DISTRACTION", "High", "noisy hero"), _f("POOR GROUPING", "High", "split nav")],
              [_grp(("POOR GROUPING", "root_cause"), ("DISTRACTION", "co_occurring"))])
    assert out.index("split nav") < out.index("noisy hero")     # ordered first (loose)
    assert "also clears smaller issues" not in out              # no claim (strict)


# ── descriptor: handle field, headline-trim crash-fallback ──────────────────────────────────

def test_descriptor_uses_handle_not_headline():
    out = _ep([_f("DISTRACTION", "High", "noisy hero", headline="A totally different long headline")])
    assert "noisy hero" in out and "different long headline" not in out


def test_descriptor_falls_back_to_trimmed_headline_when_handle_absent():
    f = _f("DISTRACTION", "High", "x", headline="Dense promotional content pushes checkout below fold")
    del f["handle"]
    out = _ep([f])
    assert "Dense promotional content pushes checkout" in out   # first 5 words
    assert "below fold" not in out


# ── forbidden vocabulary + old behavior gone ────────────────────────────────────────────────

def test_no_forbidden_words():
    out = _ep([_f("POOR GROUPING", "High", "split nav"), _f("AMBIGUOUS HOME", "Medium", "two homes")],
              [_grp(("POOR GROUPING", "root_cause"), ("AMBIGUOUS HOME", "consequence"))]).lower()
    for w in _FORBIDDEN:
        assert w not in out, f"forbidden word {w!r} leaked into the priority statement"


def test_old_region_and_tenet_lines_are_gone():
    out = _ep([_f("POOR GROUPING", "High", "split nav", tenet="HABITUATING"),
               _f("AMBIGUOUS HOME", "Medium", "two homes", tenet="HABITUATING")],
              [_grp(("POOR GROUPING", "root_cause"), ("AMBIGUOUS HOME", "consequence"))])
    assert "concentrate on" not in out
    assert "Most of what's wrong here" not in out


# ── integration: renders as its own ep-line paragraph beneath the summary ────────────────────

def test_renders_as_ep_line_paragraph():
    report = {"summary_headline": "h", "summary_narrative": "n",
              "critical_issues": [_f("DISTRACTION", "High", "noisy hero")],
              "moderate_issues": [], "minor_issues": [], "issue_groups": [],
              "traps_checked_not_found": [], "positive_observations": []}
    html = format_bytrap_report_as_html(report, {"design_name": "T"}, _SET)
    seg = " ".join(re.findall(r"<p class='narrative ep-line'>(.*?)</p>", html))
    assert "The priority here is noisy hero." in seg
