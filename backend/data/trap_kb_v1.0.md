# UI TENETS & TRAPS — MCP KNOWLEDGE ENGINE v1
## Source: Tenets_and_Traps_Card_MASTER_print.pdf (V1 card deck only)
## Built exclusively from card deck content. No book manuscript, v2 MCP, or other source used.

---
## ARCHITECTURE NOTES FOR AI TOOL

**Source constraints:** Each card provides a definition (verbatim), one example, and a card number. No extended content exists in this source — no "Why it occurs," no "How to avoid," no "Related Traps," no AI detectability sections. All disconfirmation criteria, severity assessments, and confidence tiers in this resource are derived strictly from the logical boundary conditions of each definition and the implications of each example. Where the card content does not support a reliable inference, this is noted explicitly.

**Priority order for all assessments:**
1. Minimize false alarms (highest priority) — apply disconfirmation first
2. Maximize correct rejections
3. Maximize hits on high-severity Traps
4. Minimize misses on high-severity Traps

**Disconfirmation protocol:** Each chunk leads with disconfirmation criteria derived from what the definition requires. If the stated conditions are not both present, the Trap is not present. Apply these before any positive detection logic.

**Severity convention (inferred from definitions):** High severity when the implied consequence is task failure or significant user harm.

**Confidence tier convention (inferred from definitions):**
- Tier 1: Detectable from interface artifact alone based on what the definition requires
- Tier 2: Requires user context to confirm — not determinable from artifact alone
- Tier 3: Requires hardware testing or real-world conditions

---

# CHUNK: FRAMEWORK OVERVIEW

**chunk_id:** framework_overview_v1
**source:** Card deck intro cards (Tenets_and_Traps_Card_MASTER_print.pdf)

## What are Tenets & Traps?

Tenets & Traps are a heuristic framework for evaluating user interfaces. They distill a massive body of existing UI research into a portable, actionable tool. They are proven to predict actual user performance and satisfaction. They facilitate the design of better solutions by explaining what causes problems. They improve team communication by establishing common language.

**Tenets** describe general attributes of good interface design.
**Traps** describe common design problems that degrade interface goodness. Reduce Traps and the experience improves.

## Framework Structure

| Tenet | Traps |
|---|---|
| Understandable | Invisible Element, Effectively Invisible Element, Distraction, Uncomprehended Element, Inviting Dead End, Poor Grouping, Forced Syntax, Memory Challenge, Feedback Failure |
| Comfortable | Physical Challenge, Accidental Activation |
| Responsive | Slow or No Response, Captive Wait |
| Efficient | Unnecessary Step, System Amnesia, Information Overload, Bad Prediction |
| Forgiving | Irreversible Action |
| Discreet | Unwanted Disclosure |
| Protective | Data Loss |
| Habituating | Gratuitous Redundancy, Variable Outcome, Wandering Element, Inconsistent Appearance, Ambiguous Home |
| Beautiful | Unattractive Appearance |

**9 Tenets, 26 Traps.**

## How to Use Trap Cards

1. Identify the tasks most important to your target user.
2. Walk through ALL the ways the user might try to complete each task in the design.
3. Identify and log any Traps observed; note their severity. Many issues have more than one Trap — log all.
4. If unsure which Traps apply, ask which Tenets are being degraded — this helps clarify the problem.
5. For issues with multiple Traps, ask whether one Trap may be the root cause of the others. Understanding the root cause is often critical to finding the best solution.
6. If time permits, cross-validate by having other reviewers run through the tasks.
7. Share your results. Use Tenets & Traps to facilitate a good discussion.

---

# TRAP CHUNKS — UNDERSTANDABLE TENET

---

# CHUNK: INVISIBLE ELEMENT

**chunk_id:** trap_invisible_element_v1
**card:** 1 | **tenet:** Understandable

## Definition (verbatim)
No cue (label, icon, affordance, or prompt) is provided to signal to the user how to achieve a goal, and the user has insufficient prior learning to overcome its absence.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) A cue IS provided — any label, icon, affordance, or prompt that signals how to achieve the goal means the element is not invisible. The complete absence of a cue is required.
(b) The user HAS sufficient prior learning — the definition requires both conditions: no cue AND insufficient prior learning. If users demonstrably know how to proceed without a cue, this Trap is not present even if no cue exists.

**Both conditions must be true simultaneously. Either condition absent = Trap not present.**

## Example → Rule
**Windows 8 Start Menu (2012):** Microsoft removed the visible means to launch the Start Menu. User confusion resulted. The Start button was returned in the next version of Windows.
→ *Rule: When a visible cue users rely on to reach a core function is removed and users lack sufficient prior learning for the alternative, an Invisible Element Trap is created. The restoration of the removed cue confirms that its absence was the cause.*

## Rules
- Both conditions required: no cue present AND user lacks sufficient prior learning. Either alone does not constitute this Trap.
- "Cue" covers labels, icons, affordances, and prompts — the definition is not limited to visual cues.
- Prior learning can compensate for absent cues, but only when that learning reliably exists in the user population.
- A design reversal that restores a previously removed cue after user confusion retrospectively confirms the original removal was this Trap.

## Severity
*Inferred from definition.* When no cue exists and prior learning is insufficient, the user cannot achieve the goal. **High severity** — task failure is the direct consequence when both conditions are met.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** When the absent cue is the sole path to a goal with no alternative visible anywhere in the interface, the Trap is detectable from the artifact.
- **Tier 2 (inferred):** Most instances — whether the user population has sufficient prior learning requires knowledge beyond the artifact.

## Report Language
**Finding:** No label, icon, affordance, or prompt signals how to achieve [goal], and users cannot reasonably be expected to know how to proceed without one.
**Why it matters:** When no cue exists and users lack sufficient prior learning, they cannot achieve the goal — it is effectively unavailable.
**Confidence:** [Tier 1: Confirmed — no cue present and no alternative path visible / Tier 2: Flagged — confirm whether users have sufficient prior learning]

---

# CHUNK: EFFECTIVELY INVISIBLE ELEMENT

**chunk_id:** trap_effectively_invisible_element_v1
**card:** 2 | **tenet:** Understandable

## Definition (verbatim)
A provided cue (label, icon, affordance, or prompt) is not noticed, or is slow to be noticed, because its appearance or location differs from what the user expects.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The cue IS noticed — if users reliably notice the element, it is not effectively invisible regardless of its placement or appearance.
(b) The cue's appearance and location MATCH user expectations — the definition requires a mismatch. If the cue is where users expect it and looks as they expect, this Trap is not present even if the cue is in a non-central location.

**The key test: does appearance or location differ from what the user expects? If not, this Trap is not present.**

## Example → Rule
**Xbox 360 Search (Y button):** The global search function was placed on the controller's Y button, indicated in a corner of the interface. Users' focus was on the tiles. The cue was effectively invisible. A subsequent search tile solved the problem.
→ *Rule: When a cue is placed outside the user's expected attentional focus — and the interface's dominant interaction pattern directs attention elsewhere — the cue is effectively invisible even when physically present. Adding a cue in the form and location users expect resolves this Trap.*

## Rules
- The Trap covers both complete non-noticing AND significantly delayed noticing — both qualify.
- The cause is always a mismatch between the cue's appearance or location and user expectation.
- The dominant interaction pattern of an interface shapes attentional expectations. Cues deviating from the dominant pattern are at elevated risk.
- A cue that exists but goes unnoticed produces the same user outcome as a cue that does not exist.

## Severity
*Inferred from definition.* An unnoticed critical cue means the user cannot proceed — functionally equivalent to an absent cue. **High severity** when the unnoticed cue is on the critical path to the user's goal.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Whether a cue goes unnoticed depends on where users attend during the task — requires knowledge of user goals and interface patterns, not determinable from artifact alone.

## Report Language
**Finding:** A cue required to achieve [goal] is present in the interface but is likely to go unnoticed because its [appearance / location] differs from what users expect in this context.
**Why it matters:** A cue that users do not notice produces the same outcome as a cue that does not exist — the goal is effectively unreachable.
**Confidence:** [Tier 2: Flagged — confirm attentional focus and expectation mismatch with user observation]

