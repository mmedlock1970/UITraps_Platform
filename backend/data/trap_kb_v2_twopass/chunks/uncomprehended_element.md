<!-- GENERATED from trap_kb_v2.md — do not edit; regenerate on any master edit -->
### TRAP: UNCOMPREHENDED ELEMENT *(ratified 2026-07-04)*
*Sub-tenet: Comprehensible*

**Definition.** The user notices an interface element but cannot make sense of its meaning or how to interact with it. Applies to icons, labels, controls, physical affordances, text prompts, and audible elements. The governing question is not "will users figure it out?" but "have we made sure they already know?" — comprehension is previously learned recognition, not deduction.

**Boundary.**
- IS: a noticed element that yields *no* confident interpretation for the target population. "Noticed" includes passing over: the user looked at it, failed to interpret it, and moved on — noticing happened, comprehension failed.
- IS NOT **Inviting Dead End** (sibling Trap — see Taxonomy Index for the reserved definition): there, the user forms a confident interpretation that is *wrong*. Tie-breaker: no interpretation → here; wrong interpretation → there. Under a mixed population (C1/C4 defaults), both can be simultaneously true of one element for different segments — use the segment-conditional trap line (G3), each Trap independently evidenced.
- IS NOT **Effectively Invisible Element**: that Trap is failure to notice; this one begins after noticing succeeds. But note the two-gate interaction: the same unfamiliar element can be filtered pre-attentively (that Trap) or noticed and undecodable (this one) — when the fix converges, one issue, manifests-as pattern (G3).
- IS NOT **Memory Challenge**: a user who once learned the meaning but cannot recall it has a recall failure, not a comprehension failure — the interventions differ.
- IS NOT a state-visibility problem: when the issue is that current state or selected values are not shown (filter state invisible, selection undisplayed), the meaning of the element may be perfectly clear — route to Feedback Failure or Invisible Element. The test: MEANING of the element unclear → here; VISIBILITY of state → there.
- IS NOT **Information Overload** — opposite polarities: that Trap is too much understandable content; this one is content insufficient to interpret or act confidently. If the problem description reads as the reverse of the chosen Trap's definition, the wrong Trap was chosen.
- Comprehension is not static: replacing a learned element's form or meaning (a heart that becomes a check; a mic that becomes a brand symbol) creates this Trap for experienced users — their learning attached to the old form.
- IS NOT unfamiliarity in the abstract: comprehension is population-relative (C1).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the goals (C2), enumerate, on each screen in scope, every element the user must interpret to proceed: icons, labels, controls, affordances, prompts.
2. Classify each: (a) universal convention (magnifying glass, house, gear); (b) domain convention; (c) product/brand-specific symbol; (d) novel element. Record whether a text label accompanies it, and whether icon and label agree.
3. Flag: any (c) or (d) element for a core function lacking a text label; any element whose icon and label contradict each other; any label using insider or domain jargon outside the population's presumed vocabulary (C1); any (b) element when C1 does not establish domain familiarity.
4. Name each flag with the element, its classification, and the missing compensation (G6).

5. Flag meaning or state encoded solely in hue with no shape, label, or position redundancy — ~8% of males have a color-vision deficiency; the finding is population-conditional, but the encoding fact itself is eligible for High confidence from pixels. Contrast-adjacent legibility routes to Physical Challenge.

**Disconfirmation (pass two).** NOT present when: (a) the element is a widely adopted convention the population is demonstrably familiar with (C1, or the C1 default for universal conventions); (b) a text label compensates for an unclear icon — a label reduces but may not eliminate the Trap when the icon actively contradicts it; (c) effective instruction is delivered at the moment of first encounter.

**Severity.** High when the element is on the critical path — most users choose not to "figure it out"; they abandon. Medium when alternatives exist. Escalators: C4 — one-time tasks (setup, onboarding) make this Trap paramount: every user is a first-timer, forever, and habituation will never rescue it.

**Assessability & Confidence.** High-confidence ceiling from a static artifact for brand symbols used as functional icons with no conventional equivalent and no text label — the risk is high enough on the artifact alone. Otherwise Medium confidence ceiling — comprehension is population-relative; promotion path: show the element to a few target users and ask what it means (cheap; recommend it in reports — there is no excuse for skipping it). Context axis: C1 gates most judgments — the C1 default clears universal conventions only; brand-specific, domain, and novel elements stay flagged under the default. C4 softens: habituated populations lower likelihood.

**Attribution.**
- Inviting Dead End: confirm independently that a specific *incorrect* element is likely to be chosen — not merely that the correct element is unclear. Often co-occur (right path unclear, wrong path compelling), compounding — list both only when both are evidenced.
- Memory Challenge: if users once knew the meaning, the finding moves there — confirm which failure it is.
- Where branding drove the unclear element, name the root cause as over-indexing on differentiation (a design-decision cause, not a separate Trap).

**Report fragments.** Finding: "[Element] is unlikely to be correctly interpreted by users unfamiliar with [product/brand/domain convention], and no standard element or text label clarifies its meaning." Why it matters: "Users who cannot interpret this element cannot determine how to proceed — and most will not work to figure it out."

**Remediation.** Use universally recognized elements for core functions. When in doubt, add a text label — a labeled unclear icon always beats an unlabeled one. For genuinely novel concepts, plan instruction delivered when the user is ready to receive it. Replacing a well-learned brand symbol with a conventional element is almost always the right call for functional elements, even at the cost of brand expression.
