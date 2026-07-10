"""
Disposition gate (G4 three-state rule, Ledger 26).

A Trap may render "Not present / Did not find" ONLY when BOTH hold:
  (a) it is observable in the submitted artifact class — the artifact sits at or above the Trap's
      KB-owned observability floor (ASSESSABILITY-DIGEST), AND
  (b) it carries named G6 disconfirming evidence (the coverage `detail`).
Missing either, the tool cannot honestly report absence and re-routes the verdict to "Couldn't
evaluate." The gate runs at render time in _format_new_kb_bytrap_html for the coached v2 report only —
self-serve (the raw-KB condition) is left ungated, and v1 / v1.1 carry no digest.

Fixture anchor: WANDERING ELEMENT floors at disconnected-screens; BAD PREDICTION and GRATUITOUS
REDUNDANCY floor at static-screenshot — the PV-Web verification cases.
"""
import pytest

from src.formatters import format_bytrap_report_as_html, _apply_disposition_gate


def _render(report, *, artifact_class="static-screenshot", profile="default", kb_version="v2"):
    return format_bytrap_report_as_html(
        report,
        {"design_name": "Test"},
        {"kb_version": kb_version, "report_style": "trap",
         "artifact_class": artifact_class, "profile": profile},
    )


def _cov(trap, status="not_present", detail="an absent instance is not visible here"):
    return {"trap_name": trap, "coverage_status": status, "detail": detail}


def _report(coverage):
    return {
        "summary_headline": "h", "summary_narrative": "n",
        "critical_issues": [], "moderate_issues": [], "minor_issues": [],
        "issue_groups": [], "positive_observations": [],
        "traps_checked_not_found": coverage,
    }


def _disp_row(html, trap):
    section = html.split("Trap disposition index", 1)[1]
    return section.split(f">{trap}</span>", 1)[1].split("</tr>", 1)[0]


# ── (a) observability floor ───────────────────────────────────────────────────────────────────

def test_higher_floor_trap_on_static_screenshot_routes_to_couldnt_evaluate():
    # WANDERING ELEMENT floors at disconnected-screens; a single static screenshot cannot observe
    # it, so a "Not present" verdict is not eligible — it must read "Couldn't evaluate."
    html = _render(_report([_cov("WANDERING ELEMENT")]), artifact_class="static-screenshot")
    row = _disp_row(html, "WANDERING ELEMENT")
    assert "Couldn't evaluate" in row
    assert "Did not find" not in row


def test_higher_floor_trap_at_or_above_floor_stays_not_present():
    # Same Trap, but now the artifact IS a set of disconnected screens (>= its floor) and G6 evidence
    # is cited → the "Not present" verdict is legitimate and stands as "Did not find."
    html = _render(_report([_cov("WANDERING ELEMENT")]), artifact_class="disconnected-screens")
    row = _disp_row(html, "WANDERING ELEMENT")
    assert "Did not find" in row


def test_nonpartial_static_floor_trap_with_evidence_stays_not_present():
    # GRATUITOUS REDUNDANCY floors at static-screenshot and is NOT partial, so a single screenshot
    # with cited evidence fully clears it — it stays "Did not find" (a hard clear).
    html = _render(_report([_cov("GRATUITOUS REDUNDANCY")]), artifact_class="static-screenshot")
    assert "Did not find" in _disp_row(html, "GRATUITOUS REDUNDANCY")


# ── (b) named G6 evidence ─────────────────────────────────────────────────────────────────────

def test_not_present_without_evidence_routes_to_couldnt_evaluate():
    # GRATUITOUS REDUNDANCY is observable on a static screenshot, but with NO cited evidence the
    # clear is unjustified — the gate re-routes it to "Couldn't evaluate."
    html = _render(_report([_cov("GRATUITOUS REDUNDANCY", detail="")]),
                   artifact_class="static-screenshot")
    row = _disp_row(html, "GRATUITOUS REDUNDANCY")
    assert "Couldn't evaluate" in row
    assert "Did not find" not in row