---

# CHUNK: DISTRACTION

**chunk_id:** trap_distraction_v1
**card:** 3 | **tenet:** Understandable

## Definition (verbatim)
Something in the UI suddenly appears or otherwise draws the user's attention, distracting them from their goal.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The attention-drawing element is directly relevant to the user's current goal — the definition specifies distraction FROM the goal. An element helping the user achieve their current goal is not a Distraction even if it draws attention.
(b) Nothing draws the user's attention away from their goal — if attentional focus on the goal is not disrupted, this Trap is not present.

*Note: The card does not provide further boundary conditions. The key test is: does something in the UI draw attention away from what the user is trying to accomplish?*

## Example → Rule
**iPhone GPS + news notification:** iPhone news reader notifications pop up over the GPS mapping application while driving, obscuring driving directions.
→ *Rule: When a UI element appears without user initiation during an active task and physically or cognitively interrupts progress toward the user's goal, a Distraction Trap is present. Severity scales with the criticality of the interrupted task — obscuring navigation while driving is a high-severity instance.*

## Rules
- The trigger can be sudden appearance, motion, sound, or any change that involuntarily captures attention.
- The key criterion is goal interference — the element draws attention away from what the user is trying to accomplish.
- Severity scales with how critical the interrupted task is — the same element may be tolerable in one context and a safety issue in another.

## Severity
*Inferred from definition and example.* The GPS/notification example establishes safety-critical severity. **Variable** — from minor friction to high severity. Flag as high severity when the distracted task is safety-critical or when distraction causes task failure.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Whether something constitutes a Distraction depends on what the user is doing when it appears — requires task context knowledge.
- **Tier 1 (inferred, specific case):** Auto-play audio or video elements are detectable in artifacts and broadly distracting during focused tasks.

## Report Language
**Finding:** [Element] draws user attention away from [goal] by [suddenly appearing / motion / sound] without being directly relevant to what the user is trying to accomplish.
**Why it matters:** Attention capture of this type is involuntary — it cannot be suppressed by user intent regardless of how focused the user is.
**Confidence:** [Tier 1: Confirmed for auto-play audio/video during task flows / Tier 2: Flagged — confirm task context and goal interference]

---

# CHUNK: UNCOMPREHENDED ELEMENT

**chunk_id:** trap_uncomprehended_element_v1
**card:** 4 | **tenet:** Understandable

## Definition (verbatim)
A cue (label, icon, affordance, or prompt) critical to achieving a goal is noticed, but its meaning, or the required method of interacting with it, is unclear.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The cue is NOT noticed — if the cue goes unnoticed, that is Effectively Invisible Element. This Trap requires the cue IS noticed.
(b) Meaning AND required interaction method are BOTH clear — the definition requires that meaning or interaction method is unclear. If users correctly understand both, this Trap is not present.
(c) The cue is not critical to achieving the goal — the definition specifies "critical to achieving a goal." Unclear decorative or non-critical elements do not qualify.

## Example → Rule
**Waze search icon (2016):** Waze changed their search icon from a silhouette of their logo to the very familiar and readily comprehended magnifying glass search icon.
→ *Rule: When a core function uses a brand-specific or non-standard symbol instead of a widely recognized signifier, users notice the element but cannot determine its meaning. Replacing the brand symbol with a conventional signifier resolves the Trap. The speed and ease with which users correctly interpret the replacement confirms the original was an Uncomprehended Element.*

## Rules
- Two sub-types: (1) meaning is unclear, (2) required method of interaction is unclear. Either qualifies.
- The element must be noticed — non-noticing is a different Trap.
- The element must be critical to achieving a goal — unclear non-critical elements do not qualify.
- Universally recognized conventional signifiers (magnifying glass for search) reliably resolve this Trap for that function.

## Severity
*Inferred from definition.* The card specifies "critical to achieving a goal" — when users cannot interpret a critical cue, they cannot achieve their goal. **High severity** when the element is the primary means to a core goal.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** Brand-specific symbols used as functional icons with no conventional equivalent and no text label are high-risk enough to flag from the artifact alone.
- **Tier 2 (inferred):** Most signifiers — whether comprehended depends on user familiarity, which requires knowledge of the user population.

## Report Language
**Finding:** [Element] critical to achieving [goal] is present and noticed, but its meaning or required interaction method is likely to be unclear to users unfamiliar with [this product's / this brand's] conventions.
**Why it matters:** Users who notice but cannot interpret a critical cue are unable to proceed toward their goal.
**Confidence:** [Tier 1: Confirmed for brand symbols used as functional icons without labels / Tier 2: Flagged — confirm with user familiarity assessment]

---

# CHUNK: INVITING DEAD END

**chunk_id:** trap_inviting_dead_end_v1
**card:** 5 | **tenet:** Understandable

## Definition (verbatim)
A cue (label, icon, affordance, or prompt) is incorrectly judged as a means for achieving a goal. It looks right, but is wrong.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The cue IS the correct means for achieving the goal — the definition requires an incorrect judgment. If the cue correctly leads to the goal, this Trap is not present.
(b) The cue does NOT look like the correct means — the definition requires that it "looks right." An element no plausible user pursuing this goal would choose is not this Trap.

**The key test: would a user reasonably and confidently judge this element to be the correct path to their goal — incorrectly?**

## Example → Rule
**Original iPhone iTunes vs. iPod icons:** Users were drawn into the iTunes app instead of the iPod app due to similar icon design. Subsequent changes to the iPod (music) icon have not mitigated this problem.
→ *Rule: When two elements are visually similar and users are trying to reach one, the other becomes an Inviting Dead End. When redesigns fail to resolve the confusion, the visual similarity is persistent and fundamental — significant differentiation is required, not iterative adjustment.*

## Rules
- The user is confident but wrong — this is what distinguishes the Trap from mere confusion.
- The cue has properties (appearance, label, position) that make it a plausible candidate for the user's goal.
- Persistent failure across redesign attempts signals a fundamental differentiation problem.

## Severity
*Inferred from definition and example.* Users expend effort on the wrong path and may not reach the correct one. Severity rises sharply if the wrong path triggers an irreversible action. **Moderate to high** depending on the consequences of the wrong path.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Whether users will judge a specific element as the correct path requires knowledge of user goals and expectations.
- **Tier 1 (inferred, specific case):** When the interface contains error messages amounting to "you should not have done what you just did," this retrospectively confirms the Trap from the artifact.

## Report Language
**Finding:** [Element] is likely to be judged as the correct means for achieving [goal] by users unfamiliar with the system, but leads to [wrong outcome / wrong destination] instead.
**Why it matters:** Users who follow this path will expend effort and lose confidence — and may not find their way to the correct path without assistance.
**Confidence:** [Tier 1: Confirmed when error messages document the wrong path / Tier 2: Flagged — confirm with user task observation]
---

# CHUNK: POOR GROUPING

**chunk_id:** trap_poor_grouping_v1
**card:** 6 | **tenet:** Understandable

## Definition (verbatim)
A critical relationship between two or more otherwise noticeable cues (labels, icons, affordances, or prompts) is not obvious.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The individual cues are NOT noticeable — the definition requires the cues are "otherwise noticeable." If cues go unnoticed, that is Effectively Invisible Element. Poor Grouping is specifically about the relationship between noticeable elements.
(b) The relationship IS obvious — if users correctly and reliably read the relationship between elements, this Trap is not present.
(c) The relationship is not critical — the definition specifies "critical relationship." Unclear relationships between non-critical elements do not constitute this Trap.

**Both required: cues are noticeable AND the critical relationship between them is not obvious.**

