<!-- GENERATED from trap_kb_v2.md — do not edit; regenerate on any master edit -->
# PASS ONE — DETECTION PACK (KB v2, two-pass structure)

**Role of this pass:** permissive detection. Run every procedure below against the artifact. Flag every candidate with named evidence. Do NOT filter, do NOT weigh disconfirmation, do NOT assign severity — over-reporting at this stage is correct behavior. Adjudication happens in pass two with different materials.

**Harness guidance (not KB content):** for speed, instruct the model to emit candidates in a terse line format — `TRAP | screen | element(s) | triggering condition(s)` — one line per candidate, no prose. Decode time scales with output length; adjudication needs the evidence, not an essay.

**G1. Exact trap names.** Use full, exact Trap names; several Traps have near-identical names that denote different problems.

**G2. Two-pass discipline, with selective loading.**
- **Pass one (detection):** load only the Detection Procedures for all 27 Traps, plus the Context Intake Schema. Run each procedure. Flag every candidate. Do not filter, do not weigh disconfirmation, do not assign severity. Over-reporting at this stage is correct behavior. Candidate-line economy the triggering-condition clause is telegraphic — at most ~15 words, no explanatory subordinate clauses. Pass one routes chunks; pass two explains.
- **Pass two (adjudication):** load the full chunks for candidate Traps only, plus the Taxonomy Index (so adjudication can re-route a finding to a non-candidate Trap when a Boundary clause points there). For each candidate, apply in order: (1) Boundary and Disconfirmation; (2) the one-problem-one-issue procedure (G3); (3) the Assessability lookup (G4/G5); (4) Severity and Confidence; (5) assemble the issue per G8. Kill, merge, and relabel freely — that is this pass's job.
- **Mode-agnostic discipline:** the staging above describes the two-pass runtime. In single-call execution the same discipline applies sequentially within one response: complete the full permissive detection sweep across ALL Traps first, then adjudicate the resulting candidates. Never filter, weigh disconfirmation, or assign severity during the detection sweep, in any mode.

**G6. Named evidence — symmetric.** Every flag, in either pass, must cite the specific element(s) and condition(s) that triggered it. General impressions ("feels cluttered," "low prominence") are not findings. Clearances are held to the same bar a "Not present" verdict must cite the specific disconfirming observation or the scope the procedure actually ran against, with the same specificity required of a finding — and must address the Trap's full definitional scope as given in its chunk. Clearing one manifestation (one element class, one screen region, one definitional clause) does not clear the Trap; state the scope actually cleared. A clearance without named evidence is not a clearance — emit the applicable not-assessable label from G4 instead. Per-instance enumeration (author-ruled 2026-07-06; scope widened 2026-07-08): any claim about the *observable state* of repeated or parallel elements — their **presence/absence, their position or corner, their count, or their relative arrangement** — must enumerate every instance with its specific observed state before the claim is made. Presence/absence, spatial position, and count across repeated elements are the highest-risk observation class: findings whose reasoning depends on such a claim (e.g., "badge X is top-left while badge Y is top-right," "the indicator appears on some tiles but not others") must re-verify the claim against the specific image region and state each instance's observed value in the finding. A spatial, presence, or count claim that is not enumerated instance-by-instance is not a finding. This gate governs the "directly observable technical fact" license in the Confidence-calibrated-prose rule: an observational claim earns plain, High-confidence statement only after this per-instance verification; unverified spatial/presence/count claims may not be stated plainly and may not carry High confidence — downgrade, or route to Worth a closer look.

**G7. Unit of analysis.** Detection Procedures declare their unit: per-screen, cross-screen, or both. For multi-screen artifacts: run per-screen steps on every screen in scope; run cross-screen steps where declared; compute flow-level properties (dominant interaction patterns, persistent elements) across the whole flow before consulting them in per-screen judgments — a single screen misestimates them. Every finding cites the screen(s) where its evidence sits.

---

## CONTEXT INTAKE SCHEMA (canonical — all Trap gates and defaults reference these fields)

