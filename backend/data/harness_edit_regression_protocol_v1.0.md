# HARNESS-EDIT REGRESSION CHECK — Standing Protocol (v1.0)

**Purpose.** Any edit to Claude Code's harness/tool prompt — adding, deleting, or rewording text — can change model behavior independent of whether the same logic exists elsewhere (e.g., in the KB). This is a lightweight, repeatable check to catch that, without invoking the full comparison-research protocol (frozen cells, B/D/F, etc.). It applies to all future v2.x tool work, not just this one edit.

**Trigger.** Run this whenever Claude Code's harness/tool prompt text changes in any way — additions, deletions, rewording, reordering — regardless of whether the KB content is also changing in the same pass.

**Not this.** This is not a re-scoring of overall tool quality, not a fixture-tuning exercise, and not a substitute for the freeze/epoch machinery. It targets only the specific mechanism(s) the edit touched.

## Protocol

1. **Name the mechanism.** Before editing, state in one line what behavior the edit is expected to affect (e.g., "removing the harness's promotion-path instruction — expect no change, since KB's Severity & Confidence section already states it").
2. **Run the same fixture twice** — once on the pre-edit harness, once on the post-edit harness. Same KB sha, same context inputs, same artifact. Use whatever fixture is already on hand (fresh-screenshot or otherwise); no new fixture is required for this check alone.
3. **Compare only the targeted mechanism**, not the full report:
   - If the edit removed/added *promotion-path* language → check every non-High-confidence finding still names a specific check and cost.
   - If the edit removed/added *mutual-exclusivity* language → check no trap appears in both an issue and coverage notes.
   - If the edit removed/added *Worth-a-closer-look gating* language → check entries still pass all three gates (pivotal, ≥Medium worst case, named check) rather than drifting into either Issues or silent drops.
   - If the edit touched *hedging/voice* language → check whether High-confidence findings read distinguishably plainer than Low-confidence ones, or whether all findings read uniformly hedged.
   - If the edit touched *content-type/platform* text → check whether the same categories of issues get raised on a fixture from a different content-type/platform, to confirm nothing content-type-specific was silently load-bearing.
4. **Verdict, one line:** "Held" (mechanism unchanged) / "Drifted" (describe exactly what changed) / "Inconclusive" (fixture didn't exercise the mechanism — note what fixture would).
5. **Log it.** One line in the Open Items ledger per edit: what changed, the verdict, and the run/kb_hash pair used. This is process history, not a frozen artifact — it accumulates, it doesn't get versioned itself.

## Scope note

This protocol checks *whether an edit changed behavior*, not *whether the behavior is correct*. A "Held" verdict means the edit was safe to make as intended; it does not mean the underlying rule is well-calibrated — that's a KB-content question, handled through the normal ratify-then-apply rulings, not this check.