## Example → Rule
**Butterfly Ballot (2000 US Presidential Election):** 4,000 people punched the wrong hole believing it represented the second candidate. 19,000 additional voters punched more than one hole. The spatial layout created a false association between candidate names and punch holes. This Trap changed the outcome of the election.
→ *Rule: When the spatial layout of a selection interface creates ambiguity about which control corresponds to which option, a Poor Grouping Trap exists. The individual elements were noticeable — the relationship between them was not. Consequence scales directly with the stakes of the decision being made. When thousands of users make the same error in the same direction, the cause is the design, not the users.*

## Rules
- This Trap concerns relationships between elements, not visibility of individual elements. Both must hold: elements noticeable AND critical relationship not obvious.
- The relationship must be critical to the user's ability to achieve their goal.
- Severity scales with the stakes of the action the grouping supports.
- At scale, a grouping error produces wrong confident action, not mere hesitation.

## Severity
*Inferred from definition and example.* The butterfly ballot establishes extreme severity — changed the outcome of a presidential election. **Variable, scaling with stakes** — from minor hesitation to catastrophic at scale. High severity when a misread relationship leads to confident wrong action on a consequential decision.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** When a control is measurably equidistant between two competing options with no secondary disambiguation cues, the ambiguity is structurally detectable.
- **Tier 2 (inferred):** Most instances — whether spatial ambiguity constitutes a Trap depends on user expectations and task context.

## Report Language
**Finding:** The relationship between [elements] is ambiguous — users are likely to misread which [control / label] corresponds to which [option / action].
**Why it matters:** Users who misread this relationship will take the wrong action with confidence, not uncertainty — and at scale, the consequence scales with the stakes of the decision.
**Confidence:** [Tier 1: Confirmed for measurable equidistance violations with no disambiguation cues / Tier 2: Flagged — confirm with user task observation]

---

# CHUNK: FORCED SYNTAX

**chunk_id:** trap_forced_syntax_v1
**card:** 7 | **tenet:** Understandable

## Definition (verbatim)
The system does not allow the user to issue a command or complete a sequence of actions in the order or manner that is most natural to them.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The system DOES allow the user's natural order or manner — if the interface accepts the sequence or manner the user finds most natural, this Trap is not present even if other orders are also not supported.
(b) There is only one natural order or manner for this task and the system supports it — the definition implies a mismatch between the user's natural approach and what the system requires. If virtually all users naturally approach the task as the system requires, no Forced Syntax exists.

*Note: The card does not specify how many alternative constructions must be supported. The key test is whether the system rejects an order or manner that is natural for a meaningful portion of the user population.*

## Example → Rule
**Alexa voice commands:** "Alexa, what time is it?" works. "What time is it, Alexa?" does not.
→ *Rule: When a system requires a fixed grammatical order that does not match how all users naturally formulate the same request, a Forced Syntax Trap exists for users whose natural order differs. The system accommodates one construction but not another that users commonly use, forcing those users to reorganize their expression before the system responds.*

## Rules
- "Most natural" varies by user and context — a fixed order feeling natural to one user may feel forced to another.
- Voice interfaces are particularly prone because natural language construction varies significantly between users and contexts.
- The Trap exists when the system fails to accommodate a reasonably common natural ordering — not every ordering must be supported.

## Severity
*Inferred from definition.* When the system rejects a user's natural approach, they must either discover the required order or abandon the task. **Moderate severity** — typically causes friction and extra steps; rises to high if users cannot discover the required order.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Whether a fixed sequence is unnatural for real users requires knowledge of how the user population formulates the task — not determinable from the artifact alone.

## Report Language
**Finding:** [Task / Interaction] can only be completed in one order or manner — users who naturally approach this differently will find the system unresponsive to their intent.
**Why it matters:** Users whose natural approach differs from the required one must reorganize before they can proceed.
**Confidence:** [Tier 2: Flagged — confirm alternative natural orderings with user observation]

---

# CHUNK: MEMORY CHALLENGE

**chunk_id:** trap_memory_challenge_v1
**card:** 8 | **tenet:** Understandable

## Definition (verbatim)
The system requires the user to remember information that is easy to forget.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The information is NOT easy to forget — the definition requires the information is easy to forget. If the required information is genuinely easy to remember in context (a user's own name, a daily-use PIN), this Trap is not present.
(b) The system does NOT require the user to remember it — if the interface makes the information available for reference rather than requiring recall from memory, this Trap is not present.

*Note: "Easy to forget" depends on the nature of the information and interaction frequency. Context-free strings, information encountered infrequently, and information requiring recall without retrieval cues are candidates.*

## Example → Rule
**American Express security question:** Users were required to remember not only the answer to their security question but also the security question itself.
→ *Rule: When a security mechanism requires users to recall multiple pieces of self-generated information without any retrieval cue, it creates a compounded Memory Challenge. Requiring recall of context (which question was chosen) in addition to content (the answer) doubles the memory demand. Security mechanisms that ignore memorability will fail users.*

## Rules
- Both conditions required: the system demands recall AND the information is easy to forget.
- Applies to both short-term memory demands (carrying information across screens) and long-term demands (recalling passwords, commands without cues).
- Compounding memory demands — requiring recall of both context and content — significantly increases severity.
- The test: what happens when the user forgets? If they cannot proceed, severity is high.

## Severity
*Inferred from definition and example.* When required information is forgotten and no recovery path exists, task failure results. **High severity** when the forgotten information blocks task completion and recovery is unavailable or difficult.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Whether specific information is genuinely easy to forget for a specific user population at a specific interaction frequency requires knowledge beyond the artifact.
- **Tier 1 (inferred, specific case):** Flows requiring recall of information across screens with no retrieval cue are structurally identifiable in design documentation.

## Report Language
**Finding:** [Task / Step] requires users to recall [information] that is easy to forget, with no retrieval cue or reference available.
**Why it matters:** When users cannot recall required information, they cannot complete the task — and may not know how to recover.
**Confidence:** [Tier 2: Flagged — confirm whether the information is genuinely easy to forget for this user population and interaction frequency]

---

# CHUNK: FEEDBACK FAILURE

**chunk_id:** trap_feedback_failure_v1
**card:** 9 | **tenet:** Understandable

## Definition (verbatim)
The system fails to provide noticeable, comprehensible, and actionable feedback in response to user actions.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) Feedback IS noticeable, comprehensible, AND actionable — all three criteria must be met. If feedback meets all three, this Trap is not present.
(b) No feedback is needed — when the consequence of an action is self-evident from the resulting interface state, the absence of additional feedback does not constitute this Trap.

**Three failure modes — any one constitutes this Trap:**
- Not noticeable (user does not perceive it)
- Not comprehensible (user perceives it but cannot understand it)
- Not actionable (user understands it but does not know what to do next)

## Example → Rule
**Microsoft Word error message:** "Word did not save the document." The message tells users what went wrong without telling them what to do.
→ *Rule: An error message that tells users what went wrong without telling them what to do is a Feedback Failure on the actionability criterion. The test: after reading the feedback, does the user know what action to take? If not, the feedback has failed.*

## Rules
- All three criteria (noticeable, comprehensible, actionable) must be met. Meeting two of three is still this Trap.
- Error messages that describe the problem without specifying a recovery action fail the actionability test — the most common detectable form.
- The actionability test: after reading the feedback, does the user know what to do next?
- Feedback failure is most consequential in error states, where users most need guidance.

## Severity
*Inferred from definition.* When feedback is not actionable after an error, users are left no better off. **High severity** when the failure accompanies a significant or irreversible error state with no other recovery path.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** Error messages are auditable from design files — do they answer both "what happened?" and "what should I do?" This is the most directly detectable form.
- **Tier 2 (inferred):** Whether feedback is noticeable and comprehensible requires knowledge of user attention and familiarity.

## Report Language
**Finding:** When users take [action], the system's feedback fails to be [noticeable / comprehensible / actionable] — specifically: [describe which criterion fails and why].
**Why it matters:** Feedback that does not tell users what to do next leaves them unable to recover from errors or confirm their actions succeeded.
**Confidence:** [Tier 1: Confirmed for error messages that fail to specify a recovery action / Tier 2: Flagged — confirm noticeability and comprehensibility with user observation]

