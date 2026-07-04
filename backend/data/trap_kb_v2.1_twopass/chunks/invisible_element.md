<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: INVISIBLE ELEMENT *(draft-grade)*
*Sub-tenet: Noticeable*

**Definition.** Nothing in the interface communicates how to achieve a goal — no label, icon, or other element — and the user lacks the prior learning to overcome the absence. Applies to absent visual, tactile, or auditory elements. Common forms: hidden swipe actions, press-and-hold actions, hover-only labels.

**Boundary.** IS a *missing* element (in Norman's terms, a missing signifier: nothing signals the action is available). IS NOT Effectively Invisible Element — there, an element exists but goes unnoticed; here, no element exists. IS NOT present when users already carry the knowledge (pinch-to-zoom is invisible but universally learned). IS NOT a gated path: when the path to a goal is absent because a prerequisite gate (authentication, registration, paywall, mandatory consent) blocks access, the path is not hidden — it is blocked; classify under Unnecessary Step(s) (see its forced-prerequisite-gate flag), not here. This Trap requires that the path exists but lacks visible communication. Content pushed off-screen by other elements is treated as this Trap **[JUDGMENT — per the manuscript's Gratuitous Redundancy cross-reference; confirm off-screen = Invisible rather than Effectively Invisible]**.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + task analysis.*
1. From C2 goals, enumerate goals achievable on/from this screen per the product's actual capabilities (from flows, code, or documentation where available).
2. For each goal, check: does any visible/audible/tactile element communicate how to initiate it?
3. Flag every goal with no communicating element — noting whether an invisible interaction is the SOLE path (highest concern) or a visible alternative exists.
4. Flag interactions requiring gestures with no on-screen element signaling them (swipe, press-and-hold, hover-reveal, corner-hotspots).
5. Flag content that continues beyond the visible fold with no visible continuation indicator — scroll affordances cannot be assumed absent strong prior learning for that context.
6. Flag fallback interactions that are the sole path when a primary modality is unavailable (per C3) but carry no visible communication — a fallback is an Invisible Element in exactly the context where it is needed.
7. Where version or redesign context is available: flag removal of a formerly visible element for a core function — prior learning pointed to the element, not the underlying interaction, so removal creates this Trap even for experienced users. Static-screenshot limitation: the analyzer can only detect this Trap for goals it knows the product supports — declare "capability list needed" when goals cannot be enumerated.

**Disconfirmation (pass two).** NOT present when: (a) users have sufficient prior learning from products they regularly use — standard: the interaction exists on multiple established platforms, or the target population (C1) demonstrably learned it; (b) an alternative visible means of the same action exists; (c) effective instruction has demonstrably been delivered meeting all six conditions: presented when the user is ready and motivated; action physically easy; feedback immediate and clear; total invisible-interaction count kept very low; each action distinguishable; training reintroduced on retention failure.

**Severity.** High by default — the user cannot achieve a goal they would reasonably attempt; Critical in safety contexts (vehicle exits, emergency functions — see Tesla door releases). Low–Medium when a visible alternative exists (invisible path is then an expert shortcut). C4: for one-time tasks, instruction-based mitigation is weakest (no chance to habituate).

**Assessability & Confidence.** Sole-path invisible interactions with no visible alternative: Confirmed ceiling from artifact + capability knowledge (Tier-1-like). Otherwise Probable ceiling — prior learning (C1) gates disconfirmation (a). Code/flow artifacts materially improve detection (hidden handlers enumerable). Context axis: C1 gates clearing on prior-learning grounds; C3 raises severity when the invisible path's modality is unavailable (voice command in a loud venue — the Humane Pin case).

**Attribution.** Often root cause of Variable Outcome: a mode with NO indicator. Confirm outcome variation independently; the missing indicator alone confirms only this Trap. With Memory Challenge: a trained-but-forgotten invisible interaction is both — recall failure vs. never-learned determines which leads. Distinguish from Effectively Invisible Element via existence: no element → here; unnoticed element → there.

**Report fragments.** Finding: "No visible element signals how to achieve [goal]; users cannot reasonably be expected to discover [interaction]." Why it matters: "Users who do not discover this interaction cannot complete the goal."

**Remediation.** Make the action visible — almost always the easier and more reliable path. If the invisible interaction must remain, deliver instruction meeting the six conditions, and keep the total number of invisible interactions very low. Emergency and fallback interactions — needed precisely when users are most stressed — must be the most visibly communicated interactions in the product, not the least.
