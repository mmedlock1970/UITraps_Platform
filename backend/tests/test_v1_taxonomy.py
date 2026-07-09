"""
v1 taxonomy isolation (Check-3 resolution). A v1 / v1.1 render must reflect the FROZEN v1.0 card
deck's taxonomy (KB trap_kb_v1.0.md), NOT the tool's v2.1 TENETS_AND_TRAPS table. The v1→v2.1
taxonomy change (9→8 Tenets, regroupings) was deliberate, so applying the v2.1 table to a v1 report
is leakage. These tests pin: (1) _tenet_for is version-aware on the divergent traps; (2) the render
(disposition-index pill color) follows lineage; (3) the full 26-trap v1 map matches the card deck,
so a future drift can't silently reintroduce a divergence.

Card art is SHARED by ruling — _get_card_img stays v2.1 for both lineages and is NOT tested here.
"""
from pathlib import Path

import pytest

from src.formatters import _tenet_for, _TENET_PILL, _normalize_trap_name, format_bytrap_report_as_html
from src.knowledge_extractor import load_v1_trap_tenet_map
from src.schema import VALID_TRAP_NAMES_V1

_V1_KB = Path(__file__).resolve().parents[1] / "data" / "trap_kb_v1.0.md"


def _parse_card_deck_groupings() -> dict:
    """Parse trap→Tenet groupings straight from the FROZEN v1.0 card deck (trap_kb_v1.0.md, the
    authoritative source) so the drift-guard verifies the runtime loader against the KB FILE, not a
    transcription. Section '## TENETS AND THEIR TRAPS': '+ TENET' headers, '- Trap' members."""
    lines = _V1_KB.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == "## TENETS AND THEIR TRAPS")
    mapping, cur = {}, None
    for l in lines[start + 1:]:
        s = l.strip()
        if s.startswith("## "):          # next top-level section → end of taxonomy block
            break
        if s.startswith("+ "):
            cur = s[2:].strip().upper()
        elif s.startswith("- ") and cur:
            mapping[_normalize_trap_name(s[2:].strip())] = cur
    return mapping

# The three deliberate v1→v2.1 regroupings (trap, v1 Tenet, v2.1 Tenet).
DIVERGENT = [
    ("BAD PREDICTION", "EFFICIENT", "ACCURATE"),
    ("IRREVERSIBLE ACTION", "FORGIVING", "PROTECTIVE"),
    ("UNWANTED DISCLOSURE", "DISCREET", "PROTECTIVE"),
]


@pytest.mark.parametrize("trap,v1t,v21t", DIVERGENT)
def test_tenet_for_is_version_aware(trap, v1t, v21t):
    assert _tenet_for(trap, version="v1") == v1t
    assert _tenet_for(trap, version="v1.1") == v1t
    assert _tenet_for(trap, version="v2.1") == v21t
    assert _tenet_for(trap) == v21t          # default lineage is v2.1


def _empty_report():
    return {"summary_headline": "h", "summary_narrative": "n", "critical_issues": [],
            "moderate_issues": [], "minor_issues": [], "traps_checked_not_found": [],
            "positive_observations": []}


@pytest.mark.parametrize("trap,v1t,v21t", DIVERGENT)
def test_disposition_pill_color_follows_lineage(trap, v1t, v21t):
    # The disposition index renders every canonical trap as a Tenet-colored pill. A v1 report must
    # color the divergent traps by their v1 Tenet; a v2.1 report by their v2.1 Tenet.
    v1_html = format_bytrap_report_as_html(_empty_report(), {"design_name": "T"},
                                           {"kb_version": "v1", "report_style": "trap"})
    v21_html = format_bytrap_report_as_html(_empty_report(), {"design_name": "T"},
                                            {"kb_version": "v2.1", "report_style": "trap"})
    assert f"background:{_TENET_PILL[v1t]}'>{trap}</span>" in v1_html
    assert f"background:{_TENET_PILL[v21t]}'>{trap}</span>" in v21_html
    # and NOT the other lineage's color on that trap
    assert f"background:{_TENET_PILL[v21t]}'>{trap}</span>" not in v1_html


# ── full 26-trap v1 mapping, transcribed VERBATIM from trap_kb_v1.0.md "## TENETS AND THEIR TRAPS"
# (frozen sha 8ca6a44f). This is the spot-check surface: if a future edit drifts the v1 map from the
# card deck, this fails. ──────────────────────────────────────────────────────────────────────────
def test_v1_loader_matches_card_deck_file_all_26():
    # No hand-maintained copy exists anymore: the runtime map (load_v1_trap_tenet_map, which parses
    # the KB) is cross-checked here against an INDEPENDENT parse of the same frozen card deck. If the
    # loader's parsing ever drifts from the file, this fails.
    deck = _parse_card_deck_groupings()            # independent parse of trap_kb_v1.0.md
    runtime = load_v1_trap_tenet_map()             # the loader the render actually uses
    assert len(deck) == 26, f"parsed {len(deck)} traps from the card deck, expected 26"
    assert runtime == deck, f"loader drifted from trap_kb_v1.0.md: {set(runtime.items()) ^ set(deck.items())}"


def test_v1_loader_covers_exactly_the_26_canonical_traps():
    mapped = set(load_v1_trap_tenet_map().keys())
    canon = {_normalize_trap_name(t) for t in VALID_TRAP_NAMES_V1}
    assert len(canon) == 26
    assert mapped == canon, f"missing={canon - mapped}, extra={mapped - canon}"


def test_every_v1_tenet_has_a_pill_color():
    # Every v1 Tenet (incl. the v1-only FORGIVING / DISCREET) must have a pill color, else the
    # render silently falls back to the default grey.
    for tenet in set(load_v1_trap_tenet_map().values()):
        assert tenet in _TENET_PILL, f"no pill color for v1 Tenet {tenet}"