**C1. User Knowledge.** Products and conventions the users have already internalized; domain expertise; prior exposure to this product's own conventions. ONE sub-population per evaluation (J26): C1 names a single population; evaluating multiple segments means running multiple evaluations. If a mixed population is provided anyway, analyze against the FIRST-NAMED segment and emit one prominent Coverage line: "Context named multiple populations; this analysis is conditioned on [first-named]. Run a separate evaluation for [others]." *Default when absent:* general adult population familiar with mainstream web/mobile conventions — declare it. Brand-specific, domain-insider, and novel elements cannot be cleared under the default.

**C2. Goals.** The user's primary tasks and critical paths — AND the fuller set of goals users might plausibly bring to each screen (some Traps require the full set, not just the primary; see Inviting Dead End). *Default when absent:* infer the apparent primary task from the screen itself and declare it; findings requiring the full goal set are degraded under this default.

**C3. Context of Use.** Availability of the user's channels and circumstances:
- *Attention:* fully focused, dividing attention across concurrent tasks, or frequently interrupted.
- *Vision:* eyes available vs. occupied (driving, walking, operating equipment).
- *Hearing:* environment quiet enough to hear audio, or too noisy.
- *Speech & audio-out:* free to speak and play audio comfortably — or constrained by disturbing others or by privacy (information that must not be overheard or displayed to bystanders).
- *Hands:* both free, one occupied, both occupied.
- *Mobility:* stationary vs. in motion.
- Plus: lighting, time pressure or stress, device and input method.

*Default when absent:* attentive, stationary, unencumbered, quiet, private use — the most forgiving context on every channel. Declare it, and state that findings under this default are a lower bound: occupied channels raise likelihood of attention- and memory-dependent Traps and can create channel-dependent Traps outright (an auditory-only element in a loud environment; a two-handed interaction for an encumbered user) without any change to the pixels.

**C4. Exposure & Repetition.** Two facets of the learning curve:
- *User exposure stage:* first-run users, habituated users, or a mix.
- *Task repetition profile:* performed once (setup, onboarding), a few times, or repeatedly for as long as the product is used.

Habituating-tenet Traps scale with repetition; one-time tasks make comprehension Traps paramount — every user is a first-timer, forever. *Defaults when absent:* mix including first-time users for public-facing products; infer the task's repetition profile from its nature (setup vs. core loop) — declare both.

---

---

## DETECTION PROCEDURES (all 27 Traps)

### Invisible Element
*no label, icon, or other interface element is provided to let the user know how to achieve a goal, and the user lacks the prior learning needed to overcome its absence.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + task analysis.*
1. From C2 goals, enumerate goals achievable on/from this screen per the product's actual capabilities (from flows, code, or documentation where available).
2. For each goal, check: does any visible/audible/tactile element communicate how to initiate it?
3. Flag every goal with no communicating element — noting whether an invisible interaction is the SOLE path (highest concern) or a visible alternative exists.
4. Flag interactions requiring gestures with no on-screen element signaling them (swipe, press-and-hold, hover-reveal, corner-hotspots).
5. Flag content that continues beyond the visible fold with no visible continuation indicator — scroll affordances cannot be assumed absent strong prior learning for that context.
6. Flag fallback interactions that are the sole path when a primary modality is unavailable (per C3) but carry no visible communication — a fallback is an Invisible Element in exactly the context where it is needed.
7. Where version or redesign context is available: flag removal of a formerly visible element for a core function — prior learning pointed to the element, not the underlying interaction, so removal creates this Trap even for experienced users. Static-screenshot limitation: the analyzer can only detect this Trap for goals it knows the product supports — declare "capability list needed" when goals cannot be enumerated.

---

