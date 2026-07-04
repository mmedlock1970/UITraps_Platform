# UI Tenets & Traps — Analyzer Knowledge Base — v2.1 (manuscript-content lineage; successor to deployed v2.0; full 27-trap coverage)

*v2.1 incorporates the salvage audit of the deployed v2.0 KB: rules that passed the salvage test (imperative, condition-named, pass-assigned) are integrated below; v2-sourced additions pending author sign-off are listed in Open Items.*

**Chunk grades.** Seven chunks are pilot-grade (deep-reviewed with the framework author): Effectively Invisible Element, Uncomprehended Element, Inviting Dead End, Forced Syntax, Gratuitous Redundancy, Incorrect Information, Physical Challenge. The remaining twenty are draft-grade: extracted from the manuscript with authoring judgment marked inline as **[JUDGMENT]** wherever content goes beyond what the manuscript states. Review draft-grade chunks flag-first.

---

## GLOBAL RULES (apply to every analysis, both passes)

**G1. Exact trap names.** Use full, exact Trap names; several Traps have near-identical names that denote different problems.

**G2. Two-pass discipline, with selective loading.**
- **Pass one (detection):** load only the Detection Procedures for all 27 Traps, plus the Context Intake Schema. Run each procedure. Flag every candidate. Do not filter, do not weigh disconfirmation, do not assign severity. Over-reporting at this stage is correct behavior.
- **Pass two (adjudication):** load the full chunks for candidate Traps only, plus the Taxonomy Index (so adjudication can re-route a finding to a non-candidate Trap when a Boundary clause points there). For each candidate, apply in order: (1) Boundary and Disconfirmation; (2) the one-problem-one-issue procedure (G3); (3) the Assessability lookup (G4/G5); (4) Severity and Confidence; (5) assemble the issue per G8. Kill, merge, and relabel freely — that is this pass's job.