# ── remedy phrasing ───────────────────────────────────────────────────────────────────────────

def test_class_gap_remedy_named_in_coverage_notes():
    # A gated-for-class Trap explains the settling artifact, computed from the class gap.
    html = _render(_report([_cov("WANDERING ELEMENT")]), artifact_class="static-screenshot")
    coverage = html.split("Coverage notes", 1)[1].split("Trap disposition index", 1)[0]
    assert "needs a second screen" in coverage


# ── scope: self-serve and lineage ─────────────────────────────────────────────────────────────

def test_self_serve_is_left_ungated():
    # Self-serve is the raw-KB condition that tests whether the model applies G4 unaided; the tool
    # must NOT enforce the gate there. WANDERING ELEMENT on a static screenshot stays "Did not find."
    html = _render(_report([_cov("WANDERING ELEMENT")]),
                   artifact_class="static-screenshot", profile="self-serve")
    assert "Did not find" in _disp_row(html, "WANDERING ELEMENT")


def test_unknown_artifact_class_defaults_to_most_restrictive():
    # An absent/garbage class must fall to static-screenshot (rank 0), never silently pass a
    # higher-floor Trap. WANDERING ELEMENT → "Couldn't evaluate."
    html = _render(_report([_cov("WANDERING ELEMENT")]), artifact_class="nonsense")
    assert "Couldn't evaluate" in _disp_row(html, "WANDERING ELEMENT")


# ── higher rungs of the scale ─────────────────────────────────────────────────────────────────

def test_flow_floor_trap_observable_on_flow_artifact():
    # FEEDBACK FAILURE floors at `flow`; on a flow artifact with cited evidence it can be cleared.
    html = _render(_report([_cov("FEEDBACK FAILURE")]), artifact_class="flow")
    assert "Did not find" in _disp_row(html, "FEEDBACK FAILURE")


def test_live_floor_trap_still_gated_on_flow_artifact():
    # ACCIDENTAL ACTIVATION floors at `live`; a `flow` artifact is below that floor, so even with
    # evidence the "Not present" verdict is not eligible → "Couldn't evaluate."
    html = _render(_report([_cov("ACCIDENTAL ACTIVATION")]), artifact_class="flow")
    row = _disp_row(html, "ACCIDENTAL ACTIVATION")
    assert "Couldn't evaluate" in row and "Did not find" not in row


# ── remedy text: observable-but-unjustified ───────────────────────────────────────────────────

def test_no_evidence_remedy_text_in_coverage_notes():
    # GRATUITOUS REDUNDANCY is observable on a static screenshot; with no cited evidence it is gated,
    # and the coverage note explains it was not ruled out (distinct from a class-gap remedy).
    html = _render(_report([_cov("GRATUITOUS REDUNDANCY", detail="")]), artifact_class="static-screenshot")
    coverage = html.split("Coverage notes", 1)[1].split("Trap disposition index", 1)[0]
    assert "no disconfirming evidence was cited to rule it out" in coverage


# ── the gate only ever touches `not_present` ──────────────────────────────────────────────────

def test_partially_assessed_is_left_untouched():
    # A partially_assessed entry co-exists per J27 and is NOT a "Not present" verdict — the gate must
    # leave its status alone regardless of floor/artifact class.
    rep = _report([_cov("WANDERING ELEMENT", status="partially_assessed")])
    _apply_disposition_gate(rep, {"kb_version": "v2", "artifact_class": "static-screenshot"})
    assert rep["traps_checked_not_found"][0]["coverage_status"] == "partially_assessed"


def test_gate_is_idempotent():
    # Running the gate twice (source + render copy) must not double-mutate or crash.
    rep = _report([_cov("WANDERING ELEMENT")])
    s = {"kb_version": "v2", "artifact_class": "static-screenshot"}
    _apply_disposition_gate(rep, s)
    first = rep["traps_checked_not_found"][0]["coverage_status"]
    _apply_disposition_gate(rep, s)
    assert rep["traps_checked_not_found"][0]["coverage_status"] == first == "not_assessable_artifact"