---

# TRAP CHUNKS — COMFORTABLE TENET

---

# CHUNK: PHYSICAL CHALLENGE

**chunk_id:** trap_physical_challenge_v1
**card:** 10 | **tenet:** Comfortable

## Definition (verbatim)
An action the system requires the user to perform is physically effortful, difficult, or impossible.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The required action is NOT physically effortful, difficult, or impossible for the user population in the expected use context — the definition requires physical difficulty. If the action is within normal physical capability for the expected user in the expected context, this Trap is not present.
(b) Physical difficulty is intentional and appropriate to the purpose — contexts where physical challenge is the designed intent (dexterity games, physical training tools) differ from product interfaces where physical effortlessness is the goal.

*Note: "Effortful, difficult, or impossible" represents a severity spectrum — all three qualify as this Trap.*

## Example → Rule
**iPhone lock screen music controls:** Human finger pads are about 12 mm across on average. The music controls were smaller than this. They were difficult to target and were ultimately enlarged.
→ *Rule: Touch targets substantially smaller than the average human finger pad (approximately 12 mm) will produce targeting errors regardless of user skill or motivation. When a design change addressing a physical constraint resolves the difficulty, the original design had a Physical Challenge Trap.*

## Rules
- Three severity levels: effortful, difficult, impossible — all qualify, representing increasing severity.
- 12 mm is the established physical reference point for touch target sizing from the card.
- Some Physical Challenge instances are objectively measurable against known standards (touch target size).
- When a design change addressing a physical constraint resolves user difficulty, the original design had this Trap.

## Severity
*Inferred from definition.* "Impossible" is maximum severity — the user cannot complete the required action. **Scales with difficulty level.** High severity when the action is impossible or produces significant errors for the expected user population.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** Measurable properties (touch target size vs. 12 mm standard, text contrast vs. legibility standards) are checkable from design files.
- **Tier 3 (inferred):** Many instances (weight, reach in realistic conditions, grip ergonomics) require testing on real hardware in real environments.

## Report Language
**Finding:** [Action] imposes a physical demand that exceeds what is comfortable or possible for [the expected user population] in [the expected use context] — specifically: [touch target below 12 mm / text contrast insufficient / control out of reach].
**Why it matters:** Physical barriers cause errors and exclusion regardless of user skill or motivation.
**Confidence:** [Tier 1: Confirmed for measurable violations / Tier 3: Risk noted — confirm with hardware testing for non-measurable properties]

---

# CHUNK: ACCIDENTAL ACTIVATION

**chunk_id:** trap_accidental_activation_v1
**card:** 11 | **tenet:** Comfortable

## Definition (verbatim)
The system misinterprets a user's physical actions resulting in an unintended outcome.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The outcome IS intended — the definition requires an unintended outcome. If the system correctly interprets the user's physical action and produces the intended result, this Trap is not present.
(b) The system does NOT misinterpret — if the physical action unambiguously communicates the user's intent and the system responds correctly, this Trap is not present.

**The key test: did the system produce an unintended outcome by misinterpreting a physical action?**

## Example → Rule
**Kinect gesture interface:** With gesture-based systems, it is often difficult to determine user intent — is a hand gesture a navigational swipe or an effort to scratch one's ear? Scrolling via hand gestures is prone to accidental activations.
→ *Rule: When a system's gesture or input vocabulary overlaps with natural physical behaviors users engage in while using the device, the system will misinterpret those natural behaviors as intentional commands. Gesture and voice interfaces whose activation vocabulary overlaps with natural human behavior will produce accidental activations regardless of recognition sophistication.*

## Rules
- The Trap requires misinterpretation — the system infers intent from a physical action and gets it wrong.
- Gesture and voice interfaces are particularly prone because their input vocabularies overlap with natural human behavior.
- Severity depends entirely on what the unintended outcome is.

## Severity
*Inferred from definition.* Severity scales entirely with the consequence of the unintended action. **Variable** — accidental activation of a minor function is low severity; accidental activation of an irreversible consequential action is high severity.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 3 (inferred):** Accidental Activation requires understanding the full range of physical actions users will perform in realistic conditions — not detectable from a static design file.

## Report Language
**Finding:** [Control / gesture / activation mechanism] is configured in a way that makes unintentional triggering likely when users perform [natural physical behavior] during normal device use.
**Why it matters:** When the system misinterprets natural physical actions as commands, users experience unintended outcomes they did not choose and may not be able to reverse.
**Confidence:** [Tier 3: Risk noted — confirm with hardware testing under realistic use conditions]
---

# TRAP CHUNKS — RESPONSIVE TENET

---

# CHUNK: SLOW OR NO RESPONSE

**chunk_id:** trap_slow_or_no_response_v1
**card:** 12 | **tenet:** Responsive

## Definition (verbatim)
The user is prevented from achieving a goal in a timely manner because of actual or perceived poor system performance.

*Note: In this print version of the card deck, Slow or No Response covers only actual or perceived poor system performance. The captive wait mechanism — where the design intentionally prevents the user from advancing or backing out — is a separate Trap (Captive Wait, card 13).*

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The user IS able to achieve the goal in a timely manner — the definition requires timely goal achievement is prevented. If the system responds within the user's acceptable threshold, this Trap is not present.
(b) The delay is intentional design — intentional prevention of advancing or backing out is Captive Wait, not this Trap. This Trap covers actual or perceived performance failures only.

## Example → Rule
**SuperBright LED Flashlight (Android):** After pressing the button to activate the flashlight application, it can take up to 5 seconds for the light to actually turn on.
→ *Rule: When the time between a user's action and the system's meaningful response substantially exceeds what the user expects for that type of interaction, this Trap is present. A 5-second delay for a flashlight — a tool whose primary use case is immediate illumination — is high severity because the delay defeats the purpose in the contexts where the tool is most needed.*

## Rules
- Both actual and perceived performance failures qualify — perceived slowness is a legitimate form of this Trap even when actual performance is within bounds.
- The gap between what users expect and what they receive defines the Trap — not any absolute threshold.
- Severity scales with how critical timely response is to the use case and context.

## Severity
*Inferred from definition and example.* The flashlight example establishes that a 5-second delay for an emergency-use tool is high severity because it defeats the tool's core purpose at the moment of greatest need. **Scales with use case criticality.** High when the delay defeats the primary purpose of the tool in the context where it is most needed.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** Actual response times are measurable and comparable against expected thresholds.
- **Tier 2 (inferred):** Perceived slowness may require observation to confirm even when actual times are within bounds.

## Report Language
**Finding:** [Interaction / process] takes [observed / estimated duration] to respond — substantially exceeding what users expect for this type of interaction given its purpose and context.
**Why it matters:** Delays that prevent timely goal achievement cause users to abandon tasks, repeat actions unnecessarily, or lose confidence that the system received their input.
**Confidence:** [Tier 1: Confirmed against measurable response time thresholds / Tier 2: Flagged — confirm perceived response quality with user observation]

---

# CHUNK: CAPTIVE WAIT

**chunk_id:** trap_captive_wait_v1
**card:** 13 | **tenet:** Responsive

## Definition (verbatim)
The user is prevented from achieving a goal in a timely manner because the system intentionally prevents them from advancing and/or backing out of a process.

*Note: This Trap is distinct from Slow or No Response. Slow or No Response covers actual or perceived performance failures. Captive Wait covers deliberate design choices that hold the user in a process regardless of system performance.*

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The user IS able to advance or back out at a time of their choosing — the definition requires that the system intentionally prevents advancing and/or backing out. If the user can exit or skip the process, this Trap is not present.
(b) The prevention is not intentional — if the user cannot advance due to a technical performance failure rather than a deliberate design choice, that is Slow or No Response, not this Trap.

**The key distinction from Slow or No Response: Is the user being held by a deliberate design decision, or by a performance failure?**