**G3. One problem, one issue — evidenced diagnosis.** When multiple candidate flags point at the same underlying design element or decision, report ONE issue. At the bottom of each issue, list the Traps that align to that issue — each listed Trap must independently meet its own evidence bar (no tag-cloud padding; nothing evidenced omitted). Then apply the root-cause rule:
- **Fix-based root cause:** the root cause is the Trap whose remediation resolves the other listed Traps. Designate it "(root cause)" and mark the others "(consequence)." Worked example: an element noticed slowly *because it moves between screens* — pinning it to one location (Wandering Element's fix) dissolves the noticing problem, so Wandering Element is root cause and the delayed noticing is referenced in the explanation, not separately reported.
- **Bidirectional fixes:** when fixing either Trap would resolve both, fall back to mechanism order — the Trap upstream in the causal chain is root cause.
- **Root cause unclear:** designate no root cause; state "root cause unclear" AND name the specific check that would settle it. "Unclear" without a named check is unfinished adjudication.
- **Segment-conditional:** when which Trap applies depends on who the user is (see the Uncomprehended Element / Inviting Dead End sibling definition), list both, each tagged with its segment.
- **Manifests-as:** when one underlying property produces different Traps at different moments for the same user population and the fix converges (e.g., an unfamiliar goal-critical element that some users filter [Effectively Invisible Element] and others notice but can't decode [Uncomprehended Element]), report one issue: "manifests as X or Y — same root property, same fix." Do not phrase this as X→Y causation: for the non-noticing user, the noticed-element Trap never occurred.

**G4. Absent vs. unassessable is a lookup, not a judgment — on two axes.** Assessability is a function of the Trap, the artifact evidence, and the context evidence. Before analysis: (a) classify the artifact type (static screenshot / disconnected screens / wired prototype or flow / live product / code); (b) inventory the user context provided against the Context Intake Schema. Consult each Trap's Assessability & Confidence section on both axes. Three finding labels, never interchangeable:
- "Not assessable from this artifact — [what artifact would settle it]"
- "Not assessable without user context — [what context field would settle it]"
- "Not present" — requires that the artifact CAN show the Trap, required context is available or a declared default covers it, the Detection Procedure ran, and no candidate survived (or disconfirmation positively ruled it out — state which).

**G5. Context softens or gates.** Each Trap's Assessability & Confidence section states what missing context does per schema field:
- Where context *sharpens* calibration: assess anyway, label "Provisional — assumes [stated assumption]," name what would sharpen it.
- Where context *gates* assessment: do not guess — emit the "not assessable without user context" label, unless the Trap's profile declares a permitted default for that field, in which case assess against the default and declare it.

**G6. Named evidence.** Every flag, in either pass, must cite the specific element(s) and condition(s) that triggered it. General impressions ("feels cluttered," "low prominence") are not findings.

**G7. Unit of analysis.** Detection Procedures declare their unit: per-screen, cross-screen, or both. For multi-screen artifacts: run per-screen steps on every screen in scope; run cross-screen steps where declared; compute flow-level properties (dominant interaction patterns, persistent elements) across the whole flow before consulting them in per-screen judgments — a single screen misestimates them. Every finding cites the screen(s) where its evidence sits.

**G8. Report architecture — issues first.** The evaluator's goal is not to find and name Traps per se; it is to find and fix user-impacting issues. The Trap vocabulary rides on issues as diagnosis and shared team language. Reports have three sections:

1. **Issues.** One block per adjudicated issue: *what is happening to the user and where* (named elements, plain language, standing on its own without framework knowledge) → *Severity* (ladder + escalators) → *Confidence* (Confirmed / Probable / Flagged, with the promotion path when not Confirmed) → *the fix* → closing **trap line**: the Traps aligned to this issue, root cause called out when clear, per G3 patterns. Order issues by severity, worst branch first.
2. **Worth a closer look.** For elements whose bearing on the stated goals cannot be determined from the artifact but is pivotal if real. Entry format: *element — why it matters given the stated goal — the check (with its cost: one click / five-user test / code audit) — the implication, compactly both ways.* Entry ticket: the unknown must be pivotal to a stated C2 goal AND the worst branch must clear Medium severity AND a specific nameable check must exist. Note that the "if not" branch is often itself a live Trap (e.g., if the ambiguous element is NOT the ingress to the goal, nothing on screen may communicate the goal path at all — Invisible Element); reason it through. Batch all checks into a closing verification checklist.
3. **Coverage notes.** Compressed G4 outputs: Traps assessed and not present (with the condition that ruled them out), and Traps not assessable (with what would settle them).

**Anti-hedging edge (both directions):** a finding whose evidence clears its Trap's confidence bar MUST be reported as an issue, even where a check could add certainty — the bucket is for genuine pivotal unknowns, not for discomfort. An "I'm not sure" without a nameable check is not a bucket entry; it is unfinished adjudication. An optional whole-report Trap summary may be generated as an appendix view over the issues; it is never the primary structure.

---

## SEVERITY & CONFIDENCE (replaces per-Trap consequence/likelihood/combination blocks)

**Severity ladder** — the worst plausible outcome for the stated goals (C2) under the stated context (C3), per affected user. One axis:
- **Critical** — irreversible harm: data loss, unwanted disclosure, physical harm or safety risk, unrecoverable cost.
- **High** — task failure or abandonment with no discoverable recovery.
- **Medium** — recoverable failure, or recurring friction.
- **Low** — one-time friction, delay, polish.

**Escalators:**
- **Repetition (C4):** friction on a task performed daily escalates one level; friction on a once-per-lifetime setup task does not. Habituating-tenet Traps scale with repetition by nature.
- **Context (C3):** occupied channels, divided attention, motion, or time pressure can convert "recoverable" to "unrecoverable in practice" (a fumbled interaction while driving is not Medium).

Reach is not estimated. Findings are population-conditional via C1: a finding means "this population hits this." Severity is per-affected-user; priority (severity × reach × strategy) is the team's call, not the analyzer's.

**Confidence scale** — how sure the analyzer is that the problem is real, per finding:
- **Confirmed** — direct evidence in hand (e.g., a "not allowed" error message; audited duplicate link targets; a visible input mask; measured contrast below standard).
- **Probable** — risk conditions present, disconfirmation checked and cleared, but the confirming method is not accessible from this artifact or context.
- **Flagged** — conditions partially present, or the judgment leans on a declared default rather than provided context.

Each Trap's Assessability & Confidence section sets the **ceiling** (a Trap that requires user knowledge, analyzed from a bare screenshot, cannot exceed Probable regardless of how loud the risk conditions are). Every non-Confirmed finding names its **promotion path**: the specific step that would confirm or dismiss it, with its cost.

---

## CONTEXT INTAKE SCHEMA (canonical — all Trap gates and defaults reference these fields)

**C1. User Knowledge.** Products and conventions the users have already internalized; domain expertise; novice/expert mix; prior exposure to this product's own conventions. *Default when absent:* general adult population familiar with mainstream web/mobile conventions — declare it. Brand-specific, domain-insider, and novel elements cannot be cleared under the default.

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

## TAXONOMY INDEX (all 27 Traps — pass-two routing reference)

**UNDERSTANDABLE** (It makes clear what I can do)
- **Invisible Element** — no label, icon, or other interface element is provided to let the user know how to achieve a goal, and the user lacks the prior learning needed to overcome its absence.
- **Effectively Invisible Element** — an element goes unnoticed because it is unexpected or misaligned with the user's focus of attention.
- **Distraction** — something in the interface draws the user's attention away from their current goal.
- **Uncomprehended Element** — an element is noticed, but its meaning or required method of interaction is unclear.
- **Inviting Dead End** — an element is incorrectly judged to be a means of achieving a goal; it looks right but is wrong.
- **Poor Grouping** — an important relationship between two or more interface elements is unclear.
- **Forced Syntax** — a sequence of actions cannot be completed in the order or manner the user expects or prefers.
- **Memory Challenge** — the user is required to remember information that is easy to forget.
- **Feedback Failure** — the system fails to communicate the consequence of the user's actions, or how to resolve a failed action.

**COMFORTABLE** (It's physically effortless to use)
- **Physical Challenge** — some aspect of the system causes physical discomfort or makes it physically difficult or impossible to complete actions.
- **Accidental Activation** — it's easy for the user to unintentionally trigger an action during normal use.

**RESPONSIVE** (It never makes me wait)
- **Slow or No Response** — the actual or perceived time the system takes to respond exceeds what the user wants or expects.
- **Captive Wait** — the system does not allow the user to advance or back out of a process at a time of their choosing.

**EFFICIENT** (It minimizes how much I must do)
- **Unnecessary Step(s)** — the number of steps required to achieve a goal is greater than it needs to be.
- **Information Overload** — information presented is understandable but there's more of it than there needs to be.
- **System Amnesia** — the system fails to take advantage of the user's prior work, preferences, or context.

**ACCURATE** (It's factual and relevant)
- **Incorrect Information** — information presented is factually wrong, distorted, incomplete, out-of-date, or contains errors.
- **Bad Prediction** — the system fails in its attempt to anticipate the user's intent, preference, or context; it guesses wrong.

**PROTECTIVE** (It gives me control over my actions and data)
- **Irreversible Action** — the user cannot backtrack or undo an action they have taken, though recovery is possible but unsupported.
- **Unwanted Disclosure** — the system exposes personal data or behavior in a way that is harmful, embarrassing, or unexpected.
- **Data Loss** — the system fails to retain information or content the user expects to be preserved.

**HABITUATING** (It becomes automatic to use over time)
- **Gratuitous Redundancy** — multiple separate elements at the same level serve the same function (destination, action, or information), whether visually identical or not.
- **Variable Outcome** — the system responds differently and unexpectedly to the same user action at different times.
- **Wandering Element** — the same interface element is presented in a different location at different times.
- **Inconsistent Appearance** — the same interface element is presented in a different style at different times.
- **Ambiguous Home** — the interface presents multiple, competing locations for getting oriented and initiating tasks.

**BEAUTIFUL** (It's aesthetically appealing)
- **Poor Aesthetic** — the system's sensory design, style, personality, or tone is judged unpleasing, inappropriate, or inauthentic by its intended users.

**Sibling Traps (reserved term):** Uncomprehended Element and Inviting Dead End are siblings — the same element can present either Trap, with which one applying depending on the user's prior experience: a user who has never seen the element forms no interpretation (Uncomprehended Element); a user who knows it from elsewhere, applied to a different function, forms a confident wrong one (Inviting Dead End). No other Trap pair is termed "sibling."

---
## TRAP CHUNKS — UNDERSTANDABLE

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

---

### TRAP: EFFECTIVELY INVISIBLE ELEMENT *(pilot-grade)*
*Sub-tenet: Noticeable*

**Definition.** An element that is present and perceivable, but that users fail to notice — because it sits outside their attentional focus for the task, **or because it is presented in an unexpected way, regardless of its location**. Applies to visual, auditory, and tactile elements.

**Boundary.**
- IS: a perceivable element likely to go unregistered given where the user's attention falls during the task, or given what they are looking for. **Central placement and high salience do not disconfirm this Trap; expectation mismatch renders elements unnoticed independent of position (goal-driven filtering — the brain passes signals matching the user's search template and suppresses the rest).**
- IS NOT **Invisible Element**: there, no perceivable element exists at all. Tie-breaker: an element exists but is likely missed → here; no element exists → there.
- IS NOT **Distraction**: that Trap is attention wrongly captured; this one is attention never captured (mirror images).
- IS NOT **Wandering Element**: if the element would be noticed at a stable location and the noticing failure stems from its moving between screens or states, Wandering Element is the root cause (fix-based rule) — flag it there and reference the delayed noticing in the explanation.
- IS NOT **Inconsistent Appearance**: if the noticing/recognition failure stems from the same element being restyled across contexts, attribute there.
- IS NOT mere small size or subtle styling in the abstract: the test is misalignment with task-driven attention or expectation, not aesthetics.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen, plus cross-screen steps for multi-screen artifacts.*
1. From the stated or assumed user goal, identify the elements on each screen in scope critical to completing it.
2. For each critical element, record: (a) location relative to the likely attentional focus for this task (focus = where the task's primary content or interaction lives, not screen center); (b) whether it differs from surroundings on any pre-attentive feature (color, size, orientation, motion); (c) whether its interaction style matches the flow's dominant interaction pattern (computed per G7); (d) the number of elements competing for attention in its vicinity; (e) **whether the element's appearance matches the visual category users would be searching for, given the goal it serves and their prior experience (C1) — does the thing that does X look like the kind of thing this population expects X to look like?**
3. Flag as candidate any critical element that: is peripheral to the task focus AND lacks pre-attentive distinction; OR deviates from the dominant interaction pattern; OR sits in a high-competition zone; **OR mismatches the user's likely search template for its function — flag regardless of location or visual prominence.**
4. Name the specific condition(s) per flag (G6).
5. Cross-screen (multi-screen artifacts only): flag state or mode indicators that must be noticed on a different screen from where the state was set; flag content that changes between screens in ways the user would not expect (unexpected changes are unlooked-for, hence filtered). Location changes route to Wandering Element; appearance changes route to Inconsistent Appearance (see Boundary).

**Disconfirmation (pass two).** NOT present when: (a) the element is in a location users are habituated to attending from prior product experience (C1) — even if not geometrically central; (b) the element differs from surroundings on a pre-attentive feature causing automatic pop-out AND matches the expected category for its function; (c) the element is consistent with the dominant interaction pattern, so users naturally encounter it in normal task flow.

**Severity.** High when the element is critical-path and fully unnoticed (functionally identical to absence). Delayed noticing is still this Trap; its severity equals the consequence of the delay in the specific task context (a missed mute indicator mid-meeting: High; a slowly-found settings link: Low). Escalators: C3 (divided attention, noise, motion sharply raise miss likelihood); C4 (recurring tasks compound the cost).

**Assessability & Confidence.** Static screenshot: Confirmed ceiling only when the element is measurably far from the primary task area AND critical to task completion; otherwise Probable — promotion path: confirm attentional focus with user observation (usability testing is the gold standard; design review alone cannot reliably confirm or rule this out — curse of knowledge). Context axis: C2 (task goal) softens under its default; C1 gates disconfirmation (a) only — absent C1, candidates cannot be cleared on habituation grounds and stay flagged; C3 modifies likelihood globally (its default makes findings a lower bound).

**Attribution.**
- Variable Outcome: an effectively invisible mode indicator is evidence toward Variable Outcome, but outcome variation must be independently confirmed; when confirmed, this Trap is typically root cause (fixing the indicator's noticeability resolves the outcome surprise).
- Information Overload: if the noticing failure dissolves by removing surrounding excess, Information Overload is the root cause (fix-based rule) — the manuscript states reducing it is often the remedy.
- Distraction: if motion was added to remedy this Trap, independently confirm the motion now captures attention away from the current goal before also flagging Distraction.
- Gratuitous Redundancy: if the element was *duplicated* to remedy this Trap, evaluate the duplicates under Gratuitous Redundancy — duplication is not an endorsed remedy (see Remediation).
- Two-gate interaction with Uncomprehended Element: an unfamiliar goal-critical element can fail pre-attentively (filtered — this Trap) or post-attentively (noticed but undecodable — Uncomprehended Element). Same root property; when the fix converges (a familiar, recognizable element), report one issue using the manifests-as pattern (G3). Live user observation distinguishes the gates (a fixation that never lands vs. a puzzled hover) — needed only if the team wants to size the noticing problem independently.

**Report fragments.** Finding: "An element critical to [goal] is present but likely to go unnoticed: [element], because [named condition — peripheral to task focus / pattern deviation / attention competition / expectation mismatch]." Why it matters: "Users who miss this element cannot proceed — functionally identical to the element being absent."

**Remediation.**
- Place the element within or adjacent to the user's primary attentional focus during the task in which it matters, and render it in the visual category users expect for its function.
- Or make one instance globally perceivable: whole-screen state changes (tint shift, screen-edge pulse) or attention-following placement — techniques that reach the user wherever their focal spotlight sits.
- Exploit pre-attentive features (color, size, orientation, motion) for pop-out. Caution: motion applied to elements not relevant to the current goal becomes a Distraction Trap.
- **Do not remedy by duplicating the element.** The focal area of human vision is tiny and constantly moving; duplicating indicators to "cover" attention produces indicator proliferation and a Gratuitous Redundancy Trap. One element, made unmissable, beats many competing for notice.

---

### TRAP: DISTRACTION *(draft-grade)*
*Sub-tenet: Noticeable*

**Definition.** Something in the interface draws the user's attention away from their current goal. The mirror image of Effectively Invisible Element: every attribute that makes something noticeable (color, motion, sound, sudden appearance, spatial position) can direct attention appropriately or hijack it. Forms: pop-up notifications, auto-playing audio/video, animated ads, attention-demanding chrome; also mere presence of certain information (a visible phone, a persistent badge), and mode-of-interaction distraction (voice interaction consumes the same cognitive resources as internal verbal thought — issuing a voice command mid-thought breaks the thought; a practiced physical action does not).

**Boundary.** IS: unsolicited exogenous attention capture away from the user's goal. IS NOT present when the user initiated it, when it is directly relevant to the current goal (a status update during an active process), when no focused goal exists to disrupt (passive browsing), or when the user would judge the interruption justified (an emergency call). IS NOT Information Overload: excess information slowing processing is that Trap; specific elements capturing attention is this one — the line is blurry and the fix is shared (remove what isn't relevant to the goal), so when both flags fire on the same material, report one issue and evidence each Trap independently. Bad-faith exploitation (engagement-driven autoplay, attention-hijacking ads) should additionally be flagged as a potential dark pattern.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; cross-screen for elements that appear during flows.*
1. Enumerate every element that moves, animates, auto-plays, sounds, appears without user initiation, or changes state on its own; plus persistent attention-pulling elements (badges, blinking indicators) **[JUDGMENT: and, in flow artifacts, interstitials/notifications injected mid-task]**.
2. For each, record: user-initiated? relevant to the C2 goal at that moment? modality (motion and peripheral motion are un-ignorable — the orienting response is involuntary)?
3. Flag every uninitiated, goal-irrelevant attention-capturing element; flag cumulative competition (many simultaneous attention-demanding elements — the Boeing 737 pattern) as its own candidate.

**Disconfirmation (pass two).** NOT present when: (a) directly relevant to the current goal; (b) passive/exploratory context with no focused goal; (c) user-initiated; (d) the user would agree the interruption was justified by its importance.

**Severity.** Do not default to Medium — calibrate to what the capture costs given what the user is doing: a static badge or counter in a casual browsing context is Low; motion or audio during a focused transactional task (checkout, form, search) is Medium; High when critical information is missed or obscured (notification over driving directions); Critical in safety contexts (competing cockpit warnings). Escalators: C3 (a distraction during divided-attention or safety-relevant contexts escalates); C4 (recurring interruptions in a core loop compound).

**Assessability & Confidence.** Auto-play audio/video during documented task flows: Confirmed ceiling from artifact. Otherwise Probable — whether capture harms depends on task context (C2 gates: what is the user trying to do when this fires?). Static screenshots under-detect this Trap (motion/sound invisible); declare the limitation. Context axis: C2 gates goal-relevance judgments; C3 sharpens severity.

**Attribution.** If motion was added as a remedy for an Effectively Invisible Element, confirm the original attention problem independently; remediation must replace, not merely delete (see that Trap). Information Overload: confirm excess volume independently — do not infer overload from one distracting element. Bad Prediction: an irrelevant proactive notification is Bad Prediction root cause with Distraction as consequence (fix-based: improving the prediction/removing the proaction resolves the distraction).

**Report fragments.** Finding: "[Element] draws attention away from [goal] without user initiation, goal relevance, or a justification the user would endorse." Why it matters: "Involuntary attention cannot be suppressed — users will notice this regardless of their efforts to focus."

**Remediation.** The governing question is not "will this be noticed?" but "what will the user be doing when this appears, and what will noticing it cost them?" Remove or defer uninitiated elements during focused execution; evaluate whether each interruption serves the user or the product's engagement metrics. Caution: removing a distraction that compensated for an Effectively Invisible Element requires adding a non-distracting visible solution.

---

### TRAP: UNCOMPREHENDED ELEMENT *(pilot-grade)*
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

**Disconfirmation (pass two).** NOT present when: (a) the element is a widely adopted convention the population is demonstrably familiar with (C1, or the C1 default for universal conventions); (b) a text label compensates for an unclear icon — a label reduces but may not eliminate the Trap when the icon actively contradicts it; (c) effective instruction is delivered at the moment of first encounter.

**Severity.** High when the element is on the critical path — most users choose not to "figure it out"; they abandon. Medium when alternatives exist. Escalators: C4 — one-time tasks (setup, onboarding) make this Trap paramount: every user is a first-timer, forever, and habituation will never rescue it.

**Assessability & Confidence.** Confirmed ceiling from a static artifact for brand symbols used as functional icons with no conventional equivalent and no text label — the risk is high enough on the artifact alone. Otherwise Probable ceiling — comprehension is population-relative; promotion path: show the element to a few target users and ask what it means (cheap; recommend it in reports — there is no excuse for skipping it). Context axis: C1 gates most judgments — the C1 default clears universal conventions only; brand-specific, domain, and novel elements stay flagged under the default. C4 softens: habituated populations lower likelihood.

**Attribution.**
- Inviting Dead End: confirm independently that a specific *incorrect* element is likely to be chosen — not merely that the correct element is unclear. Often co-occur (right path unclear, wrong path compelling), compounding — list both only when both are evidenced.
- Memory Challenge: if users once knew the meaning, the finding moves there — confirm which failure it is.
- Where branding drove the unclear element, name the root cause as over-indexing on differentiation (a design-decision cause, not a separate Trap).

**Report fragments.** Finding: "[Element] is unlikely to be correctly interpreted by users unfamiliar with [product/brand/domain convention], and no standard element or text label clarifies its meaning." Why it matters: "Users who cannot interpret this element cannot determine how to proceed — and most will not work to figure it out."

**Remediation.** Use universally recognized elements for core functions. When in doubt, add a text label — a labeled unclear icon always beats an unlabeled one. For genuinely novel concepts, plan instruction delivered when the user is ready to receive it. Replacing a well-learned brand symbol with a conventional element is almost always the right call for functional elements, even at the cost of brand expression.

---

### TRAP: INVITING DEAD END *(pilot-grade)*
*Sub-tenet: Comprehensible*

**Definition.** An interface element is incorrectly judged to be a means of achieving a goal — it looks right but is wrong. Two recurring forms: (1) lookalike elements — similar icons or labels representing different functions, so the wrong one attracts users pursuing the right one; (2) post-hoc invalidation — the interface presents as valid an option that is rejected only after the user commits (error messages amounting to "the action you just took is not allowed"; options revealed as unavailable, paywalled, or region-blocked only after selection).

**Boundary.**
- IS: an element that is present, compelling, and incorrect for a goal the user plausibly holds — the interface equivalent of a false affordance.
- IS NOT **Uncomprehended Element** (sibling — see Taxonomy Index): there the user forms no interpretation; here a confident wrong one. Each requires its own evidence; segment-conditional listing under mixed populations (G3).
- IS NOT **Accidental Activation**: an Inviting Dead End *lures* action ("I am the right choice"); Accidental Activation *fails to prevent* an action whose risk was never communicated. One invites, the other fails to guard.
- IS NOT **Poor Grouping**: if a *spatial ambiguity* (unclear association between label and control) creates the false path, attribute there; this Trap's mechanism is the element's own semantics or visual similarity.
- IS NOT the root cause when **Incorrect Information** creates it: a mislabeled button or outdated instruction functions as an Inviting Dead End, but Incorrect Information is the root cause — correct the information first; report this Trap as consequence (G3).
- There is NO acceptable instance of post-hoc invalidation: an option that will be refused must communicate its unavailability before the user acts. An error message saying "don't do what you just did" is never the fix — it is the evidence.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for lookalike and hidden-gate flags; cross-screen for path-walking.*
1. Enumerate the goals a user could plausibly bring to each screen in scope — the full C2 set, not only the primary task. An element can be the correct path for one goal and an Inviting Dead End for another.
2. For each goal, walk every plausible path, not just the intended one. At each decision point, list the elements a user unfamiliar with the system might judge the correct next step — weighting visual prominence, label semantics, proximity to the correct path, and similarity to the element the user would expect.
3. Flag: lookalike pairs (similar icons or labels, different functions); elements styled as interactive that are not; options presented as available that carry hidden gates (fees, regions, states) revealed only after commitment; CTA text making a specific promise the destination objectively does not keep ("Free Download" leading to payment) — where the destination is verifiable in the artifact, promise-breaking is Confirmed-grade.
4. Flag independently: any visible error state or message amounting to "that action is not allowed" — direct Confirmed-grade evidence that a wrong path was left open and inviting.
5. Name each flag with the element, the goal it falsely invites, and the actual destination or outcome (G6).

**Disconfirmation (pass two).** NOT present when: (a) no other element could plausibly be mistaken for the correct path to the user's goals (C2); (b) the correct element is visually and semantically distinctive enough from all others that confusion is implausible in this task context.

**Severity.** Medium for recoverable wrong turns (wasted effort, lost confidence); High when users cannot recover to the correct path; escalates when the dead end commits the user (payment, destructive confirmation) before revealing itself. Escalators: C3 — divided attention makes lookalike errors far more likely (the current-floor elevator button); C4 — lookalikes in recurring tasks compound.

**Assessability & Confidence.** A visible "not allowed" error state in the artifact, or such logic in code: Confirmed from the artifact alone. Lookalike pairs and hidden-gate presentations from statics: Probable ceiling (plausibility is population-relative); promotion path: user task observation, or flow/code audit for post-hoc invalidation logic. Context axis: C2 gates breadth — without the full goal set, only primary-task dead ends can be assessed (declare under the C2 default); C1 gates population-specific plausibility; C3 raises likelihood under divided attention.

**Attribution.** Uncomprehended Element: confirm the correct element's meaning is genuinely unclear before also reporting it — a compelling wrong element attracts users even when the right one is clear. Poor Grouping: confirm spatial ambiguity is the mechanism, vs. visual similarity. Incorrect Information: where wrong content creates the false path, it is root cause; this Trap is its consequence. Irreversible Action: a dead end that commits irreversibly is both, with this Trap as the luring cause.

**Report fragments.** Finding: "[Element] is likely to be judged the correct path to [goal] but leads to [actual destination/outcome]." Post-hoc form: "[Option] is presented as available but refused after selection ([error/gate]) — the interface invites an action it will not honor." Why it matters: "Users who follow this path expend effort, lose confidence, and may not recover to the correct path without assistance."

**Remediation.** Walk every plausible path; at each decision point, remove or visually differentiate anything that could be mistaken for the correct next step. For post-hoc invalidation: communicate unavailability before the act — disable, hide, or mark the option; never rely on the error message. For lookalikes: increase differentiation or eliminate the wrong path entirely. When a design needs an explanatory label to stop users from taking the wrong action, the label is evidence of the Trap, not its solution — redesign the elements so the wrong path stops looking right.

---

### TRAP: POOR GROUPING *(draft-grade)*
*Sub-tenet: Comprehensible*

**Definition.** An important relationship between two or more interface elements is unclear. Covers visual/spatial relationships (unclear hierarchy, insufficient white space, ambiguous label-to-control mapping) AND conceptual organization within information architectures — menu hierarchies, navigation structures, content categorization (per the framework author's ruling in the manuscript's PG1).

**Boundary.** IS: a *relationship* failure between elements, where the relationship is critical to the user's goal. IS NOT about individual elements' meaning (Uncomprehended Element) or noticeability. IS NOT present when apparent groupings are functionally correct, when the relationship isn't goal-critical, or when a stronger cue (explicit labels, connecting lines, consistent treatment) overrides ambiguous proximity. When grouping ambiguity causes a specific wrong control to be chosen confidently, evaluate Inviting Dead End as co-occurring — this Trap is the root cause when fixing the spatial relationship dissolves the false invitation (fix-based rule).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; conceptual/IA form is cross-screen.*
1. From C2 goals, identify the element relationships the user must read correctly to proceed: label↔control mappings, option↔description pairings, group memberships, menu categorizations.
2. For each, evaluate against the Gestalt principles by name: proximity (related elements closer to each other than to competitors — the most commonly violated); similarity (same-function elements share visual properties; different-function elements don't mimic each other); common region (elements sharing a container read as related — flag unrelated elements in one container and related elements split across containers); continuity (alignment implies reading order); figure-ground (interactive elements read as figure). Common fate requires motion artifacts — declare on statics. **[JUDGMENT: equidistance or nearer-to-unrelated = strongest flag, per the manuscript's Tier-1 criterion.]**
3. Flag: controls equidistant between two plausible referents; labels nearer an unrelated element than their referent; conflicting Gestalt cues (proximity says one grouping, similarity another); IA form — menu items whose category membership a user could reasonably assign elsewhere.
4. Name the elements, the ambiguous relationship, AND the specific Gestalt principle violated per flag (G6) — a Poor Grouping flag that cannot cite a principle is not a flag; expected vs. actual grouping must both be stated.

**Disconfirmation (pass two).** NOT present when: (a) apparent groupings are functionally correct; (b) the relationship is not critical to the goal; (c) a stronger cue resolves the ambiguity; (d) conceptual groupings are obviously categorical.

**Severity.** Scales directly with the stakes of the action the grouping supports — from hesitation (Low) to confident wrong action at scale (the butterfly ballot altered a presidential election: Critical). Key property: users who misread a grouping act with confidence, not uncertainty. Escalators: C3 (time pressure and density worsen misreads).

**Assessability & Confidence.** Confirmed ceiling for measurable violations: a control measurably equidistant between competing options with no secondary disambiguation. Otherwise Probable — whether users read the ambiguity wrongly is population/goal-relative; promotion path: task-based observation with grouping-dependent tasks. Context axis: C1 softens (learned conventions can disambiguate); C2 determines criticality.

**Attribution.** Inviting Dead End: confirm a specific wrong choice results, not mere unclarity. Information Overload: confirm excess density contributes — clutter is both cause and symptom; if removing excess resolves the grouping read, Information Overload is root cause (fix-based). Uncomprehended Element: individually clear elements confusing in combination attribute here.

**Report fragments.** Finding: "The spatial or conceptual relationship between [elements] is ambiguous — users are likely to misread which [control/label/option] corresponds to which [referent]." Why it matters: "Users who misread this relationship take the wrong action with confidence, not uncertainty."

**Remediation.** Apply Gestalt principles deliberately: related elements closer to each other than to any competitor; white space as an active grouping tool; explicit separators (lines, containers, color) where proximity alone is insufficient. For IA: categorize by users' mental models, verified by card-sort-style checks. Test with users unfamiliar with the system on grouping-dependent tasks.

---

### TRAP: FORCED SYNTAX *(pilot-grade)*
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

**Severity.** High when users abandon — assuming the function is unsupported or failing to find the supported sequence; Medium for reorganization friction. Voice-driven interfaces raise likelihood (natural speech has maximal grammatical flexibility). Escalators: C4 (a rigid construction in a daily task taxes every use); mixed novice/expert populations (C1) raise likelihood — the stages of skill acquisition construct tasks differently.

**Assessability & Confidence.** Sub-pattern B: Confirmed from a static screenshot when masks/placeholders/error text are visible; fully confirmable live by probing accepted formats. Sub-pattern A: structurally Confirmed from flows/code (which constructions exist), but whether unsupported alternatives are "reasonably expected" stays Probable without C1 — promotion path: population data or user observation of attempted starting points. Context axis: C1 softens under its default (mainstream conventions); C2 identifies the tasks that matter.

**Attribution.** Mutual exclusivity with Gratuitous Redundancy (above). Unnecessary Step(s): independent confirmation before adding. Memory Challenge adjacency: a supported-but-unguessable sequence that must be memorized may be that Trap — the distinguishing question is whether the order is unlearnable vs. merely unaccommodating **[JUDGMENT]**.

**Report fragments.** Sub-A: "[Task] can be initiated only via [construction] — users who naturally approach it via [alternative] will find the interface unresponsive to their intent." Sub-B: "[Field] accepts only [format]; common valid encodings [list] are rejected." Why it matters: "Users who think differently from the assumed sequence must reorganize their approach before proceeding — friction, and abandonment risk if they conclude the capability is missing."

**Remediation.** Sub-A: identify all reasonable starting points and accept them; plan explicitly which tasks support object→action AND action→object; support only reasonably likely constructions. Sub-B: parse tolerantly — accept all common unambiguous encodings and normalize internally; reserve rejection for genuinely ambiguous input.

---

### TRAP: MEMORY CHALLENGE *(draft-grade)*
*Sub-tenet: Comprehensible*

**Definition.** The user is required to remember information that is easy to forget: holding information across screens, recalling passwords/commands from long-term memory without a retrieval cue, executing multi-step processes by memory alone. Even carrying a small item from one screen to the next may be too much — short-term memory is tiny and volatile.

**Boundary.** IS: an unreasonable recall demand imposed by the design. IS NOT **System Amnesia**: that is the *system* failing to use information it was previously given; this is the *user* being made to remember. Both can co-occur (system has the data AND makes the user recall it) — then System Amnesia is root cause (fix-based: the system using its data removes the recall demand). IS NOT **Uncomprehended Element**: that is a knowledge gap (never learned); this is a recall gap (learned but unretrievable). With **Invisible Element**: a trained-but-forgotten invisible interaction is both — determine which is primary.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature; per-screen for recall-without-cue fields.*
1. Walk each task flow; at every step, list what the user must hold in mind to proceed, retrieve from memory without a cue, or execute from memorized instructions.
2. Flag every context-boundary carry: information shown on one screen and needed on another (or another session/device) without being re-presented.
3. Flag recall-without-cue demands: fields requiring memorized identifiers, security answers without the question shown, command vocabularies with no visible reference (voice command lists are the canonical case).
4. Flag instruction sequences the user cannot keep visible while executing them.

**Disconfirmation (pass two).** NOT present when: (a) the information is genuinely easy to remember in context (own name; a daily-used PIN); (b) the task is recognition, not recall — information presented for selection; (c) the information stays available for reference during the task.

**Severity.** High when recall failure blocks the task with no recovery path; Medium when recovery is effortful. Escalators: C3 — interruption, time pressure, and divided attention are precisely when held information evaporates; C4 — infrequent tasks (rare logins) maximize forgetting; spatially-presented information is markedly more memorable than verbal (mall-map principle).

**Assessability & Confidence.** Confirmed when provided screens show both the source information AND the recall demand — the cross-boundary carry is visible without user testing. Recall-without-cue flows: Confirmed-grade structural detection from flows/design files; whether the specific information is genuinely easy to forget stays Probable without C1/C4 — promotion path: interaction-frequency data or observation. Context axis: C4 (frequency) softens; C3 (interruption/pressure) sharpens severity.

**Attribution.** System Amnesia (above, fix-based). Invisible Element overlap (above). Forced Syntax adjacency: an unguessable required order that must be memorized — distinguish unaccommodating (there) from unlearnable-without-memorization (here) **[JUDGMENT]**.

**Report fragments.** Finding: "[Task/step] requires users to recall [information] without a retrieval cue, in a context where it is likely to be forgotten." Why it matters: "When users cannot recall this, they cannot complete the task — and may not know how to recover."

**Remediation.** Design for recognition over recall: let users see and choose rather than remember and enter. Present information spatially; chunk it; keep instructions visible during execution; provide retrieval cues (show the security question). The governing question: am I asking the user to remember this, or giving them a way to recognize it?

---

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

---

## TRAP CHUNKS — COMFORTABLE

### TRAP: PHYSICAL CHALLENGE *(pilot-grade)*
*Sub-tenet: —*

**Definition.** Some aspect of the system causes physical discomfort or makes it physically difficult or impossible to complete actions: touch targets too small to hit reliably, text too faint to read without strain, controls beyond comfortable reach, device forms too heavy or sharp to hold, audio too quiet for the environment, surfaces too hot, VR video jittery enough to induce queasiness. The user understands what to do; doing it costs strain, discomfort, or harm.

**Boundary.** IS: a physical demand exceeding the population's capabilities in the real context of use (C1 physical range + C3 channels). IS NOT **Accidental Activation** — its mirror image: this Trap makes intended actions too hard; that one makes unintended actions too easy; the fixes pull in opposite directions and each requires separate evidence. IS NOT present when the demand falls within established guidelines for the expected population and context, when difficulty is the point (dexterity games), or when it exists only under unrealistic test conditions. Systems that respond *too fast* for users to track or act on are also housed here (per the manuscript's FAQ — there is no separate "too fast" Trap).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for measurables; whole-artifact for form-factor properties.*
1. Measure every interactive target against the ~12 mm finger-pad standard (platform minimums); flag undersized targets, tight spacing, and targets in hard-reach zones for the device size and expected grip (thumb-zone maps).
2. Measure text contrast against WCAG ratios and size against platform minimums at expected viewing distance; flag failures.
3. Enumerate channel demands and check each against C3: audio-dependent elements (flag if hearing may be unavailable), speech-required interactions (flag against speech/privacy constraints), two-handed or precision gestures (flag against hands/mobility), sustained-attention visuals (flag against motion).
4. Note form-factor properties not assessable from the artifact (weight, thermals, VR comfort) for the coverage notes rather than guessing.

**Disconfirmation (pass two).** NOT present when: (a) within established guidelines for the expected population and context; (b) difficulty is intentional and appropriate to the use case; (c) the difficulty exists only in test conditions that don't reflect real use.

**Severity.** Medium for targeting errors and legibility strain; High for exclusion — users who cannot complete actions at all (accessibility populations first); Critical for illness or injury (VR motion sickness, thermal harm). Note the fluency effect: hard-to-read text doesn't just strain — users judge the *product* as harder and disengage (legibility is an engagement variable, not just an accessibility one). Escalators: C3 (a marginal target in motion or one-handed becomes a failure); C4 (strain on a core loop compounds).

**Assessability & Confidence.** Confirmed for measurable properties from artifacts: target size, spacing, contrast ratio, font size — checkable against published standards. Not assessable from design files for weight, thermal, vestibular, and true one-handed reach — hardware testing required; declare, never guess. Context axis: C3 is this Trap's primary input — its default (unencumbered, quiet, stationary) makes findings a lower bound and can gate presence outright (a hands-occupied context creates Traps a hands-free one lacks); C1 physical-capability range gates population-specific judgments (the general default assumes typical adult ranges — declare).

**Attribution.** Accidental Activation: opposite failure modes; evaluate together (enlarging targets to fix this Trap can create that one) but evidence separately. Feedback Failure: absent tactile/visual confirmation is that Trap's route (4) — confirm the perception difficulty independently.

**Report fragments.** Finding: "[Element/interaction] imposes a physical demand exceeding [guideline / comfortable reach / legibility threshold] for [population / context]." Why it matters: "Physical barriers cause errors and exclusion — and reduce users' perception of overall product quality independent of the specific difficulty."

**Remediation.** Follow established standards: minimum target sizes, WCAG contrast, platform reach-zone guidance. Prototype on real hardware in realistic conditions — design-file analysis flags candidates but cannot confirm most instances. Improving contrast removes a barrier AND measurably increases engagement. Caution: calibrate against Accidental Activation when enlarging or sensitizing anything.

---

### TRAP: ACCIDENTAL ACTIVATION *(draft-grade)*
*Sub-tenet: —*

**Definition.** It's easy for the user to unintentionally trigger an action during normal use: controls at natural grip points, overloaded gestures, wake words overlapping ordinary speech, hair-trigger sensors.

**Boundary.** IS: insufficient physical/interaction barriers between normal use and unintended triggering, with NO intent inference involved (a button pressed accidentally is simply a button pressed). IS NOT **Bad Prediction**: when the system *interprets* an ambiguous signal as intent and guesses wrong (wake word in background conversation, gesture read from incidental movement), Bad Prediction is the root cause and the activation its consequence (fix-based: better prediction thresholds resolve it). IS NOT **Inviting Dead End**: that Trap lures a deliberate action; this one fails to prevent an undeliberate one. IS NOT **Physical Challenge** — mirror image; separate evidence each way. Reversibility of the triggered action reduces severity but does not disconfirm.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact; requires device/form-factor context.*
1. Map controls against natural grip points, resting zones, and edge/corner contact areas for the device class; flag consequential controls located there.
2. Flag overloaded activations (double-tap, press-and-hold on grip surfaces), edge gestures adjacent to system gestures, and passive/sensor-based activations (proximity, motion, always-listening) — the last as candidates for Bad Prediction routing.
3. Flag hover-activated controls (menus, previews, tooltips-with-side-effects) positioned across common pointer paths — hover engagement during ordinary cursor travel is a static-detectable desktop case of this Trap.
4. For each flag, record the triggered action's consequence and reversibility (feeds severity).

**Disconfirmation (pass two).** NOT present when: (a) activation requires a deliberate, non-incidental action unlikely during normal handling; (b) the input vocabulary doesn't overlap natural behavior in the context of use (C3).

**Severity.** Scales with consequence × reversibility of the triggered action: accidental screenshot Low; accidental purchase High; accidental emergency call or recording Critical — for privacy/safety actions the acceptable false-trigger rate approaches zero. Escalators: C3 (motion, encumbrance, and pocketed/gripped carrying multiply incidental contact).

**Assessability & Confidence.** Probable ceiling from design files (placement vs. known grip zones flags candidates); actual activation behavior requires hardware testing — promotion path: realistic-use hardware trials. Context axis: C3 gates (grip, mobility, environment determine what "normal use" contacts); device class knowledge required — declare when absent.

**Attribution.** Bad Prediction routing (Boundary). Variable Outcome: overloaded controls whose outcome depends on unattended state make accidents worse — consistency is the root cause there; evidence separately.

**Report fragments.** Finding: "[Control/gesture] is positioned or configured so unintentional triggering is likely during normal use." Why it matters: "Accidental activations resist user care — severity scales with the reversibility and consequence of what fires."

**Remediation.** Add friction to the activation path: recess or shield controls, require sequential actions, add resistance, increase gesture distinctiveness. Confirmation dialogs are a last resort — they tax every intentional user (Unnecessary Step(s)); reserve for consequential AND irreversible actions after physical options are exhausted. Caution: friction added here can worsen Physical Challenge — calibrate together.

---

## TRAP CHUNKS — RESPONSIVE

### TRAP: SLOW OR NO RESPONSE *(draft-grade)*

**Definition.** The actual or perceived time the system takes to respond exceeds what the user wants or expects. Anchored to psychophysical thresholds: continuous actions (ink, AR/VR tracking) 0–10 ms; discrete actions (tap, click, scroll) ≤100 ms feels instantaneous, >1 s disruptive, >10 s attention abandons; conversational turns ≤1 s (human gaps average ~250 ms). Perceived duration is separately designable: unoccupied waits feel 1.4–1.8× longer; uncertain and unexplained waits feel longer.

**Boundary.** IS: response beyond threshold for the interaction type, OR within bounds but *feeling* slow due to absent/poor progress design. IS NOT **Captive Wait**: that Trap is about denied *control* (can't advance or exit); this is about *speed*. IS NOT present when deliberate pacing serves comprehension (transition animations that show what happened) or when a small delay corrects a too-fast response. Too-fast failures route to Physical Challenge.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-interaction; live artifacts strongly preferred.*
1. For live/instrumented artifacts: measure response times per significant interaction; flag every threshold violation by interaction type.
2. For all artifacts: audit wait-state design — flag any operation >1 s without continuous progress feedback; any >10 s with no occupied-time treatment (skeleton screens, background continuation); progress indicators that jump discretely or stall.
3. For static artifacts: response times are not assessable — declare; wait-state *design* (presence/quality of progress feedback in mocked states) remains flaggable.

**Disconfirmation (pass two).** NOT present when: (a) within thresholds AND longer operations carry well-designed progress feedback; (b) deliberate pacing serves comprehension; (c) delay is corrective for a too-fast response.

**Severity.** Medium for perceptible-but-tolerated delays; High at abandonment thresholds (>10 s undisclosed) and for conversational products beyond 1 s (users attribute rudeness/unintelligence). Critical for AR/VR tracking lag (motion sickness → Physical Challenge co-listing). Escalators: C4 (latency in a core loop taxes every use); the Weber 20% rule — improvements below ~20% are imperceptible, and accumulating sub-20% slowdowns are how products rot **[JUDGMENT: framed as maintenance guidance]**.

**Assessability & Confidence.** Confirmed for measured times against thresholds (among the most automatable checks — live/instrumented artifacts). Probable for perceived slowness from design review; promotion path: measurement, or observation of repeat-actions/frustration signals. Context axis: C2 (expectations vary by task stakes); C1 (population norms for the product category shape expectations).

**Attribution.** Feedback Failure: a slow system WITH good progress feedback has this Trap only; absent progress indication is that Trap co-occurring — separate evidence. Peak-end note for remediation prioritization: ends dominate memory; fix trailing slowness first.

**Report fragments.** Finding: "[Interaction] takes [duration] — exceeding the [threshold] for its type / with no progress indication during the wait." Why it matters: "Beyond perception thresholds users repeat actions, abandon tasks, or lose confidence their input registered."

**Remediation.** Immediate receipt confirmation under 100 ms even when the full response lags; continuous progress feedback beyond 1 s; never a static screen. Occupied-time techniques (skeletons, progressive loading, background continuation); pre-fetch so waits start before users mark time; make progress accelerate toward completion (peak-end). Improve actual speed in ≥20% increments to be felt.

---

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

---

## TRAP CHUNKS — EFFICIENT

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

---

### TRAP: INFORMATION OVERLOAD *(draft-grade)*

**Definition.** Information presented is understandable but exceeds what is needed: verbose instructions, wordy AI responses, cluttered displays, option-dense menus. Hick's Law prices it: decision time grows with choice count. The test is not "could there be less?" but "does the user need all of this right now?"

**Boundary.** IS: excess relative to the user's goal in this context. IS NOT present when the density is the task (data dashboards for comprehensive sensemaking), when everything shown is needed now, or when progressive disclosure is functioning. IS NOT **Distraction** (specific capture vs. diffuse excess — shared fix, separate evidence). Caused by **Gratuitous Redundancy** when duplicates inflate the count — confirm duplication independently; density alone can come from feature breadth or poor editing.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; menus/IA cross-screen.*
1. From the C2 goal, partition each screen's content: serves the likely goal now / secondary / serves no evident user goal.
2. Flag screens where the primary task requires processing only a small subset of what's displayed; count elements, options per decision point, and word counts of instructions/labels/errors against a plain-necessity read.
3. Flag verbosity per text element: could it shed half its words without losing clarity (the Krug test)?
4. Strongest static trigger — task burial: the primary action or call-to-action is buried within or beneath large text masses, or is not reachable without scrolling past content that does not serve the goal. Task burial is this Trap's clearest screenshot-grade evidence.
5. Homepages, dashboards, and navigation earn the closest read — accretion concentrates there.

**Disconfirmation (pass two).** NOT present when: (a) all of it is needed for the goal right now; (b) density is appropriate to comprehensive-sensemaking tasks; (c) progressive disclosure already gates the secondary tier.

**Severity.** Medium baseline (processing tax, Hick's-slowed decisions); High when the information cost exceeds motivation and users abandon. Escalators: C4 (a cluttered daily screen taxes forever); C3 (divided attention shrinks processing budget). Expert populations (C1) can legitimately need more — soften accordingly.

**Assessability & Confidence.** Probable ceiling — counts and densities measure Confirmed-grade, but necessity is goal-relative (C2 gates); promotion path: user task analysis or engagement data. Context axis: C2 gates; C1 softens for expert tools.

**Attribution.** Gratuitous Redundancy root cause when duplication inflates (confirm). Distraction co-occurring when specific elements also capture attention (separate evidence). Poor Grouping compounding: clutter obscures relationships — if decluttering restores the grouping read, this Trap is root cause (fix-based).

**Report fragments.** Finding: "[Screen] presents substantially more information than [goal] requires — [N elements / options / words] where [fewer] would serve." Why it matters: "Every element beyond what the goal requires taxes attention and decision speed on every use."

**Remediation.** Build outward from the likeliest goal; every element must earn its place. Progressive disclosure for the secondary tier. Cut text aggressively — get a professional writer. Fewer options per decision point. Audit regularly; interfaces accrete.

---

### TRAP: SYSTEM AMNESIA *(draft-grade)*

**Definition.** The system fails to take advantage of the user's prior work, preferences, or context: re-entering known information, recommendations ignoring ownership or history, context lost between sessions, re-authentication of the already-authenticated. Either the system never collected what it was exposed to, or collected it and doesn't use it.

**Boundary.** IS: the *system's* failure to leverage what it had. IS NOT **Memory Challenge** (the *user* made to remember) — both together (system has it AND user must recall it) make System Amnesia root cause (fix-based). IS NOT **Data Loss** (failing to *retain* what the user expects preserved vs. failing to *use* what it has). NOT present when re-prompting serves deliberate security/verification (though confirm-and-edit beats full re-entry even there), when architecture genuinely lacks access (verify it's actual, not assumed), or when the information may have changed (same superior pattern applies).

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-session by nature.*
1. Inventory every point where the user supplies information or exhibits trackable behavior; then flag every later point that requests or ignores the same thing: repeated form fields, criteria re-stated, ownership-blind promotions, context dropped across sessions.
2. Strongest flag — self-evidencing amnesia: the system *displays* information while simultaneously requesting it, or comments on an action in a way proving it didn't register it (selling the user what the same screen shows they own; a machine asking if you knew it takes credit cards while processing your credit card).
3. Live/multi-session artifacts: probe cross-session recall (resume point, preferences, exclusions).

**Disconfirmation (pass two).** NOT present when: (a) deliberate security/verification re-prompting (still note confirm-and-edit as superior); (b) genuine architectural inaccessibility (verified); (c) plausibly-changed information (same note).

**Severity.** Medium baseline (friction, "not paying attention" perception — which directly undermines any personalization claim the product makes); High when substantial prior work must be recreated. Escalators: C4 (recurring re-entry compounds); same-session amnesia rates worse than cross-session **[JUDGMENT: proximity heuristic from the manuscript's likelihood block]**.

**Assessability & Confidence.** Confirmed for self-evidencing cases (single screen suffices). Otherwise Probable — knowing what the system *has* requires data-architecture knowledge or session history; promotion path: architecture review or multi-session probe. Context axis: largely context-free structurally; C2 sharpens severity (critical-path re-entry).

**Attribution.** Bad Prediction downstream: poor retention makes poor predictions — confirm both (available-but-unused data AND bad predictions) before chaining, System Amnesia as root cause. Memory Challenge pairing (above). Unwanted Disclosure tension: fixing amnesia means retaining data — remediation must note the security obligation.

**Report fragments.** Finding: "[Flow] requests [information] the system already has — or displays evidence it hasn't tracked prior behavior." Why it matters: "Re-asking for what it knows signals the system isn't paying attention — friction now, and erosion of every personalization claim the product makes."

**Remediation.** Retention by default: information provided once is available at every subsequent point. Share data across product contexts. Exclude owned/engaged content from recommendations. For AI systems, design cross-session memory deliberately. Governing question: could the system reasonably be expected to retain this? If yes, it should — and secure it (see Unwanted Disclosure).

---

## TRAP CHUNKS — ACCURATE

### TRAP: INCORRECT INFORMATION *(pilot-grade)*

**Definition.** Information presented to the user is factually wrong, distorted, incomplete, out-of-date, or contains errors: inaccuracies, hallucinations, algorithmically biased content, deliberate misleading, down to typos. Its signature danger: unlike most Traps it produces no friction — users act on it in good faith and discover the wrongness late or never.

**Boundary.** IS: content presented as fact that is wrong (by external fact, internal contradiction, or staleness). IS NOT **Bad Prediction** — two tie-breakers, applied together: (1) *did the user ask for this?* Hard-coded or requested content that is wrong → this Trap only; unrequested proactive content → Bad Prediction; if also factually wrong → both. (2) *would this content be wrong for a user with completely different goals?* Wrong for any user regardless of goals → this Trap; wrong only for THIS user → Bad Prediction. Recommendation rows, surfaced content, and personalization results that are wrong for the stated user are always Bad Prediction, never this Trap. IS NOT present when content carries source attribution and honest uncertainty indicators, when it was accurate and a freshness mechanism exists, or when "incorrect" is really preference disagreement. Root cause of **Inviting Dead End** when wrong content marks a wrong path as right (mislabeled button, outdated instructions) — correct the information first; a merely-confusable element with no factual error is that Trap alone.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + cross-screen consistency.*
1. **Internal-contradiction sweep (strongest artifact-native check):** totals vs. their line items; labels vs. adjacent charts/data; counts vs. visible items; instructions referencing elements/pages that don't exist in the artifact; cross-screen statements that conflict.
2. Staleness sweep: dates, prices, version references, "current" claims with no freshness mechanism; flag time-sensitive content lacking one.
3. Provenance sweep: AI-generated or algorithmic content presented as fact without labeling, attribution, or uncertainty indicators — flag structurally regardless of truth value.
4. External-fact spot checks only where verifiable against authoritative sources within the analysis; otherwise record as not-assessable rather than guessing.

**Disconfirmation (pass two).** NOT present when: (a) attributed and presented with appropriate uncertainty — the Trap targets information presented *as fact*; (b) accurate-at-the-time with a live freshness mechanism; (c) the dispute is preference, not fact; (d) the content is placeholder (lorem ipsum, grey-box images, stub copy) and the submitter's context states the design is a draft — a known unfilled slot is not a factual claim; skip this Trap for such content.

**Severity.** Scales with domain stakes and the user's likely action taken in good faith: Low for trivial errors; High for financial, health, navigational, legal content acted upon; Critical when acted-upon wrongness is irreversible (the hallucinated-case sanctions). Confident presentation of uncertain information is itself the failure — users cannot calibrate trust without external verification, making accuracy an ethical obligation, not just a quality bar.

**Assessability & Confidence.** Confirmed for internal contradictions — the artifact convicts itself; this is the analyzer's native strength on this Trap. Confirmed for structural provenance failures (unlabeled AI content, missing attribution on factual claims). External factual accuracy: Probable at best, usually not-assessable without verification — declare rather than fact-check beyond reach. Context axis: C2 sharpens severity (what will the user *do* with this?); largely population-independent otherwise.

**Attribution.** Inviting Dead End downstream (above; fix-based — correcting the information dissolves the dead end). Bad Prediction (the did-they-ask test; both when unrequested AND wrong). Feedback Failure route (6): wrong progress/status feedback lands here as root cause.

**Report fragments.** Finding: "[Feature] presents [information] as fact that is [internally contradicted by X / stale with no freshness mechanism / unattributed machine output], in a domain where acting on it could [consequence]." Why it matters: "Users cannot calibrate trust in an interface's outputs without external verification — accuracy is an ethical and, in high-stakes domains, legal obligation."

**Remediation.** Document source, verification process, and freshness mechanism for every factual claim. Label AI-generated content and cite sources users can check. Highest verification standard plus clearest limitation disclosure for health/finance/safety/legal. Surface uncertainty rather than hide it — confident presentation of uncertain information is a design failure.

---

### TRAP: BAD PREDICTION *(draft-grade)*

**Definition.** The system fails in its attempt to anticipate the user's intent, preference, or context — it guesses wrong: autocorrect errors, irrelevant recommendations, ill-timed suggestions, proactive automation misfires. The user understands what the system did; they just didn't want it. The evaluation is economic: a 10%-wrong autocomplete can be net-positive; a 10%-wrong auto-*sender* cannot — acting demands a far higher accuracy bar than suggesting.

**Boundary.** IS: unwelcome proactive behavior from probabilistic intent inference. Two gate questions: *did the user ask for this?* and *would it be wrong for a user with completely different goals?* — content wrong only for THIS user is this Trap; content wrong for any user is Incorrect Information. IS NOT **Incorrect Information** (requested/hard-coded wrong content; both apply when unrequested AND universally wrong). Root cause of **Accidental Activation** when the system *interprets* ambiguity as intent (wake-word false positives); of **Distraction** (irrelevant interruptions); of **Unwanted Disclosure** (misjudged context surfacing private content); of **Unnecessary Step(s)** (undo/work-around burden) — each downstream effect requires its own evidence before chaining. Sometimes caused by **System Amnesia** (unused available context → worse guesses; confirm both).

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact feature inventory.*
1. Inventory every predictive/proactive feature: autocomplete/correct, recommendations, auto-actions, sensor-triggered behaviors, "helpful" interjections.
2. For each, record: does it *act* or *suggest*? Is a wrong guess dismissible at near-zero cost, or does it require undoing? Is the acted-upon outcome reversible? What signals feed it (rich context vs. ambiguous single sensor)?
3. Flag structurally (no accuracy data needed): any feature that ACTS on a prediction whose wrong outcome is irreversible or privacy/safety-relevant — the acting-threshold is unmet regardless of hit rate; any prediction requiring meaningful effort to dismiss or undo.
4. When user context (C1/C2) is stated: flag surfaced content, recommendations, or defaults that visibly contradict the stated user's demographics, goals, or tasks — this is static-screenshot detectable, and objective contradictions reach Confirmed without usage data.
5. Flag proactively surfaced content that occludes content the user is actively attending to (hover covers, overlay suggestions) — the system's guess about what helps is overriding what the user chose to attend to.
6. With usage/observation data: flag features whose correction cost exceeds their saving.

**Disconfirmation (pass two).** NOT present when: (a) the prediction economy is net-positive AND error cost is trivial; (b) wrong guesses dismiss themselves without disruption or effort.

**Severity.** Low for dismissible suggestions (residual cost: occupied space that pushes relevant content away); Medium–High for embarrassment/social harm (autocorrect in sent messages) and effortful workarounds; Critical for irreversible or safety/privacy misfires (false 911, unconsented recording). Escalators: C3 (ambient/shared contexts raise disclosure stakes); C4 (a daily-loop misprediction compounds).

**Assessability & Confidence.** Confirmed for the structural act-vs-consequence flags (feature design convicts itself). Actual accuracy: not assessable without usage data — declare; promotion path: observation of hesitation/correction/frustration after system-initiated actions. Context axis: C2 gates welcomeness (the same suggestion is welcome or painful by moment); C1/C3 shape it.

**Attribution.** Downstream chains per Boundary — each independently evidenced, this Trap as root cause where the fix (predict-when-certain, or suggest-don't-act) dissolves them. System Amnesia upstream (confirm available-but-unused context).

**Report fragments.** Finding: "[Feature] acts on [prediction] where a wrong guess is [irreversible / privacy-relevant / costly to undo] — requiring users to work around the system's guesses rather than benefit from them." Why it matters: "A prediction costing more to correct than it saves is a net negative — and wrong guesses in irreversible contexts cause harm that cannot be undone."

**Remediation.** Predict when certain. Acting requires a far higher bar than suggesting: where wrong-guess consequence is significant and reversal hard, suggest — and make dismissal free. Where accuracy can't be verified, default to inaction. Feed predictions with retained context (fix System Amnesia first where it's the cause).

---

## TRAP CHUNKS — PROTECTIVE

### TRAP: IRREVERSIBLE ACTION *(draft-grade)*

**Definition.** The user cannot backtrack or undo an action they have taken — a purchase that can't cancel, a message that can't recall, a file that can't restore. The Trap applies when recovery is *possible but unsupported* (Instagram's 30-day restore was always feasible; it simply hadn't been designed). Genuinely unavoidable real-world irreversibility (processed payment, delivered-and-read message) is scoped out — but a time-limited recovery window often exists even there.

**Boundary.** IS: unsupported-but-feasible recovery. NOT present when: irreversibility is genuine AND a *non-habituating* confirmation guards it (typed phrase, not a clickable dialog — users auto-dismiss standard dialogs); irreversibility is the intended, understood, desired outcome (permanent deletion of a sensitive file — then complicate the confirmation); a time-limited recovery window exists. A standard confirmation dialog alone does NOT disconfirm. Root cause of **Data Loss** when the unrecoverable action destroys work (reversibility fixes both — fix-based). Pairs against **Unnecessary Step(s)**: confirmations are usually a symptom; reversibility removes the risk AND the step. **Inviting Dead End** upstream when a misleading element led into the irreversible act (Reserve that means Purchase) — that Trap is root cause of the *entry*; this one owns the *no-exit*.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows/code).*
1. Walk every consequential action in scope; for each ask: is there undo? a recovery window? a back path that truly restores prior state?
2. Flag every consequential action with none of the three; record what guards it instead (nothing / standard dialog / non-habituating confirmation).
3. Flag commitment-understating labels on irreversible actions (Reserve→Purchase) as co-candidates for Inviting Dead End.
4. Flag existing confirmation dialogs for the reversibility-instead question (feeds Unnecessary Step(s)).

**Disconfirmation (pass two).** Per Boundary (a)–(c).

**Severity.** Scales with stakes: Low for trivial unrecoverable acts; High for consequential purchases/deletions; Critical for real-world irreversible harm (flight purchased, legal filing, safety actions). Likelihood risers: the action is reachable in fewer steps than its weight suggests; labels understate commitment; time pressure (C3).

**Assessability & Confidence.** Probable from flows/design (absence of visible undo is structural; whether recovery is *technically feasible* needs architecture knowledge) — promotion path: technical review. Confirmed from code showing no recovery path for a feasible one. Context axis: C2 sharpens stakes; C3 (pressure) raises likelihood.

**Attribution.** Data Loss pairing (fix-based, above). Unnecessary Step(s) pairing (reversibility beats confirmation). Inviting Dead End entry (above). Bad Prediction note: proactive error-prevention prompts ("send without attachment?") are predictions — hold them to predict-when-certain.

**Report fragments.** Finding: "[Action] cannot be undone; no recovery mechanism (undo, time-limited window, or non-habituating confirmation) exists." Why it matters: "Users who act unintentionally or under misapprehension have no path back — the cost of the error is permanent."

**Remediation.** Design forwards and backwards: for every consequential action, what does a user who changed their mind do? Reversibility over confirmation — it removes the risk and the step. Where truly irreversible: time-limited recovery window if feasible; else a non-habituating confirmation (typed phrase). Proactively prevent where prediction is certain.

---

### TRAP: UNWANTED DISCLOSURE *(draft-grade)*

**Definition.** The system exposes personal data or behavior in a way that is harmful, embarrassing, or unexpected. Two dimensions: *remote/digital* (data shared to third parties, opt-out defaults, location surfacing, history visible to household members) and *physical/real-time* (a notification read aloud in a crowded room, sensitive content on a visible screen, unsilenceable sounds). The governing test is contextual integrity: not "is this data secret?" but "does this flow match what the user would expect given the context in which they shared it?"

**Boundary.** IS: any communication of user data/behavior the user did not intend, by either dimension. NOT present when: explicit, fully-informed consent covers what/when/whom; disclosure is to the user themselves in a private context; data is aggregated and anonymized beyond individual identifiability. Caused by **Bad Prediction** when a context misjudgment surfaces private content (confirm the prediction error). Co-occurs with **Feedback Failure** when sharing happens *undisclosed* (disclosed-but-unwanted lacks that co-Trap). Deliberate business-driven over-sharing (opt-out defaults, opaque collection) flags additionally as potential dark pattern.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact + settings audit.*
1. Trace every feature that collects, stores, or surfaces user data; for each flow ask: would the user expect this destination, given where they shared it?
2. Audit defaults: flag every opt-out (rather than opt-in) sharing default, with sensitivity class (location, health, finance, behavior = highest).
3. Physical-dimension sweep against C3: flag audio announcements of content, always-visible sensitive surfaces on shared/ambient devices, unsilenceable sounds — any output the user cannot gate in social contexts.
4. Flag exports, saves, and shares that bundle more than users would expect — e.g., a saved meeting chat log that silently includes private messages; the expectation is set by what the user thinks they are sharing, not by what the feature technically captures.
5. Flag consent asked at moments the user can't understand what they're consenting to.

**Disconfirmation (pass two).** Per Boundary (a)–(c).

**Severity.** High baseline for sensitive categories (health, location, finance, sexuality) — inherently high-consequence; Critical when disclosure is irreversible and harmful (it usually is — disclosure cannot be undone, placing most confirmed instances at the ladder's top **[JUDGMENT: severity floor inference]**); Medium for social embarrassment (spoiled gifts — which still drove users to competitors). Escalators: C3 (shared/ambient devices, public contexts).

**Assessability & Confidence.** Confirmed for structural findings: opt-out defaults on sensitive data, ungated audio output of content (artifact/settings suffice). Whether a specific flow violates expectations: Probable, gated by C3 social context — promotion path: context-of-use inquiry. Context axis: C3 is primary (the privacy clause exists for this Trap); C1 norms shape expectation.

**Attribution.** Bad Prediction upstream (confirm). Feedback Failure co-occurrence (undisclosed sharing). System Amnesia tension: its remediation (retain more) raises this Trap's stakes — cross-note both ways.

**Report fragments.** Finding: "[Feature/setting] shares [data] with [audience] on an opt-out basis / in a context where users are unlikely to expect or intend it." Why it matters: "Users cannot prevent disclosures they don't know about — consequences run from embarrassment to legal liability, and disclosure cannot be undone."

**Remediation.** Defaults must match what fully-informed users would choose. Explicit opt-in for sensitive behavioral data; consent at moments of genuine understanding. For ambient/shared devices: granular control over what surfaces, when, and through which channel. Ask of every collection point: where could this surface, and would the user accept that?

---

### TRAP: DATA LOSS *(draft-grade)*

**Definition.** The system fails to retain information or content the user expects to be preserved: work lost to shutdowns without auto-save, forms discarding partial entries, co-authoring overwrites, ephemeral logs users assumed durable. Explicit-save is an engineering legacy, not a user requirement.

**Boundary.** IS: unintentional or inaction-triggered loss of user work/content. IS NOT **System Amnesia** (failing to *use* what it has vs. failing to *keep* what users expect kept — different causes, different fixes). NOT present when: continuous auto-save actually preserves it; the content is explicitly ephemeral and users are told before creating it; the user knowingly chose to discard. Co-occurs with **Irreversible Action** when a deliberate action destroys data with no undo (reversibility fixes both); accidental navigation-away losing an unsaved form is this Trap alone (system design, no deliberate act).

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen + failure-mode analysis.*
1. Identify every point where the user creates or modifies data; for each run the failure-mode battery: session timeout? crash/shutdown? navigation away? network drop? concurrent edit?
2. Flag every point where any answer is "it could be lost": absent auto-save, unpreserved partial entries, last-write-wins co-authoring, dismiss-to-void inputs (comment boxes that vanish on outside-click), transient content users would expect durable (meeting chat logs).
3. Live artifacts: simulate the failure modes where safe; design files: flag structurally and mark simulation-needed.

**Disconfirmation (pass two).** Per Boundary (a)–(c).

**Severity.** Scales with the value of the lost work and recreation effort: Low for trivially re-entered inputs; High for substantial creative work or unrecreatable data; Critical when permanent and of high personal/professional value — data loss reads as fundamental system failure and destroys trust disproportionately. Escalators: C3 (interruption-prone contexts multiply the triggering events).

**Assessability & Confidence.** Probable from design files (auto-save absence is structural; actual loss behavior needs simulation) — promotion path: deliberate failure-mode testing. Confirmed from live testing or code (retention logic inspectable). Context axis: C2 sharpens (what work is at stake); largely population-independent.

**Attribution.** Irreversible Action pairing (deliberate-destruction case; fix-based on reversibility). System Amnesia distinction (above). Unnecessary Step(s): explicit-save requirements are also an eliminable step — auto-save removes both.

**Report fragments.** Finding: "User content in [flow] is permanently lost if [failure mode] occurs before explicit saving; no auto-save or recovery exists." Why it matters: "Data loss is experienced as fundamental system failure — it destroys trust and forces users to repeat work already done."

**Remediation.** Continuous auto-save wherever feasible. Design for failure from the outset — timeouts, drops, and crashes are certainties, not edge cases. Conflict resolution that protects all contributors, not last-write-wins. Where deletion is the goal, complicate the confirmation (typed word) so habituated clicking can't destroy data. Governing question: what happens to the user's work if the session ends right now?

---

## TRAP CHUNKS — HABITUATING

### TRAP: GRATUITOUS REDUNDANCY *(pilot-grade)*
*Sub-tenet: Non-Redundant*

**Definition.** Two or more separate elements, at the same or directly nested level, serve the same function — leading to the same destination, triggering the same action, or conveying the same information. Scope is defined by function — navigational, operative, or informational: duplicated status indicators are this Trap even though they are never traversed. Visual appearance is irrelevant: duplicates need not look alike (Healthcare.gov's differently-labeled links to one page are the canonical case). For destination and action paths, duplication counts only within the same grammatical construction (object→action vs. action→object): paths serving different, *reasonably expected* constructions are flexible syntax, not this Trap. For informational elements no such exemption exists — two elements conveying the same information at the same level are duplicates regardless.

**Boundary.**
- IS: functional duplication per the definition, whether the elements are visually identical or not.
- IS NOT flexible syntax — but the exemption covers only constructions users would reasonably expect or prefer; duplicating via unlikely constructions is still gratuitous. Mutually exclusive with **Forced Syntax** per flow: only-one-construction = that Trap; duplicate-paths-same-construction = this one; confirm which before flagging either.
- IS NOT redundant encoding within a single element: icon plus label on one button, or color plus shape within one indicator, is one element — often accessibility best practice; never flag it as this Trap.
- IS NOT elements that look similar but serve different functions — verify functional equivalence before flagging; conversely, visual difference never rules the Trap out.
- IS NOT duplication across different, non-nested hierarchy levels.
- IS NOT one persistent element rendered across multiple screens (header nav, tab bar) — that is ONE element.
- **No attentional-context exemption for informational elements.** Duplicating an indicator so "one copy is wherever the user looks" is not sanctioned design — it is this Trap. The endorsed alternative is a single indicator made globally perceivable (see Remediation and Effectively Invisible Element).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen, plus cross-screen grouping for multi-screen artifacts.*
1. Enumerate every interactive and informational element on the screen or level under review — links, buttons, icons, menu items, status indicators — recording each element's apparent function from label, icon, placement, and context.
2. Group by function — apparent destination, triggered action, or information conveyed — ignoring visual appearance. For informational elements, group by the state or fact communicated.
3. Flag any group of two or more at the same or directly nested level; record the count and every instance's location.
4. Confirm functional equivalence where the artifact allows: traverse the prototype or live site; audit link targets and handlers in code; for indicators, confirm they reflect the same state variable.
5. Cross-screen (multi-screen artifacts only): group functions across screens within the same navigation level; persistent chrome counts once — flag only additional elements duplicating what it already provides.
6. Conventional-pair guard — do not silently exempt "standard patterns"; these are candidates like any others: site logo navigating to homepage alongside a separate Home link; a search input field alongside a standalone search icon triggering the same search; multiple Sign In / Get Started buttons for the same action; the same destination in two or more nav regions on one screen. Convention may inform severity; it does not disconfirm presence.
7. Routing fork on identical-looking elements: if the functional-equivalence check (step 4) shows identical-looking elements with the SAME function → this Trap; with DIFFERENT functions → route to Inviting Dead End (a lookalike inviting the wrong choice) and, where the same element type behaves differently across contexts, Variable Outcome — per those Traps' boundaries.
8. Name every candidate concretely ("six elements on Home appear to lead to Find a Location"); never flag on a general impression of clutter (G6).

**Disconfirmation (pass two).** NOT present when: (a) the paths serve different, reasonably expected goal constructions (flexible syntax); (b) the elements sit on different, non-nested hierarchy levels; (c) apparent duplicates in fact serve different functions (verified); (d) the "duplicates" are one persistent element rendered across screens.

**Severity.** The consequence is decision think-time ("are these different?") plus visual noise — for visually identical and dissimilar duplicates alike — and slowed habituation as practice divides across routes. Scales with duplicate count and real estate consumed (two quiet duplicates: Low; thirty-plus duplicated links restructuring a homepage: High). Escalators: C4 is decisive — duplication on recurring tasks rates far higher than on one-time tasks (it blocks the automaticity repetition would otherwise build); C2 critical-path placement escalates. Compounding downstream effects (displaced content, added scrolling, option proliferation) raise cumulative severity but are attributed only per the Attribution rules.

**Assessability & Confidence.** Static screenshot: look-alike duplicates → Probable ("apparent duplicates; functional equivalence requires prototype, live site, or code"); visually dissimilar duplicates → not detectable as a class — report the limitation ("this artifact cannot exclude visually dissimilar duplicates; a link-target audit would"). Prototype/live/code: Confirmed — among the most automatable Traps; code audit (duplicate destinations, shared handlers, one state variable rendered twice) routinely finds what usability testing misses, since testing walks intended paths only. Context axis: largely context-free — duplication is structural; C2 and C4 sharpen severity only; no field gates presence.

**Attribution.** Downstream Traps (Invisible Element via displaced content, Unnecessary Step(s) via added scrolling, Information Overload via option proliferation) each require independent evidence — never assume them from confirmed duplication; when confirmed, this Trap is more often a contributor than sole cause. Reverse link: where duplication was introduced to remedy an Effectively Invisible Element, report this Trap as the current problem and note the underlying attention problem it compensated for — the fix must address both. Ambiguous Home: duplicated orientation points co-occur — see that Trap.

**Report fragments.** Finding: "[N] separate elements on [screen/level] serve the same function — [function]. The duplicates add decision overhead and visual noise without adding capability." Why it matters: "Duplicate elements multiply what users must evaluate without multiplying what they can do, slowing decisions and preventing the repetition on a single route that automatic use requires."

**Remediation.** Consolidate: one path per destination per reasonably expected construction; one indicator per state. If the duplicate was added because the original was hard to notice, fix the original's noticeability instead of keeping copies — relocate into the task's attentional focus, or make the single instance globally perceivable (whole-screen tint shift, screen-edge pulse, attention-following placement). Audit code for duplicate destinations and shared handlers. Preserve genuinely flexible syntax; do not "fix" it as redundancy.

---

### TRAP: VARIABLE OUTCOME *(draft-grade)*
*Sub-tenet: Consistent with Expectations*

**Definition.** The system responds differently and unexpectedly to the same user action at different times. Most often a mode error (CapsLock; gear selectors; overloaded controls), but modes aren't required — inconsistently supported functions (right-click works on some instances, not others) qualify. The key question is not whether the same action produces different results, but whether the user is *attending to the signal that explains the difference*: a context-dependent button the user is looking at is unproblematic; a mode tracked only in memory is the Trap.

**Boundary.** IS: same action, different outcome, with the explaining state outside the user's awareness. NOT present when: a mode indicator sits within the user's attentional focus at the moment of action; the state is a quasi-mode the user physically sustains (held Shift — impossible to forget); variation is in degree, not kind (harder flick scrolls faster); the state change is itself an explicit user action they'd be attending to. Caused by **Invisible Element** (no indicator exists) or **Effectively Invisible Element** (indicator exists, placed away from attention) — confirm the indicator's existence/placement independently; do not infer either from the outcome variation alone; when confirmed, the indicator Trap is root cause (fixing it dissolves the surprise — fix-based). **Accidental Activation** worsens on overloaded, state-dependent controls — consistency is root cause there.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-state; code is the native artifact.*
1. Code artifacts: sweep for state-handlers — any place one user action routes to different outcomes by system state; each is a candidate.
2. Flow/live artifacts: for each control, probe across contexts/states — same action, same result? Flag every divergence.
3. For each candidate, locate the state signal: does one exist? where, relative to the user's attentional focus at the action moment (feeds EIE/IE routing)? Is the state user-sustained (quasi-mode)?
4. Flag inconsistently supported functions (same element type responding differently across instances) — the modeless form; static screenshots cannot detect this Trap — declare.

**Disconfirmation (pass two).** Per Boundary conditions (a)–(d) above.

**Severity.** Medium for surprise-and-retry; High when the wrong-state action costs the task; Critical in safety contexts — mode error is a recurring factor in aviation, vehicle, and medical catastrophes (the Monostable shifter killed). For safety-critical interfaces the acceptable mode-error risk is zero: redesign to eliminate the mode, not to improve the indicator. Escalators: C3 (attention elsewhere is precisely when modes are forgotten — driving); C4 (overloaded controls in core loops slow all learning — game-controller research).

**Assessability & Confidence.** Confirmed detection from code (state-handlers are directly findable — an AI-native strength); whether users will be unaware of the state: Probable, gated by attention knowledge (C2/C3) — promotion path: observe attention at the action moment. Modeless form: harder, needs flows/live probing. Context axis: C3 gates the awareness judgment; C1 (prior product conventions) softens.

**Attribution.** Indicator routing per Boundary (fix-based). Wandering Element and Inconsistent Appearance are the placement/appearance members of this consistency family — audit each independently. Ambiguous Home: a home action that sometimes lands elsewhere is this Trap co-occurring there.

**Report fragments.** Finding: "[Action] produces different outcomes depending on [state], and no indicator of that state is reliably within the user's attention when acting." Why it matters: "Unexpected outcomes prevent reliable habits — and in safety-critical contexts, mode errors kill."

**Remediation.** Eliminate the mode where possible — consistent behavior beats a well-indicated mode (even perfectly visible indicators lose to dedicated functions for learning speed). Where unavoidable: put the indicator where attention already is at the action moment, or convert to a user-sustained quasi-mode. Safety-critical: eliminate, don't indicate.

---

### TRAP: WANDERING ELEMENT *(draft-grade)*
*Sub-tenet: Consistent with Expectations*

**Definition.** The same interface element is presented in a different location at different times — controls, status indicators, or content that move across screens, contexts, or app versions. Spatial memory is among the most powerful automaticities available to designers, and it costs nothing but the discipline of keeping things where they are; wandering squanders it — every displaced encounter pulls the user back into conscious search.

**Boundary.** IS: inconsistent *placement* of the same element across contexts. IS NOT **Inconsistent Appearance** — the manuscript's line: a control can wander without changing appearance and can change appearance without wandering; audit placement and visual form independently, evidence each separately. Downstream of it: **Effectively Invisible Element** — but confirm independently that the new position falls outside where users would look; do not infer invisibility from movement alone (fix-based: pinning the element resolves derivative noticing failures — Wandering Element is root cause). NOT present when: placement variation is context-appropriate and meaningful (a Share button positioned differently in reading vs. list view because the content relationship differs); the element is low-frequency (no spatial memory would form); the change is explicitly communicated through a design transition users will attend to.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature — this Trap does not exist in a single screenshot; declare on single-screen artifacts.*
1. Identify recurring elements across the screens in scope; prioritize high-frequency controls — search, navigation, editing, confirmation — where spatial memory pays most.
2. Map each recurring element's position per context (coordinates/regions in design files make this directly auditable).
3. Flag every placement inconsistency, recording the contexts and displacement; note ecosystem-level wandering (the same platform control placed differently across an app family).

**Disconfirmation (pass two).** Per Boundary conditions.

**Severity.** Medium baseline — slowed habituation, conscious search on every encounter; escalates on C4 (high-frequency, time-sensitive controls: navigation, edit, search) and C3 (searching for a moved control while driving or under pressure). **[JUDGMENT: High when displacement of a critical control under time pressure costs the task.]**

**Assessability & Confidence.** Confirmed from multi-screen design files — cross-context placement comparison is directly auditable, one of the most automatable Traps, and precisely the audit human task-based reviews skip (an AI-native strength). Context axis: C4 gates severity weighting (frequency); largely population-independent for presence.

**Attribution.** Inconsistent Appearance: independent co-audit (both may be present; separate evidence). Effectively Invisible Element downstream (fix-based, above). This Trap is invisible to task-based evaluation — flag the methodology gap in reports where relevant.

**Report fragments.** Finding: "[Control] appears in different positions across [contexts] — users who learned its location in one context must search in others." Why it matters: "Inconsistent placement prevents spatial memory from forming — every encounter demands conscious search that consistency would have made automatic."

**Remediation.** Establish placement conventions for high-frequency controls early and treat them as constraints. Map recurring elements' placement across every context; inconsistencies are the finding. Platform-level controls hold consistent positions across an ecosystem.

---

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

---

### TRAP: AMBIGUOUS HOME *(draft-grade)*
*Sub-tenet: Well-Oriented*

**Definition.** The interface presents multiple, competing locations for getting oriented and initiating tasks. A single reliable home — one place, reachable from anywhere by one consistent action — is the anchor from which navigational habituation flows and the automatic recovery point when users get lost. When home is ambiguous, users must hold the structure in conscious memory and reason their way back — the burden habituation should have removed.

**Boundary.** IS: two or more plausible homes, or an inconsistent action for reaching home. Scope test: this Trap is exclusively about the product's GLOBAL home — the top-level anchor of the whole navigation system. Multiple competing entry points to a specific feature or task are Gratuitous Redundancy, not this Trap; ask "is the ambiguity about where to start in the whole product, or about which element to use for a specific task?" The manuscript frames it as a special case of its neighbors — multiple homes is a redundancy problem, an inconsistent home action a consistency problem — but it is its own Trap with its own fix (consolidation). NOT present when: one clearly defined home is reachable from every context via one consistent action; the product is deliberately homeless because all tasks are self-contained; apparent multiple homes are entry points to clearly distinct, non-overlapping sections users understand as separate. Co-occurring: **Gratuitous Redundancy** when the homes duplicate capabilities (confirm the overlap); **Variable Outcome** when the home action lands differently at different times (separate evidence); **Memory Challenge** downstream when users must consciously track location because no reliable home exists (confirm); **Poor Grouping** when overlapping capabilities blur the mental model. Home iconography used for non-home destinations (a house icon on a Library button — the Meta VR case) is an **Inviting Dead End** compounding this Trap.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/whole-IA.*
1. Identify every element or location that could plausibly be read as a starting point / orientation anchor (landing screens, dashboards, home-labeled or home-iconed destinations, launcher surfaces). More than one candidate = flag.
2. Audit the return-home action from every context: same action everywhere? single-step everywhere? Flag inconsistencies and multi-step returns.
3. Flag home iconography attached to non-home destinations (routes to Inviting Dead End co-listing).
4. Multi-platform/multi-mode products: compare home conventions across modes (the Windows 8 two-homes case).

**Disconfirmation (pass two).** Per Boundary conditions.

**Severity.** Medium — disorientation, orientation attention-tax on every task start; High when users cannot recover from being lost (deep hierarchies where home is the recovery mechanism) or abandon. Escalators: C4 (orientation happens every session, forever); product complexity.

**Assessability & Confidence.** Probable from design files (candidate homes and return-action consistency are structural; which one users *conceptualize* as home needs user knowledge) — promotion path: ask users unprompted where they'd go to start a task or recover; inconsistent answers confirm. Confirmed for the return-action inconsistency half (directly auditable). Context axis: C1 gates the conceptualization judgment; C4 weights severity.

**Attribution.** Per Boundary — each co-Trap independently evidenced; this Trap is root cause where consolidation dissolves the others (fix-based).

**Report fragments.** Finding: "The interface offers [N] plausible homes — [list] — producing different starting contexts and preventing a single orientation habit; the return-home action is [inconsistent across contexts]." Why it matters: "Without one reliable home, disoriented users must reason their way back instead of reaching automatically — orientation permanently taxes attention that habituation should have freed."

**Remediation.** Consolidate to one home — not better labeling of several. One destination, one action, consistent across every context and input mode. Reserve home iconography exclusively for the primary home. Audit every new entry point for whether it creates a competing home.

---

## TRAP CHUNKS — BEAUTIFUL

### TRAP: POOR AESTHETIC *(draft-grade)*

**Definition.** The system's sensory design, style, personality, or tone is judged unpleasing, inappropriate, or inauthentic by its intended users. Two dimensions: *attractiveness* (visually unpleasant) and *appropriateness* (mismatched to context, audience, or moment — and time-sensitive: current today can be dated in three years). Scope includes every sensory register — visuals, sound, voice intonation, and product personality/tone (a chatbot's sycophancy is an aesthetic failure).

**Boundary & assessability warning (read first).** The manuscript is explicit: this is the Trap least amenable to automated detection, and the framework author's verdict is **No** — an AI can flag violations of specific design principles but cannot judge whether a design is beautiful or appropriate for its audience and moment; that judgment requires cultural knowledge and aesthetic sensibility and remains the designer's domain. The analyzer therefore NEVER issues a beauty verdict. Its entire legitimate contribution: (1) principle-violation flags — misalignment, broken visual hierarchy, inconsistent typography, contrast failures — most of which route to *other* Traps as root cause (contrast → Physical Challenge; hierarchy → Poor Grouping; inconsistency → Inconsistent Appearance); (2) the functional-foundation audit — the aesthetic-usability effect runs both directions, so failures on the other eight Tenets actively degrade aesthetic experience; addressing every other-Tenet finding is the analyzer's real aesthetic contribution; (3) tone/personality observations flagged as observations for designer judgment, never verdicts. Also NOT a Trap to validate via pre-launch user opinion: pre-launch aesthetic feedback reflects resistance to the unfamiliar (the Razr and Aeron were pre-launch failures and post-launch standards) — reports must not treat "users disliked the look" as confirmation.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + whole-product coherence.*
1. Run the principle audit: alignment grid violations, hierarchy collapse (no clear reading order), typography inconsistency, color-system violations, contrast failures — each flagged with its routing Trap where one exists.
2. Flag tone/personality mismatches observable in copy and sound (celebratory intonation on sad content; sycophantic assistant register) as designer-referral observations.
3. Compile the cross-Tenet foundation summary: aesthetic experience is capped by the product's worst functional failures.
4. Cumulative-risk observation **[JUDGMENT — v2-sourced rule; confirm it coheres with the no-verdict stance]**: when three or more measurable principle violations or functional Traps co-occur on one screen, add an observation (not a verdict) that the accumulation itself signals design-investment risk — aesthetic failures are cumulative, and the combined effect reads as overall quality failure to users.

**Disconfirmation (pass two).** Principle-violation flags disconfirm normally under their routing Traps. The residual aesthetic judgment is permanently "not assessable by this analyzer — designer domain": that is the correct, honest output, not a failure of the tool.

**Severity.** When principle violations route elsewhere, their host Trap's ladder applies. The unrouted residual carries business weight the report should state without scoring: aesthetically failing products are perceived as less trustworthy, less desirable, and less usable (aesthetic-usability effect) **[JUDGMENT: reported as context, not a ladder rating]**.

**Report fragments.** Observation form only: "The following measurable design-principle violations were found [list, with routed Traps]; the residual judgment of attractiveness and appropriateness for [audience/moment] requires design expertise and is outside this analysis. Note: pre-launch user aesthetic feedback is an unreliable validator — novel designs routinely test poorly and succeed."

**Remediation.** Excel on the other eight Tenets first — functional failure cannot be rescued visually, and functional excellence is beauty's necessary foundation. Give design expertise genuine authority; principles (alignment, hierarchy, contrast, proximity, color, typography) are the floor, and knowing when to depart from them is where expertise earns its place. Listen to users; trust your designers.

---

## AUTHORING STANDARDS (for KB maintainers — never loaded into the analyzer)

**A1. Generalization test.** Every rule must be stated in terms of mechanism and observable conditions, never the surface features of a UI it was derived from. Before a rule enters the KB: would it fire correctly on an unseen interface from a different domain (medical device, game console, banking app)? If it names widgets, layouts, or phrasings specific to one evaluated product, it is overfit — rewrite at the mechanism level or reject.

**A2. Anecdote rule.** A failure observed once justifies a measurement, not a rule. Rules enter on evidence across artifacts or on principled mechanism; single-incident rules enter, at most, as a scoresheet column to watch.

**A3. Token budget.** Every rule competes with every other rule for the model's attention. Prefer deletion to addition; a rule that cannot state what failure it prevents does not stay.

**A4. Eval hygiene.** Never tune rules against the same artifacts used to score the KB. When iterating on eval results, hold out artifacts the revised KB has not seen, or the KB overfits the eval set exactly as A1 warns for single UIs.

**A5. Context-free language.** Every rule must be self-contained and readable without the history of its authoring. Never write a rule as a correction to a misreading only the authors remember ("X, not Y" where Y is a private reference); name the full intended scope instead. The analyzer has no memory of why a sentence was written — only what it says.

**A6. Write against the full artifact range.** Draft every detection procedure against all artifact types the analyzer accepts (single screenshot, disconnected screens, flows, live products, code) and declare its unit of analysis per G7. A procedure written with only the simplest artifact in mind silently overfits to it — "this screen" phrasing on a flow analysis is the canonical failure.

**A7. Definition coverage check.** Before a Trap chunk is final, map each clause of its definition to at least one detection trigger; any definitional clause with no corresponding trigger means the procedure detects a subset of the Trap. Sub-check — qualifier scope: for every qualifier in a definition, verify it applies to every disjunct it grammatically modifies; a qualifier true of some disjuncts silently attached to all of them makes the definition mean less (or more) than it says.

**A8. Controlled vocabulary, neutral terms.** The KB uses the framework's controlled vocabulary throughout — "element," not cue/signifier/affordance; synonyms from the broader literature appear only when explaining related concepts, never in operational rules. "Sibling Trap" is reserved for the Uncomprehended Element / Inviting Dead End pair as defined in the Taxonomy Index. Operational terms must be descriptively neutral — no intent, agency, or evaluation baked into words naming observable conditions (test: does the connotation describe the mechanism or decorate it? "invites" describes an Inviting Dead End's mechanism and stays; "disguised" decorated duplicate-appearance with intent and was cut).

---

## OPEN ITEMS
1. Where does gratuitously multi-cue encoding *within* a single conceptual signal (one state, five simultaneous cues in one place) live — Information Overload, or a gap? [Gap-lens candidate]
2. Manuscript edits implied by KB work: Gratuitous Redundancy section rewritten in function language (incl. informational scope and appearance-irrelevance); Forced Syntax boundary vs. expression rigidity made explicit; FAQ Q8 (element terminology) answer written; Effectively Invisible Element confidence-tier sentence completed; placeholders (Forced Syntax Alexa example, Mass General, "add another path to it. But…", missing quotes/examples across draft-trap sections); stranded Variable Outcome definition line at end of Gratuitous Redundancy's block; "Sibling Trap" definition added to the manuscript.
3. Draft-grade review pass by framework author: all [JUDGMENT] flags, then boundaries and severity blocks generally.
4. Literature gap-lens (phase two): per-trap audit of what the literature offers that the manuscript hasn't operationalized, and where each item sits.
5. Eval build: artifacts (seeded seven + decoys + one root-cause-ambiguous case + clean control), scoresheet (detection / attribution three-way / epistemic honesty / remediation specificity / trap-name-adjacency watch column), pre-registered success bars, A/B/C/D/E conditions with fresh-content C.
6. v2-salvage additions pending author sign-off (integrated in v2.1, sourced from the deployed v2.0 KB's feedback-derived rules): Invisible Element ↔ Unnecessary Step(s) prerequisite-gate disambiguation; Incorrect Information ↔ Bad Prediction wrong-for-whom test and recommendation-row rule; the placeholder/draft exception; Feedback Failure's in-screen vs. post-action rule; Gratuitous Redundancy's conventional-pair guard (logo+Home, search field+icon, repeated CTAs) and identical-elements routing fork; Ambiguous Home's global-home scope test; Uncomprehended Element's state-vs-meaning exclusion, IO polarity check, and design-change regression clause; Poor Grouping's cite-the-principle requirement and common-region addition; Memory Challenge's dual-visibility Confirmed condition; Information Overload's task-burial trigger; Accidental Activation's hover trigger; Unwanted Disclosure's bundled-export trigger; Inviting Dead End's promise-breaking and label-as-evidence rules; Poor Aesthetic's cumulative-risk observation (also [JUDGMENT]-tagged). Routing note for review: v2.0's identical-elements-different-functions fork routed to Variable Outcome; v2.1 routes primarily to Inviting Dead End with Variable Outcome secondary — confirm intended routing.