# ── lineage scope: only v2 carries a digest ───────────────────────────────────────────────────

@pytest.mark.parametrize("ver", ["v1", "v1.1"])
def test_non_v2_lineage_is_ungated(ver):
    # v1 / v1.1 carry no ASSESSABILITY-DIGEST; the gate must skip them entirely (never load a digest,
    # never re-route), leaving the model's verdict as-is.
    rep = _report([_cov("WANDERING ELEMENT")])
    _apply_disposition_gate(rep, {"kb_version": ver, "artifact_class": "static-screenshot"})
    assert rep["traps_checked_not_found"][0]["coverage_status"] == "not_present"


# ── Option-3 scoped clearance: partial Trap at its floor (Ledger 27) ──────────────────────────

def test_partial_trap_at_floor_renders_scoped_clearance_never_bare_not_present():
    # INCONSISTENT APPEARANCE is static-screenshot PARTIAL: on a single screenshot it may clear only
    # its same-screen sub-scope, NEVER a wholesale "Not present." The gate re-routes not_present →
    # partially_assessed and renders the KB scoped-coverage string; the disposition reads "Partially
    # evaluated," and the cross-context out-of-scope dimension is named verbatim from the KB.
    html = _render(_report([_cov("INCONSISTENT APPEARANCE")]), artifact_class="static-screenshot")
    row = _disp_row(html, "INCONSISTENT APPEARANCE")
    assert "Partially evaluated" in row
    assert "Did not find" not in row
    coverage = html.split("Coverage notes", 1)[1].split("Trap disposition index", 1)[0]
    assert "not from this artifact: cross-screen/cross-context form consistency" in coverage


def test_partial_scoped_detail_is_pulled_verbatim_from_kb_not_synthesized():
    from src.knowledge_extractor import load_scoped_coverage
    rep = _report([_cov("BAD PREDICTION")])
    _apply_disposition_gate(rep, {"kb_version": "v2", "artifact_class": "static-screenshot"})
    e = rep["traps_checked_not_found"][0]
    assert e["coverage_status"] == "partially_assessed"          # never bare not_present
    # The rendered detail is a verbatim slice of the KB scoped string (leading "Bad Prediction — "
    # stripped as mechanical de-dup of the pill) — the tool never invents scope language.
    assert e["detail"] and e["detail"] in load_scoped_coverage("v2")["BAD PREDICTION"]
    assert "prediction accuracy" in e["detail"]                  # the out-of-scope dimension, verbatim


def test_partial_trap_above_floor_hard_clears_with_evidence():
    # A partial Trap ABOVE its floor sees the fuller scope, so with cited evidence it hard-clears like
    # a non-partial (INCONSISTENT APPEARANCE on disconnected-screens → cross-context is now observable).
    html = _render(_report([_cov("INCONSISTENT APPEARANCE")]), artifact_class="disconnected-screens")
    assert "Did not find" in _disp_row(html, "INCONSISTENT APPEARANCE")


# ── fail-loud: a corrupt scoped-coverage line must raise, never silently drop ──────────────────

def test_scoped_coverage_fails_loud_on_corrupt_line(monkeypatch):
    import src.knowledge_extractor as ke
    ke._scoped_coverage_cache.clear()
    orig = ke.load_analysis_reference
    def _fake(v="v2"):
        # strip the opening quote from one scoped line → it no longer matches `- <TRAP>: "<string>"`
        return orig(v).replace('- BAD PREDICTION: "Bad Prediction', '- BAD PREDICTION: Bad Prediction')
    monkeypatch.setattr(ke, "load_analysis_reference", _fake)
    try:
        with pytest.raises(ValueError):
            ke.load_scoped_coverage("v2")
    finally:
        ke._scoped_coverage_cache.clear()
