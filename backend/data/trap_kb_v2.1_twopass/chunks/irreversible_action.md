<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: IRREVERSIBLE ACTION *(draft-grade)*

**Definition.** The user cannot backtrack or undo an action they have taken — a purchase that can't cancel, a message that can't recall, a file that can't restore. The Trap applies when recovery is *possible but unsupported* (Instagram's 30-day restore was always feasible; it simply hadn't been designed). Genuinely unavoidable real-world irreversibility (processed payment, delivered-and-read message) is scoped out — but a time-limited recovery window often exists even there.

**Boundary.** IS: unsupported-but-feasible recovery. NOT present when: irreversibility is genuine AND a *non-habituating* confirmation guards it (typed phrase, not a clickable dialog — users auto-dismiss standard dialogs); irreversibility is the intended, understood, desired outcome (permanent deletion of a sensitive file — then complicate the confirmation); a time-limited recovery window exists. A standard confirmation dialog alone does NOT disconfirm. Root cause of **Data Loss** when the unrecoverable action destroys work (reversibility fixes both — fix-based). Pairs against **Unnecessary Step(s)**: confirmations are usually a symptom; reversibility removes the risk AND the step. **Inviting Dead End** upstream when a misleading element led into the irreversible act (Reserve that means Purchase) — that Trap is root cause of the *entry*; this one owns the *no-exit*.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows/code).*
1. Walk every consequential action in scope; for each ask: is there undo? a recovery window? a back path that truly restores prior state?
2. Flag every consequential action with none of the three; record what guards it instead (nothing / standard dialog / non-habituating confirmation).
3. Flag commitment-understating labels on irreversible actions (Reserve→Purchase) as co-candidates for Inviting Dead End.
4. Flag existing confirmation dialogs for the reversibility-instead question (feeds Unnecessary Step(s)).

**Disconfirmation (pass two).** Per Boundary (a)–(c).

**Severity.** Scales with stakes: Low for trivial unrecoverable acts; High for consequential purchases/deletions; Critical for real-world irreversible harm (flight purchased, legal filing, safety actions). Likelihood risers: the action is reachable in fewer steps than its weight suggests; labels understate commitment; time pressure (C3).

**Assessability & Confidence.** Probable from flows/design (absence of visible undo is structural; whether recovery is *technically feasible* needs architecture knowledge) — promotion path: technical review. Confirmed from code showing no recovery path for a feasible one. Context axis: C2 sharpens stakes; C3 (pressure) raises likelihood.

**Attribution.** Data Loss pairing (fix-based, above). Unnecessary Step(s) pairing (reversibility beats confirmation). Inviting Dead End entry (above). Bad Prediction note: proactive error-prevention prompts ("send without attachment?") are predictions — hold them to predict-when-certain.

**Report fragments.** Finding: "[Action] cannot be undone; no recovery mechanism (undo, time-limited window, or non-habituating confirmation) exists." Why it matters: "Users who act unintentionally or under misapprehension have no path back — the cost of the error is permanent."

**Remediation.** Design forwards and backwards: for every consequential action, what does a user who changed their mind do? Reversibility over confirmation — it removes the risk and the step. Where truly irreversible: time-limited recovery window if feasible; else a non-habituating confirmation (typed phrase). Proactively prevent where prediction is certain.