### Effectively Invisible Element
*an element goes unnoticed because it is unexpected or misaligned with the user's focus of attention.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen, plus cross-screen steps for multi-screen artifacts.*
1. From the stated or assumed user goal, identify the elements on each screen in scope critical to completing it.
2. For each critical element, record: (a) location relative to the likely attentional focus for this task (focus = where the task's primary content or interaction lives, not screen center); (b) whether it differs from surroundings on any pre-attentive feature (color, size, orientation, motion); (c) whether its interaction style matches the flow's dominant interaction pattern (computed per G7); (d) the number of elements competing for attention in its vicinity; (e) **whether the element's appearance matches the visual category users would be searching for, given the goal it serves and their prior experience (C1) — does the thing that does X look like the kind of thing this population expects X to look like?**
3. Flag as candidate any critical element that: is peripheral to the task focus AND lacks pre-attentive distinction; OR deviates from the dominant interaction pattern; OR sits in a high-competition zone; **OR mismatches the user's likely search template for its function — flag regardless of location or visual prominence.**
4. Name the specific condition(s) per flag (G6).
5. Cross-screen (multi-screen artifacts only): flag state or mode indicators that must be noticed on a different screen from where the state was set; flag content that changes between screens in ways the user would not expect (unexpected changes are unlooked-for, hence filtered). Location changes route to Wandering Element; appearance changes route to Inconsistent Appearance (see Boundary).

6. Flag goal-critical elements styled or positioned like promotional content (banner slots, right rails, ad-like framing) — learned suppression of ad-shaped regions applies regardless of C1 product familiarity.

---

### Distraction
*something in the interface draws the user's attention away from their current goal.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; cross-screen for elements that appear during flows.*
1. Enumerate every element that moves, animates, auto-plays, sounds, appears without user initiation, or changes state on its own; plus persistent attention-pulling elements (badges, blinking indicators) and, in flow artifacts, interstitials/notifications injected mid-task.
2. For each, record: user-initiated? relevant to the C2 goal at that moment? modality (motion and peripheral motion are un-ignorable — the orienting response is involuntary)?
3. Flag every uninitiated, goal-irrelevant attention-capturing element; flag cumulative competition (many simultaneous attention-demanding elements — the Boeing 737 pattern) as its own candidate.

---

### Uncomprehended Element
*an element is noticed, but its meaning or required method of interaction is unclear.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the goals (C2), enumerate, on each screen in scope, every element the user must interpret to proceed: icons, labels, controls, affordances, prompts.
2. Classify each: (a) universal convention (magnifying glass, house, gear); (b) domain convention; (c) product/brand-specific symbol; (d) novel element. Record whether a text label accompanies it, and whether icon and label agree.
3. Flag: any (c) or (d) element for a core function lacking a text label; any element whose icon and label contradict each other; any label using insider or domain jargon outside the population's presumed vocabulary (C1); any (b) element when C1 does not establish domain familiarity.
4. Name each flag with the element, its classification, and the missing compensation (G6).

5. Flag meaning or state encoded solely in hue with no shape, label, or position redundancy — ~8% of males have a color-vision deficiency; the finding is population-conditional, but the encoding fact itself is eligible for High confidence from pixels. Contrast-adjacent legibility routes to Physical Challenge.

---

### Inviting Dead End
*an element is incorrectly judged to be a means of achieving a goal; it looks right but is wrong.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for lookalike and hidden-gate flags; cross-screen for path-walking.*
1. Enumerate the goals a user could plausibly bring to each screen in scope — the full C2 set, not only the primary task. An element can be the correct path for one goal and an Inviting Dead End for another.
2. For each goal, walk every plausible path, not just the intended one. At each decision point, list the elements a user unfamiliar with the system might judge the correct next step — weighting visual prominence, label semantics, proximity to the correct path, and similarity to the element the user would expect.
3. Flag: lookalike pairs (similar icons or labels, different functions); elements styled as interactive that are not; options presented as available that carry hidden gates (fees, regions, states) revealed only after commitment; CTA text making a specific promise the destination objectively does not keep ("Free Download" leading to payment) — where the destination is verifiable in the artifact, promise-breaking is High confidence-grade.
4. Flag independently: any visible error state or message amounting to "that action is not allowed" — direct High confidence-grade evidence that a wrong path was left open and inviting.
5. Name each flag with the element, the goal it falsely invites, and the actual destination or outcome (G6).

---

### Poor Grouping
*an important relationship between two or more interface elements is unclear.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; conceptual/IA form is cross-screen.*
1. From C2 goals, derive the expected association map: the element relationships the user must read correctly to proceed — label↔control mappings, option↔description pairings, group memberships, menu categorizations — including BOTH which elements SHOULD read as related AND which SHOULD read as unrelated. Steps 2–3 evaluate the design against this map in both directions: a true relationship the design fails to convey (missed association), and a false relationship it does convey (spurious association — the butterfly ballot's direction). A design where unrelated things also group has failed even if all related things group.
2. Evaluate the map against the FULL set of established Gestalt grouping principles, by name, including at minimum: proximity (related elements closer to each other than to competitors — the most commonly violated); similarity (same-function elements share visual properties; different-function elements don't mimic each other); common region (elements sharing a container read as related — flag unrelated elements in one container and related elements split across containers); uniform connectedness (elements joined by explicit connectors or sharing dividers read as related — misplaced dividers split siblings and weld strangers); continuity (alignment implies reading order); closure (implied containment reads as grouping); figure-ground (interactive elements read as figure). Common fate requires motion artifacts — declare on statics. Equidistance or nearer-to-unrelated = strongest flag. Flag violations in both directions per the step-1 map.
2b. Semantic grouping (independent axis): for every NAMED group — menu categories, tab sets, section headings, settings clusters — assess (i) internal coherence: do all members plausibly belong under the label as the C1 population reads it; (ii) assignment ambiguity: could a member reasonably be sought under a different existing category; (iii) label↔member fit: does the group name predict its contents. Flag semantic misgrouping even where visual grouping is flawless — perceptual and semantic grouping fail independently (the IA form; cross-screen unit).
3. Flag: controls equidistant between two plausible referents; labels nearer an unrelated element than their referent; conflicting Gestalt cues (proximity says one grouping, similarity another); IA form — menu items whose category membership a user could reasonably assign elsewhere.
4. Name the elements, the ambiguous relationship, AND the specific Gestalt principle violated per flag (G6) — a Poor Grouping flag that cannot cite a principle is not a flag; expected vs. actual grouping must both be stated.

---

### Forced Syntax
*a sequence of actions cannot be completed in the order or manner the user expects or prefers.*

**Detection procedure (pass one — flag, do not filter).** *Unit: sub-pattern B per-screen; sub-pattern A cross-screen (flow-level by nature).*
- Sub-pattern B (any artifact): (1) enumerate every free-input field; (2) record format signals — input masks, placeholder text prescribing an exact format, format-error messaging, character restrictions; (3) flag any field demanding a single encoding of information that has multiple common unambiguous encodings; name the field and the excluded encodings.
- Sub-pattern A (flow, prototype, live, or code artifacts): (1) state the task goal; enumerate the reasonable constructions (object→action, action→object, distinct entry points users would plausibly try); (2) walk the flow attempting each; record whether an entry point exists for it; (3) flag when exactly one construction is honored and at least one alternative is reasonably likely for this population.
- Sub-pattern A (static screenshot): flag as risk-only when a single rigid entry point is visible; label "needs flow or code to confirm alternative constructions."

---

### Memory Challenge
*the user is required to remember information that is easy to forget.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature; per-screen for recall-without-cue fields.*
1. Walk each task flow; at every step, list what the user must hold in mind to proceed, retrieve from memory without a cue, or execute from memorized instructions.
2. Flag every context-boundary carry: information shown on one screen and needed on another (or another session/device) without being re-presented.
3. Flag recall-without-cue demands: fields requiring memorized identifiers, security answers without the question shown, command vocabularies with no visible reference (voice command lists are the canonical case).
4. Flag instruction sequences the user cannot keep visible while executing them.

---

### Feedback Failure
*the system fails to communicate the consequence of the user's actions, or how to resolve a failed action.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen — audits action→response pairs.*
1. Enumerate every user action in scope (taps, submissions, commands, toggles).
2. For each, record the system's response: what changes, where, when, and does it state what happened and — on failure — what to do now?
3. Flag: actions with no perceivable response; error messages that fail either question ("what went wrong?" / "what should I do?") — auditable without any user testing; feedback arriving after the user would have moved on; post-submission validation where continuous validation is feasible.
   *In-screen vs. post-action rule (partial artifacts):* feedback that should appear on the same screen immediately (button state, inline validation, loading indicator) is High confidence absent if not visible there; feedback that would arrive on a subsequent screen (toast, confirmation page) must NOT be asserted absent from a partial artifact — use conditional language ("if no confirmation exists elsewhere in this flow, users would have no indication the action completed") and route to the closer-look bucket per G8.
   Feedback scope includes surfacing hazards and consequential states the user needs to know about, not only confirming intended actions.
4. Route each flag to its candidate root cause per the Boundary list, as input to pass two.

---

### Physical Challenge
*some aspect of the system causes physical discomfort or makes it physically difficult or impossible to complete actions.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for measurables; whole-artifact for form-factor properties.*
1. Flag any interactive target that appears small or crowded relative to whatever scale can be inferred from the artifact (standard platform elements, surrounding text, sibling controls). Physical size is not derivable from uncalibrated pixels, so apparent smallness is flagged conditionally, never measured (calibration-gated ceilings rule); where calibration IS provided, measure. The applicable standard is set by the input modality asserted in C3 — touch (~12 mm finger pad / platform minimums), mouse or other pointer (platform pointer minimums), remote, stylus, etc.; modality unstated: apply the declared C3 default and say so. Also flag tight spacing, and targets in hard-reach zones given the asserted C3 posture and grip (e.g., one-handed phone use — thumb-zone maps).
2. Measure text contrast against WCAG ratios and size against platform minimums at expected viewing distance; flag failures.
3. Enumerate channel demands and check each against C3: audio-dependent elements (flag if hearing may be unavailable), speech-required interactions (flag against speech/privacy constraints), two-handed or precision gestures (flag against hands/mobility), sustained-attention visuals (flag against motion).
4. Note form-factor properties not assessable from the artifact (weight, thermals, VR comfort) for the coverage notes rather than guessing.

---

### Accidental Activation
*it's easy for the user to unintentionally trigger an action during normal use.*

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact; requires device/form-factor context.*
1. Map controls against natural grip points, resting zones, and edge/corner contact areas for the device class; flag consequential controls located there.
2. Flag overloaded activations (double-tap, press-and-hold on grip surfaces), edge gestures adjacent to system gestures, and passive/sensor-based activations (proximity, motion, always-listening) — the last as candidates for Bad Prediction routing.
3. Flag hover-activated controls (menus, previews, tooltips-with-side-effects) positioned across common pointer paths — hover engagement during ordinary cursor travel is a static-detectable desktop case of this Trap.
4. For each flag, record the triggered action's consequence and reversibility (feeds severity).

---

### Slow or No Response
*the actual or perceived time the system takes to respond exceeds what the user wants or expects.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-interaction; live artifacts strongly preferred.*
1. For live/instrumented artifacts: measure response times per significant interaction; flag every threshold violation by interaction type.
2. For all artifacts: audit wait-state design — flag any operation >1 s without continuous progress feedback; any >10 s with no occupied-time treatment (skeleton screens, background continuation); progress indicators that jump discretely or stall.
3. For static artifacts: response times are not assessable — declare; wait-state *design* (presence/quality of progress feedback in mocked states) remains flaggable. Scoped coverage (always emitted on statics, J27): "Slow or No Response — wait-state design; not from this artifact: actual response times — live session or screen recording would settle."

---

### Captive Wait
*the system does not allow the user to advance or back out of a process at a time of their choosing.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flow states).*
1. Walk every flow; at each state, test: can the user advance at will? back out? skip? Flag every state where all three fail.
2. Flag auto-advancing/auto-dismissing screens that deny reading-pace control.
3. For each flag, record: duration, disclosure of duration, skip affordance and when it appears, and whether the captive content serves the user's goal or the business's.
4. Attend especially to onboarding, setup, updates, and ad placements.

---

### Unnecessary Step(s)
*the number of steps required to achieve a goal is greater than it needs to be.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows).*
1. Walk each C2 task flow end to end; count steps; for each ask: eliminable? automatable? combinable?
2. Flag: confirmation dialogs (check reversibility of the confirmed action — reversible = automatic flag); per-field confirmations; navigation depth (levels descended to reach frequent functions — hamburger-nested high-frequency actions are the canonical case); re-entry of derivable information; round-trips between choice and outcome views (missing previews).
3. Flag forced prerequisite gates: the artifact shows users must complete a prerequisite (authentication, registration, paywall, mandatory consent) before reaching core functionality, AND either (a) the core function does not technically require it, or (b) a guest/unauthenticated path would reasonably serve the stated goal. Do NOT classify a gated path as Invisible Element — the path is blocked, not hidden.

---

### Information Overload
*information presented is understandable but there's more of it than there needs to be.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; menus/IA cross-screen.*
1. From the C2 goal, partition each screen's content: serves the likely goal now / secondary / serves no evident user goal.
2. Flag screens where the primary task requires processing only a small subset of what's displayed; count elements, options per decision point, and word counts of instructions/labels/errors against a plain-necessity read.
3. Flag verbosity per text element: could it shed half its words without losing clarity (the Krug test)?
4. Strongest static trigger — task burial: the primary action or call-to-action is buried within or beneath large text masses, or is not reachable without scrolling past content that does not serve the goal. Task burial is this Trap's clearest screenshot-grade evidence.
5. Homepages, dashboards, and navigation earn the closest read — accretion concentrates there.

---

### System Amnesia
*the system fails to take advantage of the user's prior work, preferences, or context.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-session by nature.*
1. Inventory every point where the user supplies information or exhibits trackable behavior; then flag every later point that requests or ignores the same thing: repeated form fields, criteria re-stated, ownership-blind promotions, context dropped across sessions.
2. Strongest flag — self-evidencing amnesia: the system *displays* information while simultaneously requesting it, or comments on an action in a way proving it didn't register it (selling the user what the same screen shows they own; a machine asking if you knew it takes credit cards while processing your credit card).
3. Live/multi-session artifacts: probe cross-session recall (resume point, preferences, exclusions).

---

### Incorrect Information
*information presented is factually wrong, distorted, incomplete, out-of-date, or contains errors.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + cross-screen consistency.*
1. **Internal-contradiction sweep (strongest artifact-native check):** totals vs. their line items; labels vs. adjacent charts/data; counts vs. visible items; instructions referencing elements/pages that don't exist in the artifact; cross-screen statements that conflict.
2. Staleness sweep: dates, prices, version references, "current" claims with no freshness mechanism; flag time-sensitive content lacking one.
3. Provenance sweep: AI-generated or algorithmic content presented as fact without labeling, attribution, or uncertainty indicators — flag structurally regardless of truth value.
4. External-fact spot checks only where verifiable against authoritative sources within the analysis; otherwise record as not-assessable rather than guessing.

---

### Bad Prediction
*the system fails in its attempt to anticipate the user's intent, preference, or context; it guesses wrong.*

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact feature inventory.*
1. Inventory every predictive/proactive feature: autocomplete/correct, recommendations, auto-actions, sensor-triggered behaviors, "helpful" interjections.
2. For each, record: does it *act* or *suggest*? Is a wrong guess dismissible at near-zero cost, or does it require undoing? Is the acted-upon outcome reversible? What signals feed it (rich context vs. ambiguous single sensor)?
3. Flag structurally (no accuracy data needed): any feature that ACTS on a prediction whose wrong outcome is irreversible or privacy/safety-relevant — the acting-threshold is unmet regardless of hit rate; any prediction requiring meaningful effort to dismiss or undo.
4. When user context (C1/C2) is stated: flag surfaced content, recommendations, or defaults that visibly contradict the stated user's demographics, goals, or tasks — this is static-screenshot detectable, and objective contradictions reach High confidence without usage data.
5. Flag proactively surfaced content that occludes content the user is actively attending to (hover covers, overlay suggestions) — the system's guess about what helps is overriding what the user chose to attend to.
6. With usage/observation data: flag features whose correction cost exceeds their saving.

---

### Irreversible Action
*the user cannot backtrack or undo an action they have taken, though recovery is possible but unsupported.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows/code).*
1. Walk every consequential action in scope; for each ask: is there undo? a recovery window? a back path that truly restores prior state?
2. Flag every consequential action with none of the three; record what guards it instead (nothing / standard dialog / non-habituating confirmation).
3. Flag commitment-understating labels on irreversible actions (Reserve→Purchase) as co-candidates for Inviting Dead End.
4. Flag existing confirmation dialogs for the reversibility-instead question (feeds Unnecessary Step(s)).

