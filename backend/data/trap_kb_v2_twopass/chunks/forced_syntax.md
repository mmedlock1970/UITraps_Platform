<!-- GENERATED from trap_kb_v2.md — do not edit; regenerate on any master edit -->
### TRAP: FORCED SYNTAX *(ratified 2026-07-04)*
*Sub-tenet: Comprehensible*

**Definition.** The interface honors only one of several reasonable ways to sequence or express a task. Two sub-patterns:
- **A — Construction rigidity:** only one ordering of task steps is supported (object→action but not action→object; wake-word must precede command).
- **B — Expression rigidity:** input is accepted in only one exact format when multiple unambiguous formats exist (dates, phone numbers, currency, names with diacritics).

**Boundary.**
- IS: either sub-pattern, where at least one unsupported alternative is one users would reasonably expect or prefer.
- IS NOT **Gratuitous Redundancy** — mutually exclusive per task flow: only-one-construction = Forced Syntax; duplicate paths via the same construction = Gratuitous Redundancy. Confirm which is present before flagging either.
- IS NOT present when the task has a single dominant natural order virtually all users share, or when the fixed order is a genuine technical constraint.
- IS NOT an obligation to support every conceivable sequence: only reasonably likely alternatives count — for presence and for remediation.
- IS NOT **Captive Wait**: Forced Syntax imposes *order*; Captive Wait imposes *timing and exit* — a flow the user cannot back out of is Captive Wait even if its ordering is flexible.
- IS NOT **Unnecessary Step(s)**: if users must restart a flow because of the syntax constraint, confirm the extra steps are caused by the constraint, not separate flow design, before attributing.

**Detection procedure (pass one — flag, do not filter).** *Unit: sub-pattern B per-screen; sub-pattern A cross-screen (flow-level by nature).*
- Sub-pattern B (any artifact): (1) enumerate every free-input field; (2) record format signals — input masks, placeholder text prescribing an exact format, format-error messaging, character restrictions; (3) flag any field demanding a single encoding of information that has multiple common unambiguous encodings; name the field and the excluded encodings.
- Sub-pattern A (flow, prototype, live, or code artifacts): (1) state the task goal; enumerate the reasonable constructions (object→action, action→object, distinct entry points users would plausibly try); (2) walk the flow attempting each; record whether an entry point exists for it; (3) flag when exactly one construction is honored and at least one alternative is reasonably likely for this population.
- Sub-pattern A (static screenshot): flag as risk-only when a single rigid entry point is visible; label "needs flow or code to confirm alternative constructions."

**Disconfirmation (pass two).** NOT present when: (a) the sequence has a dominant natural order virtually all users expect for this task type; (b) the interface already provides the most common alternative construction; (c) the rigidity is a genuine technical constraint. Supporting every possible sequence is not required — only reasonably likely alternatives.

**Severity.** High when users abandon — assuming the function is unsupported or failing to find the supported sequence; Medium for reorganization friction. Anchor: the command accepted only wake-word-first — "Alexa, what time is it?" works, "What time is it, Alexa?" doesn't (card example): Medium — reorganization friction taxing every use. Voice-driven interfaces raise likelihood (natural speech has maximal grammatical flexibility). Escalators: C4 (a rigid construction in a daily task taxes every use); mixed novice/expert populations (C1) raise likelihood — the stages of skill acquisition construct tasks differently.

**Assessability & Confidence.** Sub-pattern B: High confidence from a static screenshot when masks/placeholders/error text are visible; fully confirmable live by probing accepted formats. Sub-pattern A: structurally High confidence from flows/code (which constructions exist), but whether unsupported alternatives are "reasonably expected" stays Medium confidence without C1 — promotion path: population data or user observation of attempted starting points. Context axis: C1 softens under its default (mainstream conventions); C2 identifies the tasks that matter.

**Attribution.** Mutual exclusivity with Gratuitous Redundancy (above). Unnecessary Step(s): independent confirmation before adding. Sequence routing map (author-ruled): (1) user doesn't know how to proceed, no expectation story → Invisible/Effectively Invisible/Uncomprehended Element per their boundaries, not this Trap. (2) User misses or misreads the entry point BECAUSE they are anchored at a different semantic starting point → bidirectional pair with the element Trap: supporting their natural start (this Trap's fix) dissolves the element problem; making the entry salient dissolves discovery but leaves the unnatural order — list both, note the bidirectionality, name the deciding check. (3) User notices, understands, and merely dislikes the required order → this Trap alone (the Alexa case). (4) User completes the sequence but cannot recall it later → this Trap (root cause), Memory Challenge (consequence, C4-gated): the recall burden exists because the required order is arbitrary relative to the user's mental model, and accepting their natural construction dissolves it. Memory Challenge stands alone only when the recalled content is intrinsically arbitrary (codes, passwords) — no syntax flexibility removes those.

**Report fragments.** Sub-A: "[Task] can be initiated only via [construction] — users who naturally approach it via [alternative] will find the interface unresponsive to their intent." Sub-B: "[Field] accepts only [format]; common valid encodings [list] are rejected." Why it matters: "Users who think differently from the assumed sequence must reorganize their approach before proceeding — friction, and abandonment risk if they conclude the capability is missing."

**Remediation.** Sub-A: identify all reasonable starting points and accept them; plan explicitly which tasks support object→action AND action→object; support only reasonably likely constructions. Sub-B: parse tolerantly — accept all common unambiguous encodings and normalize internally; reserve rejection for genuinely ambiguous input.
