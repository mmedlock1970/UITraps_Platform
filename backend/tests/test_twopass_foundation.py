"""
Phase 2a foundation: staleness guard, loaders, and tolerant candidate matching.

These cover the deterministic parts of twopass mode — no API calls. The guard must
regenerate packs when the master hash moves (the "sha256 makes the swap automatic"
contract); the matcher must recover trap names from messy pass-1 output without
silently dropping anything.
"""
import json

import pytest

from src import pack_generator as pg


VERSIONS = ["v2.1"]  # v1.1 retired from the active test matrix (pack support retained)


@pytest.mark.parametrize("version", VERSIONS)
def test_ensure_current_regenerates_and_stamps_live_hash(version):
    """After ensure_current, the manifest hash equals the live master hash."""
    manifest = pg.ensure_current(version)
    assert manifest["master_sha256"] == pg.master_hash(version)
    # Idempotent: a second call is a no-op (hash already matches) and returns the same hash.
    again = pg.ensure_current(version)
    assert again["master_sha256"] == manifest["master_sha256"]


@pytest.mark.parametrize("version", VERSIONS)
def test_ensure_current_refuses_when_regeneration_disabled_and_stale(version, monkeypatch):
    """With regenerate=False and a moved master hash, the guard refuses rather than run stale."""
    pg.ensure_current(version)  # make packs current first
    monkeypatch.setattr(pg, "master_hash", lambda v: "deadbeef" * 8)
    with pytest.raises(RuntimeError, match="stale"):
        pg.ensure_current(version, regenerate=False)


@pytest.mark.parametrize("version", VERSIONS)
def test_manifest_trap_count(version):
    manifest = pg.ensure_current(version)
    expected = 27  # v2.1 taxonomy
    assert len(manifest["traps"]) == expected
    assert len(manifest["verbatim_definitions"]) == expected


def test_match_candidates_clean_pipe_lines():
    manifest = pg.ensure_current("v2.1")
    names = [t["trap"] for t in manifest["traps"]]
    a, b = names[0], names[5]
    raw = f"{a} | login screen | submit btn | disabled\n{b} | cart | qty field | silent cap"
    matched, unmatched = pg.match_candidates(raw, manifest)
    assert matched == [a, b] or set(matched) == {a, b}
    assert unmatched == []


def test_match_candidates_tolerates_markdown_and_dedupes():
    manifest = pg.ensure_current("v2.1")
    name = manifest["traps"][0]["trap"]
    raw = (
        f"- **{name}** | home | hero | x\n"
        f"1. {name.upper()} | home | hero | x (duplicate)\n"
        "| Trap | Screen |\n"          # table header noise -> unmatched
        "random prose with no trap\n"  # -> unmatched
    )
    matched, unmatched = pg.match_candidates(raw, manifest)
    assert matched == [name]          # case-insensitive + deduped
    assert len(unmatched) == 2        # header row + prose surfaced, not dropped


def test_match_candidates_longest_name_wins():
    """A candidate naming a longer trap must not be captured by a shorter contained name."""
    manifest = pg.ensure_current("v2.1")
    names = [t["trap"] for t in manifest["traps"]]
    # Find any pair where one normalized name contains another.
    norm = {n: pg._norm_letters(n) for n in names}
    pair = None
    for long in names:
        for short in names:
            if long != short and norm[short] and norm[short] in norm[long]:
                pair = (long, short)
                break
        if pair:
            break
    if not pair:
        pytest.skip("no nested trap names in this manifest")
    long, short = pair
    # Candidate line with extra words so exact-match fails and the fallback runs.
    raw = f"TRAP: {long} (sole path) | screen | el | cond"
    matched, _ = pg.match_candidates(raw, manifest)
    assert long in matched
    assert short not in matched


def test_load_chunks_returns_full_chunk_bodies():
    manifest = pg.ensure_current("v2.1")
    first_two = [t["trap"] for t in manifest["traps"][:2]]
    text = pg.load_chunks("v2.1", first_two, manifest=manifest)
    assert "### TRAP:" in text
    # Both requested traps present, in manifest order.
    assert text.count("### TRAP:") == 2