## Example → Rule
**YouTube unskippable advertisements:** YouTube often presents users with advertisements without providing a means of advancing to the content they are actually interested in.
→ *Rule: When a system deliberately withholds the user's ability to advance or exit a process regardless of system performance, a Captive Wait Trap is present. The user is held not because the system is slow but because the design has chosen to deny them control over their time.*

## Rules
- The defining feature is intentionality — the design deliberately prevents advancing or backing out.
- Captive Wait is not a performance failure; it is a design choice that removes user control over time.
- The consequence is goal delay — the user cannot achieve their actual goal until the system releases them.

## Severity
*Inferred from definition and example.* The user cannot proceed toward their goal until the system releases them. **High severity** when the captive period is long, when the captive content is irrelevant to the user's goal, and when users cannot opt out.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Unskippable sequences are identifiable in design documentation or code. Whether duration and inability to skip constitute a meaningful Trap depends on context and user goals.

## Report Language
**Finding:** [Flow / Screen] prevents users from advancing or backing out for [duration / unknown duration] — not due to system performance but as a deliberate design constraint — without serving the user's current goal.
**Why it matters:** Deliberately withholding user control over time generates frustration disproportionate to the actual duration, because it removes autonomy rather than merely delaying response.
**Confidence:** [Tier 2: Flagged — confirm intentionality of the barrier, duration, and whether a skip option exists]

---

# TRAP CHUNKS — EFFICIENT TENET

---

# CHUNK: UNNECESSARY STEP

**chunk_id:** trap_unnecessary_step_v1
**card:** 14 | **tenet:** Efficient

## Definition (verbatim)
When the product is being used as intended, the number of actual or perceived steps required to achieve a goal is too high.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The steps are necessary — the definition specifies "unnecessary" steps. Steps serving a legitimate purpose (security, safety, error prevention, managing cognitive load) are not this Trap.
(b) The product is NOT being used as intended — the definition specifies this condition. Steps required for edge cases or error recovery may not qualify.

*Note: The card does not specify what makes step count "too high." The key test is whether steps could be eliminated or combined without loss to the quality of the experience.*

## Example → Rule
**Spotify hamburger menu elimination:** Companies discovered that removing the hamburger menu and flattening the hierarchy increases efficiency. Spotify ditched the hamburger.
→ *Rule: When high-frequency functions are placed behind a navigation layer, users must take an additional step to access them on every use. Removing the layer and surfacing functions directly reduces step count and increases efficiency. When a design change reducing hierarchy produces engagement gains, the original hierarchy contained Unnecessary Steps.*

## Rules
- Both actual steps (measurable interactions) and perceived steps (interactions that feel like more work than necessary) qualify.
- The definition applies specifically when the product is being used as intended.
- High-frequency functions buried in navigation hierarchy are the most impactful source of this Trap.
- Engagement gains following step reduction retrospectively confirm the original design had Unnecessary Steps.

## Severity
*Inferred from definition.* Extra steps accumulate across every use. **Scales with frequency** — low-frequency extra steps are lower severity; high-frequency extra steps compounding across many users are higher severity. Task abandonment raises severity further.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Whether steps are genuinely unnecessary requires understanding user goals and whether steps serve a legitimate purpose — not fully determinable from the artifact alone.

## Report Language
**Finding:** [Task / Flow] requires [N] steps to complete when fewer steps would suffice — [describe which steps appear unnecessary and why].
**Why it matters:** Every unnecessary step is a cost paid on every use, compounding across frequency and user base into significant lost efficiency.
**Confidence:** [Tier 2: Flagged — confirm step necessity against user goals and task analysis]

---

# CHUNK: SYSTEM AMNESIA

**chunk_id:** trap_system_amnesia_v1
**card:** 15 | **tenet:** Efficient

## Definition (verbatim)
The system re-prompts the user for information it previously gathered, or otherwise fails to leverage the user's prior work.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The system has NOT previously gathered the information — the definition requires the system previously gathered the information. If the system is prompting for information it genuinely does not have, this is not System Amnesia.
(b) The system IS leveraging the user's prior work — if the system uses previously gathered information appropriately to benefit the user, this Trap is not present.

## Example → Rule
**Xbox website recommending owned game:** The Xbox website used valuable space to sell the user Halo, even though it clearly displayed that the user already owned it. The system had the information — it showed ownership — but failed to use it.
→ *Rule: When a system uses space or attention to present content that its own interface shows is already addressed, it has failed to leverage prior work the user or system has already done. The system had the information needed to avoid the redundancy but failed to use it. When the system displays possessed information while simultaneously acting as if it does not have that information, the Trap is visible in a single screen.*

## Rules
- Two forms: (1) actively re-prompting for information already provided, (2) passively failing to use prior work or preferences.
- Tier 1 detection signal: system displays information it possesses while simultaneously acting as if it does not.
- "Prior work" includes information the user directly provided AND information gathered from user behavior.

## Severity
*Inferred from definition.* The primary cost is efficiency — users must redo already-done work. **Moderate** in most cases; higher when re-prompting forces recreation of significant prior work or when the amnesia produces a clearly wrong result that degrades the experience.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** When the system displays information it possesses while simultaneously requesting or acting contrary to it — as in the Xbox/Halo case — the Trap is visible in the artifact.
- **Tier 2 (inferred):** Other instances require knowledge of what information the system previously collected — not always visible in the artifact.

## Report Language
**Finding:** [Screen / Flow] requests [information] or presents content that the system demonstrably already has — either shown elsewhere in the interface or previously provided by the user.
**Why it matters:** Re-prompting for known information or ignoring prior work forces users to repeat effort they have already invested, signaling that the system is not paying attention.
**Confidence:** [Tier 1: Confirmed when system displays possessed information while simultaneously acting contrary to it / Tier 2: Flagged — confirm what information the system previously collected]

---

# CHUNK: INFORMATION OVERLOAD

**chunk_id:** trap_information_overload_v1
**card:** 16 | **tenet:** Efficient

## Definition (verbatim)
Information presented to the user is comprehensible, but there is too much of it.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) All presented information IS necessary for the user's goal in the current context — the definition requires the information is too much, not merely that it could be shorter. If all presented information serves the user's current goal, this Trap is not present.
(b) The information is NOT comprehensible — if information is present but not understood, that is Uncomprehended Element, not this Trap. Information Overload specifically requires the information is comprehensible.

**The key test: is all of this information necessary for the user's goal right now? If yes, this Trap is not present even if the volume is high.**

## Example → Rule
**Jeep dealer search (2002 vs. 2007):** In 2002, the Jeep website had an extremely wordy description explaining how to find the nearest Jeep dealer. By 2007 this was fixed with a simple zip code entry field.
→ *Rule: When a task requiring only simple input is accompanied by extensive instructions, the instructions constitute Information Overload if the interface is self-explanatory without them. The redesign demonstrates how much information can be removed without loss of usability — often far more than teams assume is possible.*

## Rules
- Specifically about comprehensible information in excess — not about unclear information (that is a different Trap).
- The test for necessity: can users accomplish the goal without this information? If yes, it is a candidate for removal.
- The example shows the gap between what teams assume is necessary and what actually is can be vast.

## Severity
*Inferred from definition.* Excess information slows progress and can cause task abandonment when processing cost exceeds motivation. **Moderate** in most cases — friction and slowed efficiency rather than task failure.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Element count and word count are measurable, but whether specific information is necessary requires knowledge of user goals and context.

## Report Language
**Finding:** [Screen / Section] presents substantially more information than users need to accomplish [primary goal] — [describe excess content and why it appears unnecessary for the goal].
**Why it matters:** Every additional element the user must process beyond what their goal requires is a tax on attention and decision speed that compounds across every use.
**Confidence:** [Tier 2: Flagged — confirm information necessity against user goal analysis]

---

# CHUNK: BAD PREDICTION

**chunk_id:** trap_bad_prediction_v1
**card:** 17 | **tenet:** Efficient

