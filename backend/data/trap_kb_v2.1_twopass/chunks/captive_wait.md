<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: CAPTIVE WAIT *(draft-grade)*

**Definition.** The system does not allow the user to advance or back out of a process at a time of their choosing: unskippable pre-roll ads and cutscenes, updates that commandeer the device, locked flows. Frustration is disproportionate to time cost because the violation is of *control*, not speed.

**Boundary.** IS: denied ability to advance, skip, or exit. IS NOT **Slow or No Response** (speed, not control) — a captive wait can be short and still this Trap. IS NOT **Forced Syntax** (order, not exit). NOT present when the wait is skippable, when duration is disclosed and reasonable for a purpose users accept, or when technically unavoidable AND pre-announced with an accurate estimate AND the limitation is one users find reasonable.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flow states).*
1. Walk every flow; at each state, test: can the user advance at will? back out? skip? Flag every state where all three fail.
2. Flag auto-advancing/auto-dismissing screens that deny reading-pace control **[JUDGMENT: the inverse capture — the system moves when the user wanted to stay]**.
3. For each flag, record: duration, disclosure of duration, skip affordance and when it appears, and whether the captive content serves the user's goal or the business's.
4. Attend especially to onboarding, setup, updates, and ad placements.

**Disconfirmation (pass two).** NOT present when: (a) skippable (even after a brief mandatory period); (b) duration disclosed and judged reasonable for the purpose; (c) technically unavoidable + advance notice + accurate estimate + reasonable limitation.

**Severity.** Medium typically — but escalates on repetition (C4: an unskippable ad on every session compounds) and when users are in active goal pursuit rather than passive browsing; High when captivity blocks time-sensitive goals or forces abandonment. Undisclosed duration compounds (uncertain waits feel longer — route the missing disclosure to Feedback Failure as co-occurring).

**Assessability & Confidence.** Confirmed from flows/live/code (locked states and missing skip paths are structural). Static screenshots: not assessable beyond visible skip affordances — declare. Context axis: C2 gates the goal-service judgment; C4 sharpens severity via repetition.

**Attribution.** Feedback Failure: confirm independently that duration/purpose are undisclosed — disclosure reduces severity without dissolving the Trap. Business-driven captivity (forced ad exposure) flags as potential dark pattern, per the Distraction precedent **[JUDGMENT: extending the D1 ruling]**.

**Report fragments.** Finding: "[Flow/screen] prevents advancing or backing out for [duration/unknown], without [skip / disclosure / service to the user's goal]." Why it matters: "Perceived control shapes experience independent of duration — captivity generates frustration disproportionate to its time cost."

**Remediation.** Question every no-exit point. Make content skippable as fast as possible; disclose duration upfront; for system processes give advance notice, allow parallel work, notify on completion; anything >10 s needs a stop or background option. Prefer progressive disclosure over mandatory flows.
