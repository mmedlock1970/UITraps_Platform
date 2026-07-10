"""
RELAY B — runtime version stamp + isolation/full-stack attestations on every report.

All values are runtime facts: KB sha = sha256 of the loaded KB FILE (first 8), build sha = env/git,
and the isolation / full-stack items reflect the ACTUAL config + render path. The stamp attests
INPUTS/paths (what was loaded/applied), NEVER output cleanliness (v1) or performance (v2); no
staleness verdict. A contradicting fact is stamped as-is (that's the regression signal).
"""
import hashlib
import re
from pathlib import Path

import pytest

from src.formatters import format_bytrap_report_as_html
from src.knowledge_extractor import kb_file_sha256

_DATA = Path(__file__).resolve().parents[1] / "data"


def _render(kb="v2", mode="single", profile="default", findings=True):
    crit = [{"trap_name": "BAD PREDICTION", "tenet": "", "headline": "x", "problem": "p",
             "recommendation": "r", "severity_label": "High", "confidence": "High"}] if findings else []
    rep = {"summary_headline": "h", "summary_narrative": "n", "critical_issues": crit,
           "moderate_issues": [], "minor_issues": [], "traps_checked_not_found": [],
           "positive_observations": []}
    return format_bytrap_report_as_html(
        rep, {"design_name": "T"},
        {"kb_version": kb, "report_style": "trap", "mode": mode, "profile": profile})


def _stamp(html, cls):
    m = re.search(rf"<div class='{cls}'>(.*?)</div>", html)
    return m.group(1) if m else None


def test_kb_sha_is_sha256_of_loaded_file_and_lineage_correct():
    for kb, fn in [("v2", "trap_kb_v2.md"), ("v1", "trap_kb_v1.0.md")]:
        expected = hashlib.sha256((_DATA / fn).read_bytes()).hexdigest()[:8]
        assert kb_file_sha256(kb) == expected                       # matches `sha256sum <file>`
        stamp = _stamp(_render(kb, profile=("self-serve" if kb == "v1" else "default")), "r-stamp")
        assert f"KB {kb} · {expected}" in stamp                     # version + sha stamped verbatim
    # the two lineages carry DIFFERENT shas — the stamp is file-derived, not label-derived
    assert kb_file_sha256("v1") != kb_file_sha256("v2")


def test_stamp_present_and_build_sha_present_or_flagged():
    for kb, profile in [("v2", "default"), ("v1", "self-serve")]:
        s = _stamp(_render(kb, profile=profile), "r-stamp")
        assert s and s.startswith("KB ") and " · build " in s
        build = s.split("· build ", 1)[1]
        assert build == "unavailable" or re.fullmatch(r"[0-9a-f]{6,8}", build), build


def test_no_staleness_verdict():
    s = _stamp(_render("v2"), "r-stamp")
    for w in ("stale", "current", "latest", "out of date", "up to date", "expected"):
        assert w not in s.lower(), f"staleness verdict word {w!r} in stamp"


def test_v1_isolation_line_and_no_v2_or_ep_claims():
    html = _render("v1", profile="self-serve")
    att = _stamp(html, "r-attest")
    assert att.startswith("v1.0 isolated —")
    assert "v1 taxonomy" in att and "no Emergent Patterns" in att
    assert "self-serve (no v2 scaffolding)" in att
    assert "8ca6a44f" in att and "0603182a" not in att              # v1.0 sha, not the v2 sha
    assert "Emergent Patterns ✓" not in html and "ep-line" not in html
    assert "v2 full stack" not in html


def test_v1_contradiction_is_stamped_not_suppressed():
    # A v1 run that is NOT self-serve must stamp the true (contradicting) profile, not fake clean.
    att = _stamp(_render("v1", profile="default"), "r-attest")
    assert "NOT self-serve" in att


def test_v21_fullstack_reflects_actual_mode():
    two = _stamp(_render("v2", mode="twopass"), "r-attest")
    assert two.startswith("v2 full stack —")
    assert "two-pass ✓" in two and "system-prompt know-how ✓" in two and "exec-voice ✓" in two
    one = _stamp(_render("v2", mode="single"), "r-attest")
    assert "two-pass — (not applied)" in one and "two-pass ✓" not in one   # single-pass is honest


def test_v21_emergent_patterns_reflects_findings():
    assert "Emergent Patterns ✓" in _stamp(_render("v2", findings=True), "r-attest")
    assert "Emergent Patterns — (no findings)" in _stamp(_render("v2", findings=False), "r-attest")


@pytest.mark.parametrize("kb,profile", [("v1", "self-serve"), ("v2", "default")])
def test_attestation_never_overclaims(kb, profile):
    att = _stamp(_render(kb, profile=profile), "r-attest").lower()
    for w in ("leak-free", "leak free", "guarantee", "guaranteed", "optimal", "certified",
              "clean output", "maximum"):
        assert w not in att, f"overclaim {w!r} in attestation"
