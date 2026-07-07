<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: VARIABLE OUTCOME *(ratified 2026-07-04)*
*Sub-tenet: Consistent with Expectations*

**Definition.** The system responds differently and unexpectedly to the same user action at different times. Most often a mode error (CapsLock; gear selectors; overloaded controls), but modes aren't required — inconsistently supported functions (right-click works on some instances, not others) qualify. The key question is not whether the same action produces different results, but whether the user is *attending to the signal that explains the difference*: a context-dependent button the user is looking at is unproblematic; a mode tracked only in memory is the Trap.

**Boundary.** IS: same action, different outcome, with the explaining state outside the user's awareness. Physically distinct lookalike elements with different functions are NOT this Trap's root — route to Inviting Dead End (root cause) with this Trap as C4-gated consequence (see Gratuitous Redundancy's fork); this Trap proper requires literally the same control varying over time. NOT present when: a mode indicator sits within the user's attentional focus at the moment of action; the state is a quasi-mode the user physically sustains (held Shift — impossible to forget); variation is in degree, not kind (harder flick scrolls faster); the state change is itself an explicit user action they'd be attending to. Caused by **Invisible Element** (no indicator exists) or **Effectively Invisible Element** (indicator exists, placed away from attention) — confirm the indicator's existence/placement independently; do not infer either from the outcome variation alone; when confirmed, the indicator Trap is root cause (fixing it dissolves the surprise — fix-based). **Accidental Activation** worsens on overloaded, state-dependent controls — consistency is root cause there.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-state; code is the native artifact.*
1. Code artifacts: sweep for state-handlers — any place one user action routes to different outcomes by system state; each is a candidate.
2. Flow/live artifacts: for each control, probe across contexts/states — same action, same result? Flag every divergence.
3. For each candidate, locate the state signal: does one exist? where, relative to the user's attentional focus at the action moment (feeds EIE/IE routing)? Is the state user-sustained (quasi-mode)?
4. Flag inconsistently supported functions (same element type responding differently across instances) — the modeless form; static screenshots cannot detect this Trap — declare.

**Disconfirmation (pass two).** Per Boundary conditions (a)–(d) above.

**Severity.** Medium for surprise-and-retry; High when the wrong-state action costs the task; High in safety contexts — mode error is a recurring factor in aviation, vehicle, and medical catastrophes (the Monostable shifter killed). For safety-critical interfaces the acceptable mode-error risk is zero: redesign to eliminate the mode, not to improve the indicator. Escalators: C3 (attention elsewhere is precisely when modes are forgotten — driving); C4 (overloaded controls in core loops slow all learning — game-controller research).

**Assessability & Confidence.** High confidence detection from code (state-handlers are directly findable — an AI-native strength); whether users will be unaware of the state: Medium confidence, gated by attention knowledge (C2/C3) — promotion path: observe attention at the action moment. Modeless form: harder, needs flows/live probing. Context axis: C3 gates the awareness judgment; C1 (prior product conventions) softens.

**Attribution.** Indicator routing per Boundary (fix-based). Wandering Element and Inconsistent Appearance are the placement/appearance members of this consistency family — audit each independently. Ambiguous Home: a home action that sometimes lands elsewhere is this Trap co-occurring there.

**Report fragments.** Finding: "[Action] produces different outcomes depending on [state], and no indicator of that state is reliably within the user's attention when acting." Why it matters: "Unexpected outcomes prevent reliable habits — and in safety-critical contexts, mode errors kill."

**Remediation.** Eliminate the mode where possible — consistent behavior beats a well-indicated mode (even perfectly visible indicators lose to dedicated functions for learning speed). Where unavoidable: put the indicator where attention already is at the action moment, or convert to a user-sustained quasi-mode. Safety-critical: eliminate, don't indicate.