## Definition (verbatim)
The system incorrectly predicts or interprets the user's intent or preference, resulting in the user having to work around the problem.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The prediction IS correct — the definition requires an incorrect prediction. A predictive feature that gets it right is not this Trap.
(b) The user does NOT have to work around the problem — the definition requires that an incorrect prediction results in the user having to work around it. If an incorrect prediction is easily ignored without additional effort, this Trap may not be present.

**The key test: does an incorrect prediction result in the user having to work around it?**

## Example → Rule
**Smartphone autocorrect:** Spelling autocorrection services often make mistakes. When wrong, it is irritating, embarrassing, or insulting.
→ *Rule: The severity of individual wrong predictions varies significantly by the nature of the substitution — not just its frequency. An error rate produces very different user experiences depending on what is being substituted. Three levels from the card: irritating (minor inconvenience), embarrassing (social harm), or insulting (offensive substitution). Consequence type, not just error rate, determines severity.*

## Rules
- The definition requires two conditions: incorrect prediction AND user must work around it.
- Severity of an incorrect prediction scales with the type of error (irritating → embarrassing → insulting) and the reversibility of the resulting action.
- A prediction that creates more work to correct than it saves is a net-negative feature.

## Severity
*Inferred from definition and example.* The card explicitly identifies three consequence levels: irritating, embarrassing, insulting — establishing that severity is variable and depends on error type. **Variable** — from minor friction (irritating) to significant social harm (insulting). High severity when a wrong prediction triggers an action that is irreversible or causes social harm.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Predictive features are identifiable in design files, but whether specific predictions are wrong and how often requires usage data — not determinable from the artifact alone.

## Report Language
**Finding:** [Predictive feature] incorrectly predicts or interprets user intent, requiring users to work around the incorrect result — with consequences ranging from [irritating / embarrassing / insulting] depending on the nature of the error.
**Why it matters:** A prediction that creates more effort to correct than it saves is a net negative. Wrong predictions in social communication contexts can cause embarrassment or offense.
**Confidence:** [Tier 2: Flagged — confirm prediction accuracy rate and consequence of wrong predictions with usage data]

---

# TRAP CHUNKS — FORGIVING TENET

---

# CHUNK: IRREVERSIBLE ACTION

**chunk_id:** trap_irreversible_action_v1
**card:** 18 | **tenet:** Forgiving

## Definition (verbatim)
The system does not allow the user to undo an action they have taken.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The system DOES allow the user to undo the action — the definition requires that undoing is not allowed. If an undo mechanism exists, this Trap is not present.
(b) The action is genuinely technically irreversible AND the user clearly understood and intended permanence — the definition implies the Trap applies when recovery is possible but not supported, or when users arrived at an irreversible action without adequate warning.

*Note: The card does not provide explicit disconfirmation beyond the definition's boundary. The key test is: can the user undo this action? If yes, this Trap is not present.*

## Example → Rule
**Concur iOS travel app (Reserve = Purchase):** Pressing the "Reserve" button not only reserved but also purchased the flight, which could not be undone.
→ *Rule: When a label communicates a lower-commitment action than what the system actually executes, and the result cannot be undone, two failures occur simultaneously: the label misled the user (Inviting Dead End) and the result cannot be reversed (Irreversible Action). The combination is maximally damaging: the user was misled into a consequential action they cannot undo.*

## Rules
- The Trap is about the absence of an undo path — not the nature of the action itself.
- Many actions that appear irreversible could be made reversible with design investment.
- Label-consequence mismatch combined with irreversibility is a particularly damaging combination.
- Severity scales with the stakes of the irreversible action.

## Severity
*Inferred from definition and example.* A purchased flight that cannot be undone establishes high financial and logistical stakes. **Scales with consequences** — high severity when the irreversible action has significant financial, data, or real-world consequences for the user.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Actions lacking visible undo mechanisms are identifiable in design files, but whether a specific action could technically be made reversible requires architecture knowledge.

## Report Language
**Finding:** [Action] cannot be undone — no undo mechanism, cancellation option, or recovery path is provided after the user takes this action.
**Why it matters:** Users who take this action unintentionally or under misapprehension have no path to recovery — the cost of the error is permanent.
**Confidence:** [Tier 2: Flagged — confirm whether a reversibility mechanism could be technically feasible]

---

# TRAP CHUNKS — DISCREET TENET

---

# CHUNK: UNWANTED DISCLOSURE

**chunk_id:** trap_unwanted_disclosure_v1
**card:** 19 | **tenet:** Discreet

## Definition (verbatim)
The system makes the user's data or behavior public in a way that is harmful or embarrassing to the user.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The disclosure is NOT harmful or embarrassing to the user — the definition requires that the disclosure is harmful or embarrassing. If the user would not find the disclosure harmful or embarrassing in the relevant context, this Trap is not present.
(b) The user explicitly consented to the disclosure with full understanding — the definition implies users did not intend or consent to the disclosure. Disclosure users deliberately chose is not this Trap.

*Note: The card does not provide further boundary conditions. The key test: would the user find this disclosure harmful or embarrassing?*

## Example → Rule
**Facebook Beacon:** Shared users' partner-site purchase activities on the news feed on an opt-out basis. Friends were alerted to gifts meant to be surprises. Beacon became the target of a class action lawsuit and Facebook shut it down.
→ *Rule: When a system shares user data or behavior with others on an opt-out basis, it creates Unwanted Disclosure for all users who do not notice or understand the opt-out. Default sharing settings that do not reflect what users would choose if fully informed constitute this Trap. Shutdown following legal action and user backlash retrospectively confirms the Trap at scale.*

## Rules
- Opt-out sharing defaults create this Trap for users who do not notice or understand the default.
- The consequences scale from personal (ruined gift surprises) to legal (class action, shutdown).
- Default settings should reflect what users would choose if fully informed — not what maximizes data sharing.

## Severity
*Inferred from definition and example.* The Facebook Beacon example establishes legal liability and product shutdown as consequences. **Variable** — from minor embarrassment to significant social harm to legal liability. High severity when sensitive behavioral data is shared without consent and consequences are significant.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** Opt-out sharing of user data is detectable in interface design — the default setting is visible.
- **Tier 2 (inferred):** Whether a specific disclosure would be harmful or embarrassing requires knowledge of the social contexts in which the interface is used.

## Report Language
**Finding:** [Feature / setting] shares [data type] with [audience] in a way that users are unlikely to have intended or consented to — specifically: [describe the disclosure mechanism and its default state].
**Why it matters:** Users have no way to prevent disclosures they are not aware of — and consequences range from personal embarrassment to legal liability.
**Confidence:** [Tier 1: Confirmed for opt-out sharing of user behavioral data / Tier 2: Flagged — confirm whether this disclosure would be experienced as harmful or embarrassing in the relevant use context]

---

# TRAP CHUNKS — PROTECTIVE TENET

---

# CHUNK: DATA LOSS

**chunk_id:** trap_data_loss_v1
**card:** 20 | **tenet:** Protective

## Definition (verbatim)
The system can lose the user's work through some action or inaction on the user's part.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The system CANNOT lose the user's work through any action or inaction — the definition requires that data loss is possible through some user action or inaction. If continuous auto-save or equivalent protection is in place and eliminates the risk, this Trap is not present.
(b) The user explicitly and knowingly chose to discard the data — the definition implies unintentional loss. Deliberate deletion that the user intended is not this Trap.

*Note: The card specifies "through some action or inaction on the user's part" — covering both accidental actions that cause loss AND inaction (forgetting to save) that allows loss to occur.*

## Example → Rule
**Windows 8 unexpected shutdown:** Unexpected system shutdowns can cause users to lose any unsaved work. Good user interfaces mitigate this risk by continuously saving users' data.
→ *Rule: When explicit saving is required and unexpected events can prevent saving, data loss is an inherent risk of the design. The card's own resolution — "continuously saving users' data" — establishes continuous auto-save as the standard mitigation. When this is technically feasible and not implemented, the risk exists.*