def test_load_packs_readable():
    pg.ensure_current("v2.1")
    p1 = pg.load_pack("v2.1", "pass1")
    p2 = pg.load_pack("v2.1", "pass2")
    assert p1.strip() and p2.strip()
    assert "GLOBAL RULES" in p2 or "GLOBAL" in p2


# ── Per-trap assessability digest (pass-2 core) ──────────────────────────────

@pytest.mark.parametrize("version", VERSIONS)
def test_assessability_digest_present_and_complete(version):
    """The pass-2 core pack carries a digest with exactly one bullet per taxonomy trap, so
    coverage for non-candidate traps (whose chunks never load) is written informed."""
    pg.ensure_current(version)
    p2 = pg.load_pack(version, "pass2")
    assert "## PER-TRAP ASSESSABILITY DIGEST" in p2
    digest = p2.split("## PER-TRAP ASSESSABILITY DIGEST", 1)[1]
    manifest = pg.load_manifest(version)
    # One bullet per trap, each naming that trap.
    assert digest.count("\n- **") == len(manifest["traps"])
    for t in manifest["traps"]:
        assert f"- **{t['trap']}** —" in digest


def test_assessability_digest_is_verbatim_static_clause():
    """The digest lifts each chunk's own assessability declaration verbatim — Irreversible
    Action must carry its 'not assessable from this artifact' clause (the misfile this fixes),
    and the text must match the chunk word-for-word (no tool authoring)."""
    pg.ensure_current("v2.1")
    p2 = pg.load_pack("v2.1", "pass2")
    digest = p2.split("## PER-TRAP ASSESSABILITY DIGEST", 1)[1]
    line = next(ln for ln in digest.splitlines() if ln.startswith("- **Irreversible Action**"))
    assert "not assessable from this artifact" in line.lower()
    # Verbatim check: the collapsed chunk block text appears in the collapsed digest line.
    chunk = pg.load_chunks("v2.1", ["Irreversible Action"])
    block = pg._assessability_block(chunk)
    body = " ".join(pg._digest_line("X", block).split("—", 1)[1].split())
    assert body and body in " ".join(line.split())


def test_assessability_block_stops_at_next_bold_label():
    """The block must end at the NEXT line-start bold label of any shape — colon-terminated
    ('**Escalators:**') or lowercase — not just an uppercase+period one, so a future chunk
    reorder can't silently swallow the following section into the digest bullet."""
    chunk = (
        "### TRAP: EXAMPLE\n"
        "**Definition.** something.\n\n"
        "**Assessability & Confidence.** Static screenshot: partly assessable — declare.\n\n"
        "**Escalators:** C4 is decisive — this must NOT be captured.\n\n"
        "**Attribution.** also not captured.\n"
    )
    block = pg._assessability_block(chunk)
    assert "Static screenshot: partly assessable" in block
    assert "Escalators" not in block and "Attribution" not in block


def test_assessability_block_ignores_prose_mention():
    """An 'assessab' mention inside another block's prose (not its label) must not trigger
    capture — only a line-start bold label containing 'assessab' does."""
    chunk = (
        "### TRAP: EXAMPLE\n"
        "**Boundary.** This is hard to assess / assessability is limited, but see below.\n\n"
        "**Assessability & Confidence.** the real block.\n"
    )
    block = pg._assessability_block(chunk)
    assert block.startswith("**Assessability & Confidence.**")
    assert "Boundary" not in block


def test_assessability_digest_handles_nonstandard_label():
    """Poor Aesthetic labels its assessability content '**Boundary & assessability warning...**',
    not '**Assessability & Confidence.**'. The structural 'assessab' match must still catch it."""
    pg.ensure_current("v2.1")
    chunk = pg.load_chunks("v2.1", ["Poor Aesthetic"])
    block = pg._assessability_block(chunk)
    assert "assessab" in block.lower()
    line = pg._digest_line("Poor Aesthetic", block)
    assert line.startswith("- **Poor Aesthetic** —")
    assert "\n" not in line  # collapsed to one line