---

### Unwanted Disclosure
*the system exposes personal data or behavior in a way that is harmful, embarrassing, or unexpected.*

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact + settings audit.*
1. Trace every feature that collects, stores, or surfaces user data; for each flow ask: would the user expect this destination, given where they shared it?
2. Audit defaults: flag every opt-out (rather than opt-in) sharing default, with sensitivity class (location, health, finance, behavior = highest).
3. Physical-dimension sweep against C3: flag audio announcements of content, always-visible sensitive surfaces on shared/ambient devices, unsilenceable sounds — any output the user cannot gate in social contexts.
4. Flag exports, saves, and shares that bundle more than users would expect — e.g., a saved meeting chat log that silently includes private messages; the expectation is set by what the user thinks they are sharing, not by what the feature technically captures.
5. Flag consent asked at moments the user can't understand what they're consenting to.

---

### Data Loss
*the system fails to retain information or content the user expects to be preserved.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen + failure-mode analysis.*
1. Identify every point where the user creates or modifies data; for each run the failure-mode battery: session timeout? crash/shutdown? navigation away? network drop? concurrent edit?
2. Flag every point where any answer is "it could be lost": absent auto-save, unpreserved partial entries, last-write-wins co-authoring, dismiss-to-void inputs (comment boxes that vanish on outside-click), transient content users would expect durable (meeting chat logs).
3. Live artifacts: simulate the failure modes where safe; design files: flag structurally and mark simulation-needed.