## Rules
- The Trap covers loss through user action (accidentally deleting) and user inaction (forgetting to save).
- The Trap is present whenever the risk of data loss exists, even if not yet triggered.
- Continuous auto-save is identified on the card itself as the standard mitigation.

## Severity
*Inferred from definition.* The severity scales with the value and irreplaceability of the data at risk. **Scales with data value** — high severity when the data at risk is substantial creative work, important records, or anything that cannot be recreated.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Absence of auto-save mechanisms is identifiable in design documentation. Whether the risk would actually result in loss under realistic failure conditions requires simulation.

## Report Language
**Finding:** User-generated content in [screen / flow] can be permanently lost if [failure mode — session timeout / unexpected shutdown / accidental action] occurs, and no continuous auto-save or recovery mechanism is in place.
**Why it matters:** Data loss is experienced as a fundamental system failure — it destroys trust and requires users to repeat work they have already done.
**Confidence:** [Tier 2: Flagged — confirm auto-save status and failure mode coverage with technical review]
---

# TRAP CHUNKS — HABITUATING TENET

---

# CHUNK: GRATUITOUS REDUNDANCY

**chunk_id:** trap_gratuitous_redundancy_v1
**card:** 21 | **tenet:** Habituating

## Definition (verbatim)
The system presents duplicate cues (labels, icons, affordances, or prompts) for the same action on the same level, or a directly nested level of the UI.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The duplicate cues reach DIFFERENT destinations or trigger DIFFERENT actions — the definition requires duplicate cues for the SAME action. If similar-looking elements lead to different outcomes, this Trap is not present.
(b) The duplicate cues are on DIFFERENT, non-nested levels of the navigation hierarchy — the definition specifies "the same level, or a directly nested level." Cues on entirely separate levels of a hierarchy do not qualify.
(c) Multiple paths exist that serve DIFFERENT ways users naturally construct the same task (e.g., object-first vs. action-first) — the card does not explicitly address this distinction, but the definition's focus on duplication that "impedes habituation" implies paths serving genuinely different mental models are not the target.

**The key structural test: do multiple cues on the same or directly nested level all point to the same destination or action?**

## Example → Rule
**Healthcare.gov (2014):** Three links on the homepage all went to the exact same place. A fourth was subsequently added, exacerbating the issue. This duplication of choices impedes habituation.
→ *Rule: When multiple cues on the same navigation level reach the same destination, the Trap is structurally present and directly detectable. Adding more duplicates does not solve the discoverability problem — it worsens the redundancy. The card itself identifies "duplication of choices impedes habituation" as the direct consequence.*

## Rules
- Directly detectable from structure: multiple cues on the same or directly nested level pointing to the same destination.
- The consequence named on the card is impeded habituation — duplicate choices divide user practice across paths rather than concentrating it on one.
- Adding more duplicates in response to a discoverability problem makes the Trap worse, not better.

## Severity
*Inferred from definition.* The primary cost is impeded habituation — users cannot develop automatic navigation because multiple paths compete. **Moderate** as a primary consequence; severity rises when redundancy also displaces other content or adds decision overhead on high-frequency tasks.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** Multiple cues pointing to the same destination on the same or directly nested level are directly detectable by auditing the design structure. This is among the most structurally detectable Traps in the framework.

## Report Language
**Finding:** [N] separate elements on [screen / level] — [describe them] — all lead to the same destination: [destination]. The duplicate choices add decision overhead without adding destinations.
**Why it matters:** Duplicate paths divide user practice across routes rather than concentrating it, slowing the development of automatic navigation habits.
**Confidence:** [Tier 1: Confirmed — duplicate destinations on the same or directly nested level are directly auditable]

---

# CHUNK: VARIABLE OUTCOME

**chunk_id:** trap_variable_outcome_v1
**card:** 22 | **tenet:** Habituating

## Definition (verbatim)
The system responds differently at different times to the same user action.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The system responds THE SAME WAY to the same user action — the definition requires different responses at different times. Consistent responses are not this Trap.
(b) The variation in response is in degree rather than kind — a scroll that moves faster when flicked harder varies in degree but not in the fundamental nature of the response. The card does not provide this distinction explicitly, but the implied mechanism (mode-based inconsistency) suggests different-kind responses are the target.
(c) The user clearly knows which state the system is in and the different response is therefore expected — the card does not state this explicitly, but the mechanism described (impeded habituation) implies the problem is unexpected variation. If the variation is always expected, it does not impede habituation.

## Example → Rule
**Twitter Back button:** The browser Back button yields a different outcome depending on when it is clicked. After launching a Twitter dialog and then hitting Back, the user is taken back two steps instead of one. This lack of consistency impedes habituation.
→ *Rule: When a navigation control produces different outcomes depending on system state — and users cannot reliably predict which outcome will occur — a Variable Outcome Trap is present. The card identifies "lack of consistency impedes habituation" as the direct consequence. Navigation controls (Back, Home, Close) are particularly damaging instances because users invoke them precisely when they need reliable recovery.*

## Rules
- The definition is simple and strict: same action, different response, different times.
- The consequence named on the card is impeded habituation — users cannot build reliable expectations.
- Navigation and recovery controls (Back, Home) are high-severity instances because reliability is most needed when users are uncertain.
- The Trap is identifiable through code analysis: state-handlers routing the same action to different outcomes are the structural mechanism.

## Severity
*Inferred from definition and example.* The Twitter Back button example is a navigation failure — moderate severity. Severity rises when the inconsistent action is in a safety-critical or high-stakes context. **Variable** — scales with the consequence of the unexpected outcome.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** State-handlers in code routing the same user action to different outcomes are structurally detectable.
- **Tier 2 (inferred):** Whether users will be unaware of the system state that drives the variation requires knowledge of user attention and expectations.

## Report Language
**Finding:** [Action] produces different outcomes depending on [system state / context] — users cannot reliably predict which outcome will occur when they take this action.
**Why it matters:** When the same action produces inconsistent results, users cannot develop reliable habits — and must remain consciously attentive to an interaction that should be automatic.
**Confidence:** [Tier 1: State-handler detected in code or demonstrated in design — same action routes to different outcomes / Tier 2: Flagged — confirm whether users are aware of the state that drives the variation]

---

# CHUNK: WANDERING ELEMENT

**chunk_id:** trap_wandering_element_v1
**card:** 23 | **tenet:** Habituating

## Definition (verbatim)
The physical location of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The cue's location is CONSISTENT across all contexts — the definition requires that location varies across the UI. If the cue appears in the same location in every context where it appears, this Trap is not present.
(b) The cue is low-frequency enough that users would not be expected to develop spatial memory for it — the card does not provide this boundary explicitly, but the consequence (impeded habituation) implies the Trap is most meaningful for cues used frequently enough that spatial habits would otherwise form.

## Example → Rule
**iPhone Edit control:** Placement of the Edit control is inconsistent from one iPhone app to another. Several other functions are similarly inconsistent. This lack of consistency impedes habituation.
→ *Rule: When the same control appears in different positions across different contexts of an interface or ecosystem, users cannot develop spatial memory for it — every encounter requires a small act of conscious search rather than automatic reach. The card identifies "lack of consistency impedes habituation" as the direct consequence. Platform-level controls used across multiple apps are particularly impactful instances.*

## Rules
- Directly detectable: compare control placement across contexts in design files.
- The consequence named on the card is impeded habituation — inconsistent placement prevents spatial memory from forming.
- Platform-level controls appearing across multiple apps in an ecosystem are high-impact instances.
- Standard usability testing following task flows does not reveal this Trap — it requires deliberate cross-context comparison.

## Severity
*Inferred from definition.* Primary cost is impeded habituation for the affected control. **Scales with frequency** — high-frequency controls used constantly across contexts are high-severity instances; low-frequency controls are lower severity.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** Cross-context placement consistency is directly auditable by comparing control coordinates across screens in a design file.

