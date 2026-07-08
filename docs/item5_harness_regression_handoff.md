# Item 5 — Harness-Edit Regression Check: Fixture + Per-Mechanism Checklist

Run against `backend/data/harness_edit_regression_protocol_v1.0.md`. Steve runs the API
calls; the harness edits are already applied.

## What changed (the harness deletions this pass)
Five prose blocks were deleted from the **v2.1 Prompting+KB scaffolds only**
(`_build_new_kb_system_prompt`, `_build_new_kb_issues_system_prompt`,
`_build_twopass_detection_system`, `CONTENT_TYPE_GUIDANCE`). Each was a duplicate of a
rule the **KB master now carries**. The v1.0 KB-only path (`_build_self_serve_*`) was
**not touched** — it's the control.

## Configs to run (both surviving configs, same fixture, same KB shas)
- **Primary — v2.1 Prompting+KB** (where the deleted blocks lived):
  `kb_version="v2.1"`, `profile="default"`, `mode="twopass"`. Run **both** report styles:
  `report_style="issues"` (exercises detection + issues scaffolds + description-voice) and
  `report_style="trap"` (exercises the by-trap scaffold). KB sha to pin: **v2.1 = 93b0ae78**.
- **Control — v1.0 KB-only**:
  `kb_version="v1"`, `profile="self-serve"`, `mode="single"`, `report_style="trap"`.
  Expectation: **no change** vs its own pre-edit output (its harness wasn't edited).

## Fixture — artifact
`analyses/screenshots/wayfair-homepage-2026-01-27.png` — a dense e-commerce home screen
that reliably exercises all five mechanisms (many traps present, several absent, ambiguous
statically-unconfirmable elements, a spread of High↔Low confidence). Any on-hand
fresh-screenshot fixture works; keep it identical across before/after runs.

## Fixture — context inputs (use verbatim on every run)
```json
{
  "users": "First-time shoppers browsing for home furniture, comfortable on the web but new to this site",
  "tasks": "Find and start buying a specific item (e.g., a sofa) from the home screen",
  "format": "PNG",
  "content_type": "website"
}
```
Hold these constant across the before run, the after run, and both configs. Do not change
`users`/`tasks`/`content_type` between runs — the check compares behavior, not inputs.

## Before / after
"Before" = the harness **with** the five blocks; "after" = current working tree. Because
this pass's edits are uncommitted and sit on top of earlier-session feature work, HEAD is
**not** a clean "before." If you want a literal A/B rather than a post-edit presence check,
ask and you'll get an isolated pre-edit `prompts.py` (current tree + the five blocks
re-inserted, nothing else) so the only delta is these deletions. Otherwise the decisive
signal is **post-edit presence** of each mechanism below on the v2.1 runs.

---

## Per-mechanism checklist
Compare **only** the targeted mechanism (protocol §3). One-line verdict each:
**Held** / **Drifted** (say exactly what changed) / **Inconclusive** (fixture didn't
exercise it — say what would).

| # | Mechanism (Item-5 name) | Deleted block → KB rule now carrying it | What to check on the v2.1 output | Verdict |
|---|---|---|---|---|
| 1 | **Promotion-path presence** | "confidence promotion-path" sentence + WORTH-A-CLOSER-LOOK entry ticket → **G8 + Severity & Confidence** | Every non-High-confidence finding and every `potential_issues` entry still names a **specific `check`** and a **`check_cost`**. None left bare. | |
| 2 | **Mutual-exclusivity / coverage correctness** | coverage-notes explanatory prose (per-value) → **G4 / G8 / J27** | No trap appears in **both** an issue/potential **and** `traps_checked_not_found`. Every taxonomy trap accounted for exactly once. `partially_assessed` still used where scope is split (not collapsed to not_present). | |
| 3 | **Worth-a-closer-look gating** | WORTH-A-CLOSER-LOOK entry-ticket paragraph → **G8** | Each `potential_issues` entry passes all three gates: **pivotal**, **≥Medium worst-case implication**, **named check**. Nothing pivotal drifted into Issues or got silently dropped. | |
| 4 | **Confidence-calibrated hedging** | "⚠️ MEASURED, PREDICTIVE LANGUAGE" block → new KB rule **"Confidence-calibrated prose"** | High-confidence findings read **distinguishably plainer** than Low-confidence ones — not uniformly hedged, not uniformly flat. Low-confidence prose still carries visible uncertainty. | |
| 5 | **Technical bugs withheld / reported** | draft/placeholder exception (CONTENT_TYPE + TECHNICAL BUGS clause) → new KB rule **"Technical bugs" (G8 item 4)** | A genuine technical failure lands in **`bugs_detected`**, not as a trap. Draft/placeholder/lorem content is **not** flagged as a bug or trap. | |

### Also-deleted (same "KB already carries it" rationale) — verify no behavior drop
| Deleted | KB rule | Check |
|---|---|---|
| "🔍 GROUND EVERY FINDING…" anti-hallucination block (+ detection line) | **G4 / G6** | Every finding still cites something **visible in the artifact**; no invented UI. |
| "Favor RECALL over precision / over-inclusion expected" (detection scaffold) | **G2** | Detection pass still over-includes candidates rather than pre-filtering. |
| "State any causal cascade… HERE, in prose" (By-Issue voice) | **G3** | Multi-trap issues still narrate the causal chain in the description prose. |

### Control (v1.0 KB-only)
Confirm its output is the shape it produced before this pass (flat, bare schema, no
`potential_issues`/`coverage_status`). Any change here = cross-contamination bug.

### Log (protocol §5)
One Open-Items-ledger line per verdict: what changed, verdict, run id + kb sha (v2.1 = 93b0ae78).
