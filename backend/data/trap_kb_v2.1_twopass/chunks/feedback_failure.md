<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: FEEDBACK FAILURE *(draft-grade)*
*Sub-tenet: Confirmatory*

**Definition.** The system fails to communicate the consequence of the user's action, or how to resolve a failed action. Unlike other Traps, this one is defined by a *moment* — what happens after the user acts — not a single mechanism. Any failure that leaves the user without a clear understanding of what their action accomplished, or how to recover, qualifies. It is an additional lens: it exists to force evaluators to check whether the system closes the loop on every action, because feedback is foundational to how people learn an interface.

**Boundary.** IS: a broken action→response loop. Its root cause is almost always another Trap, and per the manuscript the root cause MUST be identified before this Trap is flagged: no feedback element exists → Invisible Element; feedback present but away from attention → Effectively Invisible Element; noticed but unclear → Uncomprehended Element; physically hard to perceive → Physical Challenge; too late → Slow or No Response; factually wrong → Incorrect Information; inconsistent across occasions → Variable Outcome. Report ONE issue with the root cause designated and Feedback Failure listed as the lens/consequence (G3). IS NOT present when the consequence is self-evident from the resulting state, or when silence is itself the designed, understood signal.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen — audits action→response pairs.*
1. Enumerate every user action in scope (taps, submissions, commands, toggles).
2. For each, record the system's response: what changes, where, when, and does it state what happened and — on failure — what to do now?
3. Flag: actions with no perceivable response; error messages that fail either question ("what went wrong?" / "what should I do?") — auditable without any user testing; feedback arriving after the user would have moved on; post-submission validation where continuous validation is feasible.
   *In-screen vs. post-action rule (partial artifacts):* feedback that should appear on the same screen immediately (button state, inline validation, loading indicator) is Confirmed absent if not visible there; feedback that would arrive on a subsequent screen (toast, confirmation page) must NOT be asserted absent from a partial artifact — use conditional language ("if no confirmation exists elsewhere in this flow, users would have no indication the action completed") and route to the closer-look bucket per G8.
   Feedback scope includes surfacing hazards and consequential states the user needs to know about, not only confirming intended actions.
4. Route each flag to its candidate root cause per the Boundary list, as input to pass two.

**Disconfirmation (pass two).** NOT present when: (a) the consequence is self-evident from the resulting interface state; (b) absence of feedback is itself the meaningful, understood signal (silence = no error, by established convention); (c) the failure is fully attributed to a root-cause Trap — then that Trap is the finding and this one rides the trap line.

**Severity.** Medium for confusion/repeated attempts; High when users cannot recover from errors; Critical when absent feedback compounds an irreversible action or conceals a safety condition (play-space boundaries). Escalators: C3 (occupied channels can make otherwise-adequate feedback imperceptible — route to Physical Challenge/Effectively Invisible Element as root cause).

**Assessability & Confidence.** Error-message quality: Confirmed from artifact (audit each message against the two questions). Absent responses: Confirmed from flows/live/code (action→response pairs enumerable). Noticeability/comprehensibility of feedback: Probable ceiling — inherits the root-cause Trap's profile. Not assessable for physical-feedback products from digital artifacts — declare.

**Attribution.** Root-cause routing is mandatory (Boundary). Irreversible Action: recovery feedback only helps when recovery exists — when both fail, list both, Irreversible Action root cause for the recovery half **[JUDGMENT]**.

**Report fragments.** Finding: "When users [action], the system fails to communicate [what happened / what to do next] in a way that is [noticeable / comprehensible / timely / actionable]." Why it matters: "Without clear feedback, users cannot confirm success, recover from errors, or learn how the system responds."

**Remediation.** Every action produces a response that is immediate, clear, and sufficient. Error messages answer both questions. Prefer continuous real-time validation over post-submission. The fix depends entirely on the root cause — identify it first.