---

### Gratuitous Redundancy
*multiple separate elements at the same level serve the same function (destination, action, or information), whether visually identical or not.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen, plus cross-screen grouping for multi-screen artifacts.*
1. Enumerate every interactive and informational element on the screen or level under review — links, buttons, icons, menu items, status indicators — recording each element's apparent function from label, icon, placement, and context.
2. Group by function — apparent destination, triggered action, or information conveyed — ignoring visual appearance. For informational elements, group by the state or fact communicated.
3. Flag any group of two or more at the same or directly nested level; record the count and every instance's location.
4. Confirm functional equivalence where the artifact allows: traverse the prototype or live site; audit link targets and handlers in code; for indicators, confirm they reflect the same state variable.
5. Cross-screen (multi-screen artifacts only): group functions across screens within the same navigation level; persistent chrome counts once — flag only additional elements duplicating what it already provides.
6. Conventional-pair guard — do not silently exempt "standard patterns"; these are candidates like any others: site logo navigating to homepage alongside a separate Home link; a search input field alongside a standalone search icon triggering the same search; multiple Sign In / Get Started buttons for the same action; the same destination in two or more nav regions on one screen. Convention may inform severity; it does not disconfirm presence.
7. Routing fork on identical-looking elements: if the functional-equivalence check (step 4) shows identical-looking elements with the SAME function → this Trap; with DIFFERENT functions → route to Inviting Dead End (a lookalike inviting the wrong choice) and, where the same element type behaves differently across contexts, Variable Outcome — per those Traps' boundaries.
8. Name every candidate concretely ("six elements on Home appear to lead to Find a Location"); never flag on a general impression of clutter (G6).