## Report Language
**Finding:** [Control] appears in different positions across [contexts] — users who have learned its location in one context will need to consciously search for it in others.
**Why it matters:** Inconsistent placement prevents spatial memory from forming — every encounter with the control requires conscious search rather than automatic reach.
**Confidence:** [Tier 1: Confirmed — placement inconsistency is directly measurable across screens]

---

# CHUNK: INCONSISTENT APPEARANCE

**chunk_id:** trap_inconsistent_appearance_v1
**card:** 24 | **tenet:** Habituating

## Definition (verbatim)
The visual appearance of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The visual appearance IS consistent across all contexts — the definition requires that appearance varies. If the cue looks the same everywhere it appears, this Trap is not present.
(b) The variation in appearance IS intentional and communicates meaningful information — the card does not explicitly provide this boundary, but it can be inferred from the consequence (impeded habituation) that variation serving a communicative purpose differs from incidental inconsistency.
(c) The cue is low-frequency enough that users would not be expected to develop automatic visual recognition of it.

**Note: Wandering Element and Inconsistent Appearance are distinct.** Wandering Element = same appearance, different location. Inconsistent Appearance = same location (or different location), different visual form. Both can occur simultaneously and each requires separate assessment.

## Example → Rule
**iPhone "New" action:** The new action in iPhone apps sometimes appears as the word "New," while elsewhere it appears as a box with a pen. This lack of consistency impedes habituation.
→ *Rule: When the same action is represented by different visual forms across contexts — a word in some contexts and an icon in others — users must learn multiple representations for the same function and cannot develop a single automatic recognition response. The card identifies "lack of consistency impedes habituation" as the direct consequence.*

## Rules
- Directly detectable: compare visual representation of the same function across contexts in design files.
- Mixing word labels and icons for the same function is a particularly clear instance — word and icon are categorically different visual forms.
- The consequence named on the card is impeded habituation.
- Standard task-based evaluation does not reveal this Trap — it requires deliberate cross-context visual audit.

## Severity
*Inferred from definition.* Primary cost is impeded habituation for the affected function. **Scales with frequency** — functions used constantly across contexts are high-severity instances.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** Cross-context visual consistency is directly auditable by comparing visual representation of recurring functions across screens.

## Report Language
**Finding:** [Function] is represented as [form A] in [context 1] and [form B] in [context 2] — users who have learned to recognize one form will not automatically recognize the other as the same function.
**Why it matters:** Each visual form users must learn for the same function is an additional cognitive investment that consistent design would eliminate — and inconsistency prevents automatic recognition from developing.
**Confidence:** [Tier 1: Confirmed — visual inconsistency is directly auditable across screens]

---

# CHUNK: AMBIGUOUS HOME

**chunk_id:** trap_ambiguous_home_v1
**card:** 25 | **tenet:** Habituating

## Definition (verbatim)
The UI provides no single place the user can return to at any time to begin a new task or get re-oriented.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) A single, clearly defined home EXISTS and is reachable from every context — the definition requires no single such place exists. If a clear, consistent home is present and accessible from anywhere, this Trap is not present.
(b) The product is deliberately designed without a persistent home because all tasks are self-contained — the definition implies hierarchically organized interfaces where orientation is needed. Flat, single-purpose tools may not require a home in the same sense.

## Example → Rule
**Windows 8 dual home experiences:** Windows 8 had two different Start or Home experiences — one for mouse and keyboard, one for touch. Much was the same, some was different. The result was confusion, which has been mitigated in more recent versions.
→ *Rule: When a product provides two or more competing home experiences — particularly across different input modes — users cannot develop a single automatic action for returning to home and getting re-oriented. The card's own framing ("mitigated in more recent versions") confirms that consolidation to a single home resolves the Trap.*

## Rules
- The definition requires a single home reachable at any time. Two competing homes — especially across input modes — directly violates this.
- The Trap can be detected by asking users unprompted where they would go to start a new task. Inconsistent answers confirm it.
- Consolidation to a single home resolves the Trap; improving labeling of multiple homes does not.

## Severity
*Inferred from definition.* When users cannot orient themselves or recover from getting lost, navigation fails entirely. **High severity** in complex products with deep hierarchies where home is the primary recovery mechanism.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 2 (inferred):** Multiple home candidates are identifiable in design files. Whether the ambiguity is actually disorienting for real users requires knowledge of user mental models.

## Report Language
**Finding:** The interface provides [N] locations or experiences that could plausibly serve as home — [describe them] — producing different starting contexts and preventing users from developing a single reliable orientation habit.
**Why it matters:** Without a single reliable home, users who get disoriented must reason their way back rather than reaching automatically — navigation requires conscious attention that a well-designed interface should eliminate.
**Confidence:** [Tier 2: Flagged — confirm user mental models around home with navigation observation]

---

# TRAP CHUNKS — BEAUTIFUL TENET

---

# CHUNK: UNATTRACTIVE APPEARANCE

**chunk_id:** trap_unattractive_appearance_v1
**card:** 26 | **tenet:** Beautiful

## Definition (verbatim)
The UI is aesthetically unpleasing, inconsistent, and/or inappropriate for its intended users.

## DISCONFIRMATION — Apply First
NOT this Trap when:
(a) The UI IS aesthetically pleasing, consistent, AND appropriate for its intended users — all three positive conditions would need to be met to fully rule out this Trap.
(b) Negative aesthetic response reflects unfamiliarity rather than genuine aesthetic failure — the card does not provide this boundary explicitly, but "inappropriate for its intended users" implies audience-relative evaluation. A design appropriate for its intended audience is not this Trap even if others find it unattractive.
(c) Apparent aesthetic problems are entirely attributable to co-occurring functional Traps (clutter from Information Overload, inconsistency from Wandering Element / Inconsistent Appearance) — address functional Traps first and reassess.

**Three dimensions in the definition — any one can constitute this Trap:**
- Aesthetically unpleasing
- Inconsistent (visual inconsistency as an aesthetic failure)
- Inappropriate for intended users

## Example → Rule
**Hi Lo card counting app:** The example app is described as overly cluttered with poor color choice, label justifications, and layout issues.
→ *Rule: When multiple simultaneous aesthetic failures co-occur — clutter, poor color, typography problems, layout issues — they signal overall design investment failure. The example establishes that specific measurable aesthetic failures (poor color choice, misaligned labels, layout problems) constitute this Trap even when overall aesthetic judgment is subjective. Measurable failures are directly detectable.*

## Rules
- Three dimensions: aesthetically unpleasing, visually inconsistent, or inappropriate for intended users. Any one qualifies.
- Some instances are measurable from design files (misalignment, information density, poor color contrast). These are the most directly detectable form.
- "Inappropriate for intended users" is audience-relative — evaluation requires knowledge of the intended audience.
- The card does not address whether pre-launch user feedback is a reliable signal for this Trap — no inference can be made on this point.

## Severity
*Inferred from definition.* The card does not specify severity consequences. *Severity inference is not reliably derivable from card content alone.* The card establishes only that aesthetic unpleasantness, inconsistency, and inappropriateness are Traps — it does not describe the downstream consequences.

## Confidence Tier
*Inferred from definition; no AI detectability section in source.*
- **Tier 1 (inferred):** Specific measurable failures (misalignment, label justification problems, layout density violations) are detectable from design files.
- **Tier 3 (inferred):** Overall aesthetic judgment — whether the design is unpleasing or inappropriate for its intended users — requires cultural knowledge and audience understanding beyond design file analysis.

## Report Language
**Measurable failures (Tier 1):**
**Finding:** The interface exhibits [specific measurable failures — misalignment / poor color contrast / label justification issues / visual clutter] that constitute aesthetic problems independent of overall aesthetic judgment.
**Why it matters:** Measurable aesthetic failures signal design investment problems and are known to affect user perception of overall product quality.
**Confidence:** [Tier 1: Confirmed for measurable failures]

**Overall aesthetic judgment (Tier 3):**
**Confidence:** [Tier 3: Overall aesthetic judgment — whether the design is unpleasing or inappropriate for its intended audience — requires audience and cultural knowledge beyond design file analysis]

