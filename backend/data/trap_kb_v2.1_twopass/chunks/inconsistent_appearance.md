<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: INCONSISTENT APPEARANCE *(draft-grade)*
*Sub-tenet: Consistent with Expectations*

**Definition.** The same interface element is presented in a different style at different times — visual or auditory: differing icons, labels, control styling, or sounds for the same function while position may hold. Users cannot form an automatic response to something that doesn't reliably present itself the same way; worse, a learned form may not be *recognized* in its variant form — habit breaks, deliberation resumes (Windows' Fluent-vs-legacy settings is the persistent example).

**Boundary.** IS: inconsistent presentation of the same element/function. IS NOT **Wandering Element** (placement vs. appearance — independent audits, separate evidence). Downstream: can temporarily produce an **Uncomprehended Element** when a familiar function appears in an unfamiliar form — confirm the variant is genuinely unclear, not merely different; when it is, this Trap is root cause (fix-based: unifying the form restores recognition). NOT present when: variation is intentional and communicates a meaningful distinction (save styled differently in edit vs. view mode to signal the mode); the legacy context is one users recognize as distinct; the element is low-frequency.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature; declare on single-screen artifacts.*
1. Identify recurring functions across screens in scope; prioritize core actions — New, Delete, Edit, Share, Search — and recurring status vocabulary.
2. For each, collect every visual/auditory representation across contexts; flag any function with more than one form (icon variants, icon-in-one-place-word-in-another, mixed design languages, legacy/current coexistence).
3. Record whether variation is systematic (design-language boundary) or scattered (drift) — informs remediation.

**Disconfirmation (pass two).** Per Boundary conditions.

**Severity.** Medium baseline — slowed recognition and habituation, plus per-form learning cost; escalates on C4 (core recurring actions) and at comprehension breakdown (route the Uncomprehended Element consequence). Escalator: mixed design languages across a product boundary users cross constantly.

**Assessability & Confidence.** Confirmed from multi-screen design files — cross-context visual comparison of recurring elements is directly auditable; like its placement twin, an AI-native strength and a blind spot of task-based human review. Context axis: C4 weights severity; C1 softens where the population knows the legacy context as distinct.

**Attribution.** Wandering Element co-audit. Uncomprehended Element downstream (fix-based, above). Gestalt similarity note: inconsistent forms don't just fail recognition — they actively signal *different function*, misleading category perception.

**Report fragments.** Finding: "[Function] appears as [form A] in [context 1] and [form B] in [context 2] — users who learned one form will not automatically recognize the other as the same function." Why it matters: "Each form users must learn for the same function is a cognitive investment consistency would have eliminated — and variant forms can read as different functions entirely."

**Remediation.** A design system specifying every recurring element's presentation, enforced — deviations require explicit justification. Evolving the design language obligates a legacy-component audit; don't let two languages coexist. Core actions represented identically product-wide.