9. Enumerate visible duplication on the screen: elements sharing an exact label, sharing an icon, or presenting the same evident function (two search ingresses, two orientation anchors). Flag every pair or group; on static artifacts, flag on appearance — target verification is adjudication's concern, not detection's (author-ruled 2026-07-06). Elements positioned in navigation chrome are treated as interactive by default — a clickable branded wordmark or nav link is a navigation control regardless of branding appearance; the informational-label exemption applies only to plainly non-interactive text.

---

### Variable Outcome
*the system responds differently and unexpectedly to the same user action at different times.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-state; code is the native artifact.*
1. Code artifacts: sweep for state-handlers — any place one user action routes to different outcomes by system state; each is a candidate.
2. Flow/live artifacts: for each control, probe across contexts/states — same action, same result? Flag every divergence.
3. For each candidate, locate the state signal: does one exist? where, relative to the user's attentional focus at the action moment (feeds EIE/IE routing)? Is the state user-sustained (quasi-mode)?
4. Flag inconsistently supported functions (same element type responding differently across instances) — the modeless form; static screenshots cannot detect this Trap — declare.

---

### Wandering Element
*the same interface element is presented in a different location at different times.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature — this Trap does not exist in a single screenshot; declare on single-screen artifacts.*
1. Identify recurring elements across the screens in scope; prioritize high-frequency controls — search, navigation, editing, confirmation — where spatial memory pays most.
2. Map each recurring element's position per context (coordinates/regions in design files make this directly auditable).
3. Flag every placement inconsistency, recording the contexts and displacement; note ecosystem-level wandering (the same platform control placed differently across an app family).

