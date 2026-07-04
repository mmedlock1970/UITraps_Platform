<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: UNNECESSARY STEP(S) *(draft-grade)*

**Definition.** The number of steps to achieve a goal exceeds what it needs to be: steps that could be eliminated, automated, or combined without loss. The target is the *right* number, not the minimum — steps that make an experience more understandable (wizard vs. one dense screen) are a legitimate trade.

**Boundary.** IS: eliminable/automatable/combinable steps. IS NOT present when a step serves a documented legitimate purpose: confirmation for consequential irreversible actions; cognitive-load chunking; security/legal/safety requirements. Confirmation dialogs on *reversible* actions are this Trap by definition (reversibility makes them pure cost). IS NOT **Forced Syntax** (wrong order vs. too many). Caused by **Gratuitous Redundancy** when duplicates displace content into scrolling — confirm displacement independently.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows).*
1. Walk each C2 task flow end to end; count steps; for each ask: eliminable? automatable? combinable?
2. Flag: confirmation dialogs (check reversibility of the confirmed action — reversible = automatic flag); per-field confirmations; navigation depth (levels descended to reach frequent functions — hamburger-nested high-frequency actions are the canonical case); re-entry of derivable information; round-trips between choice and outcome views (missing previews).
3. Flag forced prerequisite gates: the artifact shows users must complete a prerequisite (authentication, registration, paywall, mandatory consent) before reaching core functionality, AND either (a) the core function does not technically require it, or (b) a guest/unauthenticated path would reasonably serve the stated goal. Do NOT classify a gated path as Invisible Element — the path is blocked, not hidden.
4. Flag flows evidently accreted by multiple teams (style shifts mid-flow) for end-to-end audit **[JUDGMENT: heuristic indicator]**.

**Disconfirmation (pass two).** NOT present when: (a) the step serves a legitimate documented purpose; (b) it chunks complexity for comprehension; (c) security/legal/safety requires it.

**Severity.** Medium baseline (friction); escalates hard on C4 — extra steps on high-frequency tasks are paid on every use (Spotify's nav-flattening produced large engagement gains); High when cumulative cost drives abandonment.

**Assessability & Confidence.** Confirmed for confirmation-on-reversible (structural); step counts Confirmed from flows; whether a step is *genuinely* unnecessary stays Probable without C2 purpose knowledge — promotion path: task analysis with the team. Context axis: C2 gates necessity judgments; C4 drives severity.

**Attribution.** Gratuitous Redundancy as root cause (displacement — confirm independently). Irreversible Action: confirm irreversibility before condemning a confirmation; the superior fix is usually reversibility, which removes both the risk and the step (fix-based pairing).

**Report fragments.** Finding: "[Task] requires [N] steps; [which] could be eliminated, automated, or combined without loss." Why it matters: "Every unnecessary step is a cost paid on every use — compounding across frequency into significant lost efficiency."

**Remediation.** Surface high-frequency functions to persistent navigation; provide hierarchy-cutting paths (search, command, voice); replace confirmations with reversibility; preview outcomes to kill round-trips; audit accreted flows end to end.
