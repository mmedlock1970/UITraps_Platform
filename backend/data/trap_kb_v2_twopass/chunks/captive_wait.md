<!-- GENERATED from trap_kb_v2.md — do not edit; regenerate on any master edit -->
### TRAP: CAPTIVE WAIT *(ratified 2026-07-04)*

**Definition.** The system does not allow the user to advance or back out of a process at a time of their choosing: unskippable pre-roll ads and cutscenes, updates that commandeer the device, locked flows. Frustration is disproportionate to time cost because the violation is of *control*, not speed.

**Boundary.** Scope is bidirectional: control over WHEN is denied whether the user is held past their choosing (cannot advance or exit) or dragged before it (auto-advancing/auto-dismissing content) — \"at a time of their choosing\" covers both directions. IS: denied ability to advance, skip, or exit. IS NOT **Slow or No Response** (speed, not control) — a captive wait can be short and still this Trap. IS NOT **Forced Syntax** (order, not exit). NOT present when the wait is skippable, when duration is disclosed and reasonable for a purpose users accept, or when technically unavoidable AND pre-announced with an accurate estimate AND the limitation is one users find reasonable.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flow states).*
1. Walk every flow; at each state, test: can the user advance at will? back out? skip? Flag every state where all three fail.
2. Flag auto-advancing/auto-dismissing screens that deny reading-pace control.
3. For each flag, record: duration, disclosure of duration, skip affordance and when it appears, and whether the captive content serves the user's goal or the business's.
4. Attend especially to onboarding, setup, updates, and ad placements.

**Disconfirmation (pass two).** NOT present when: (a) skippable (even after a brief mandatory period); (b) duration disclosed and judged reasonable for the purpose; (c) technically unavoidable + advance notice + accurate estimate + reasonable limitation.

**Severity.** Medium typically — anchor: the unskippable advertisement before requested content (card example): Medium, escalating hard on C4, every session pays it — and escalates on repetition (C4: an unskippable ad on every session compounds) and when users are in active goal pursuit rather than passive browsing; High when captivity blocks time-sensitive goals or forces abandonment. Undisclosed duration compounds (uncertain waits feel longer — route the missing disclosure to Feedback Failure as co-occurring).

**Assessability & Confidence.** High confidence from flows/live/code (locked states and missing skip paths are structural). Static screenshots: not assessable beyond visible skip affordances — declare. Context axis: C2 gates the goal-service judgment; C4 sharpens severity via repetition.

**Attribution.** Feedback Failure: confirm independently that duration/purpose are undisclosed — disclosure reduces severity without dissolving the Trap. Business-driven captivity (forced ad exposure) flags as potential dark pattern, per the Distraction precedent.

**Report fragments.** Finding: "[Flow/screen] prevents advancing or backing out for [duration/unknown], without [skip / disclosure / service to the user's goal]." Why it matters: "Perceived control shapes experience independent of duration — captivity generates frustration disproportionate to its time cost."

**Remediation.** Question every no-exit point. Make content skippable as fast as possible; disclose duration upfront; for system processes give advance notice, allow parallel work, notify on completion; anything >10 s needs a stop or background option. Prefer progressive disclosure over mandatory flows.