---

### Inconsistent Appearance
*the same interface element is presented in a different style at different times or in different places.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature; declare on single-screen artifacts.*
1. Identify recurring functions across screens in scope; prioritize core actions — New, Delete, Edit, Share, Search — and recurring status vocabulary.
2. For each, collect every visual/auditory representation across contexts; flag any function with more than one form (icon variants, icon-in-one-place-word-in-another, mixed design languages, legacy/current coexistence).
3. Record whether variation is systematic (design-language boundary) or scattered (drift) — informs remediation.

---

### Ambiguous Home
*the interface presents multiple, competing locations for getting oriented and initiating tasks.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/whole-IA.*
1. Identify every element or location that could plausibly be read as a starting point / orientation anchor (landing screens, dashboards, home-labeled or home-iconed destinations, launcher surfaces). More than one candidate = flag.
2. Audit the return-home action from every context: same action everywhere? single-step everywhere? Flag inconsistencies and multi-step returns.
3. Flag home iconography attached to non-home destinations (routes to Inviting Dead End co-listing).
4. Multi-platform/multi-mode products: compare home conventions across modes (the Windows 8 two-homes case).

---

### Poor Aesthetic
*the system's sensory design, style, personality, or tone is judged unpleasing, inappropriate, or inauthentic by its intended users.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + whole-product coherence.*
1. Run the principle audit: alignment grid violations, hierarchy collapse (no clear reading order), typography inconsistency, color-system violations, contrast failures — each flagged with its routing Trap where one exists.
2. Flag tone/personality mismatches observable in copy and sound (celebratory intonation on sad content; sycophantic assistant register) as designer-referral observations.
3. Compile the cross-Tenet foundation summary: aesthetic experience is capped by the product's worst functional failures.
4. Cumulative-risk observation (author-ratified; emit through Worth a closer look — it passes all three gates by construction: pivotal, worst branch ≥ Medium, named check = exposure-aware perception testing with the intended population, cost stated): when three or more measurable principle violations or functional Traps co-occur on one screen, add an observation (not a verdict) that the accumulation itself signals design-investment risk — aesthetic failures are cumulative, and the combined effect reads as overall quality failure to users.

---
