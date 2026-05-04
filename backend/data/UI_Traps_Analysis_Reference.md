# UI Tenets & Traps — AI Analysis Reference

**PROPRIETARY & CONFIDENTIAL — UI Traps LLC**
This file is the condensed AI analysis reference. It is optimized for trap detection from screenshots.
The full manuscript (UI_Tenets_Traps.txt) remains the authoritative human reference.

---

## HOW TO USE THIS REFERENCE

For each trap you assess:
1. Check the **Assessment Tier** first — it tells you whether you CAN assess this trap from a screenshot
2. Read **Can AI Find This?** — it tells you the honest limits of AI detection for this trap
3. Use **What to Look For** to identify visual evidence
4. Apply **Do Not Flag Unless** as a gate before calling any trap
5. Use **Severity Guide** to assign Critical / Moderate / Minor
6. Use **Distinguish From** if you are uncertain between two traps

**Assessment Tier key:**
- **Tier 1:** AI can assess confidently from a single screenshot using visible evidence
- **Tier 2:** AI can assess but needs full task-flow screenshots (flag as `incomplete_flow_findings` if partial)
- **Tier 3:** Requires human judgment — flag with `flagged_for_human_review: true`, do not self-assess
- **Tier 4:** Cannot assess from static screenshots — requires live interaction or timing data

---

## TENET: UNDERSTANDABLE
*"I know what I can do"*

---

### INVISIBLE ELEMENT
**Tenet:** UNDERSTANDABLE
**Assessment Tier:** 1 — AI can assess confidently from a single screenshot

**Definition:** No label, icon, or other interface element is provided to let the user know how to achieve a goal, and the user lacks the prior learning needed to overcome its absence.

**Can AI Find This?**
YES. Given a stated user task, AI can identify when the required action or path has no visible affordance. This is one of the most reliably AI-assessable traps.

**What to Look For:**
- A task the user needs to complete (given their stated goal) that has no visible control, button, link, or affordance to trigger it
- Swipe, gesture, or press-and-hold actions with no visible hint that they exist
- Labels or controls that only appear on hover and are completely absent in the static view
- Navigation options, filters, or actions that are required for the task but entirely absent from the visible UI
- Empty areas of the screen where a control would be expected but none exists

**Examples:**
- A hamburger menu that is the only way to reach a critical feature, with no other visible path
- A pull-to-refresh interaction with no visible indicator that it exists
- A product listing with no visible "Add to Cart" button until the user scrolls — if the button is completely off screen and there is no indicator it exists, this is an Invisible Element

**Severity Guide:**
- **Critical:** The missing element blocks completion of the user's primary stated task entirely
- **Moderate:** The missing element causes the user to take a significantly longer alternate path
- **Minor:** The missing element is for a secondary task or is likely discovered through reasonable exploration

**Do Not Flag Unless:**
- The missing element is relevant to the user's **stated task** (not just any missing feature)
- You have confirmed the element is not present elsewhere on the same screen (e.g., scrolled below the fold does not count as invisible if a scroll indicator is visible)
- The typical user of this product would NOT already know about the invisible interaction from prior experience with the platform

**Distinguish From:**
- **EFFECTIVELY INVISIBLE ELEMENT:** The element IS present on screen but goes unnoticed — if you can see it, it is not Invisible Element
- **INVITING DEAD END:** The element IS present but leads the user the wrong way — if something is there, it is not Invisible Element

---

### EFFECTIVELY INVISIBLE ELEMENT
**Tenet:** UNDERSTANDABLE
**Assessment Tier:** 3 — Requires human judgment. Flag for human review; do not self-assess severity.

**Definition:** A label, icon, or other interface element goes unnoticed because it is unexpected or misaligned with the user's focus of attention.

**Can AI Find This?**
PARTIALLY. AI can identify candidates — elements that are present but positioned far from the likely focus of attention. However, AI CANNOT assess whether a real user would actually miss the element during the task. Attention is determined by what the user is doing in the moment, which cannot be inferred from a static screenshot alone. Always flag candidates for human review; never self-assign severity.

**What to Look For:**
- A critical control that exists on screen but is placed far from where the user's attention would naturally fall during the task
- A status indicator (e.g., mute button, save status) positioned in a screen corner away from the content the user is interacting with
- Small text links placed in areas dominated by larger visual elements, making them easy to overlook
- Error messages or notifications placed outside the user's natural reading flow
- Filter or sort controls that are visually de-emphasized relative to the content they control

**Examples:**
- A "Clear filters" link in small blue text at the top right of a filter panel, far from the filter checkboxes a user just set — the user focused on the checkboxes and never scanned the header area
- A "Save" confirmation that appears briefly in the top corner while the user is focused on a form in the center of the screen

**Severity Guide:**
- ⚠️ **DO NOT assign severity** — this trap requires a human observer to judge whether a real user would miss this element given their actual focus of attention. Flag it with `flagged_for_human_review: true`.

**Do Not Flag Unless:**
- The element IS visually present on the screen (if it is absent, use INVISIBLE ELEMENT instead)
- The element is relevant to the user's stated task
- You can articulate a plausible reason a user's attention would be elsewhere — do not flag simply because an element is small or peripheral

**Distinguish From:**
- **INVISIBLE ELEMENT:** The element does not exist at all on screen
- **DISTRACTION:** Something pulls attention AWAY from the task; Effectively Invisible is about something relevant going UNNOTICED


---

### DISTRACTION
**Tenet:** UNDERSTANDABLE
**Assessment Tier:** 1 — AI can assess from a screenshot when the user's task is stated

**Definition:** Something in the interface draws the user's attention away from their current goal.

**Can AI Find This?**
PARTIALLY. AI can identify visually prominent elements (animated, high-contrast, large) that are unrelated to the user's stated task and positioned in or near the task area. AI CANNOT assess distractiveness without a stated task — something is only a distraction relative to a goal. If no task is stated, do not flag.

**What to Look For:**
- Animated elements (carousels, banners, auto-playing video, blinking badges) near primary task content
- Promotional content or advertisements visually competing with the task flow
- High-contrast or brightly colored elements that are unrelated to the user's current task
- Pop-ups, tooltips, or overlays that appear over task content
- Notification badges or counters on navigation items while the user is mid-task

**Examples:**
- A "Member Days" promotional banner with bright colors and motion positioned directly above a product search result list the user is trying to scan
- A persistent chat widget that overlaps the "Add to Cart" button on mobile

**Severity Guide:**
- **Critical:** The distraction covers or blocks the primary task flow, or causes the user to abandon the task entirely
- **Moderate:** The distraction competes visually with the task area and requires deliberate effort to ignore
- **Minor:** The distraction is present but peripheral, unlikely to significantly derail most users

**Do Not Flag Unless:**
- The user's task is defined — something is only a distraction relative to a goal
- The distracting element is in or near the area the user must focus on to complete their stated task
- The element is visually prominent enough to plausibly compete for attention (do not flag subtle design elements)

**Distinguish From:**
- **INFORMATION OVERLOAD:** Too much content of the same type; Distraction is specifically about attention being pulled OFF the task
- **EFFECTIVELY INVISIBLE ELEMENT:** About something going unnoticed; Distraction is about something being too noticeable


---

### UNCOMPREHENDED ELEMENT
**Tenet:** UNDERSTANDABLE
**Assessment Tier:** 3 — Requires human judgment. Flag for human review; do not self-assess severity.

**Definition:** A label, icon, or other interface element is noticed, but its meaning or required method of interaction is unclear.

**Can AI Find This?**
NO. Whether an element is truly uncomprehended depends entirely on the target user's background knowledge and prior experience — which AI cannot verify. AI can flag elements that appear ambiguous, but cannot determine whether they are actually uncomprehended by the specific user population. Always flag candidates for human review.

**What to Look For:**
- Icons without labels where the icon's meaning is not universally understood
- Labels using technical jargon, internal terminology, or abbreviations unfamiliar to the stated user group
- Controls that look like one type of interaction but work differently (e.g., something that looks like a button but is a drag handle)
- Toggle controls, sliders, or steppers without labels explaining what they control
- Category names or navigation labels that are ambiguous for the stated user type

**Examples:**
- A filter option labeled "SKU" on a consumer-facing shopping site — most shoppers don't know what a SKU is
- A three-line icon that could be a menu, a sort control, or a drag handle with no label

**Severity Guide:**
- ⚠️ **DO NOT assign severity** — flag as a *possible* Uncomprehended Element with `flagged_for_human_review: true`. Human judgment is required to determine whether the element is truly uncomprehended by the actual user population.

**Do Not Flag Unless:**
- The element is genuinely ambiguous to the **stated user type** — do not flag technical terms for technical users
- The element is relevant to completing the user's stated task
- There is no tooltip, label, or context nearby that clarifies the meaning

**Distinguish From:**
- **INVISIBLE ELEMENT:** The element is not present at all
- **INVITING DEAD END:** The user understands the element but it leads somewhere wrong

---

### INVITING DEAD END
**Tenet:** UNDERSTANDABLE
**Assessment Tier:** 3 — Requires human judgment. Flag for human review; do not self-assess severity.

**Definition:** A label, icon, or other interface element is incorrectly judged to be a means of achieving a goal; it looks right but is wrong.

**Can AI Find This?**
NO. AI cannot follow navigation paths or verify what destinations actually contain without additional screenshots of those destinations. AI can flag elements whose labels suggest a plausible match to the user's task but cannot confirm whether the destination actually satisfies it.

**What to Look For:**
- Navigation items or links whose labels suggest they lead to task-relevant content but likely do not
- Buttons or CTAs placed near task content that trigger an unrelated action
- Search results or filter options that appear relevant but lead to a dead end
- "Back" or breadcrumb paths that look like they will return the user to their prior state but do not

**Examples:**
- A "Cat Food" category link that a user clicks expecting to find dry indoor cat food, but which leads to a mixed page of all cat products including toys and litter
- A "Learn More" button near a product that leads to a general marketing page instead of product details

**Severity Guide:**
- ⚠️ **Flag for human review** — requires judgment about whether the element's label genuinely misleads users with the stated task

**Do Not Flag Unless:**
- You can identify the specific element AND articulate why a user with the stated task would plausibly choose it
- The destination or result of following the element is clearly wrong for the task

**Distinguish From:**
- **INVISIBLE ELEMENT:** Nothing is present to guide the user
- **UNCOMPREHENDED ELEMENT:** The user is confused about the element; Inviting Dead End is when it looks clear but is wrong


---

### POOR GROUPING
**Tenet:** UNDERSTANDABLE
**Assessment Tier:** 1 — AI can assess using Gestalt principles

**Definition:** An important relationship between two or more interface elements is unclear.

**Can AI Find This?**
YES. Gestalt principles — proximity, similarity, enclosure, continuity — are rule-based and visible. AI can apply these directly to screenshot evidence.

**What to Look For:**
- Related controls or content that are visually separated (too much space between them)
- Unrelated elements that are placed close together, implying a relationship that doesn't exist
- Labels that are equidistant between two controls, making it unclear which label applies to which control
- Form fields and their labels that are not clearly paired
- Filters or sort controls that are visually disconnected from the content they control
- Action buttons that are spatially separated from the content they act on

**Examples:**
- A price range filter at the top of a sidebar, visually separated from the product list it filters by a wide margin and several unrelated elements
- A "Add to Cart" button positioned below a row of product recommendations rather than clearly adjacent to the product being viewed

**Severity Guide:**
- **Critical:** The grouping failure causes the user to take an action on the wrong item (e.g., add wrong product to cart)
- **Moderate:** The user must spend extra effort determining which elements are related before proceeding
- **Minor:** Grouping is slightly unclear but context or proximity still makes the relationship inferrable

**Do Not Flag Unless:**
- There is a specific, identifiable relationship between two elements that is visually unclear
- Apply Gestalt principles: proximity, similarity, enclosure, continuity — flag when these are violated for related elements

**Distinguish From:**
- **INFORMATION OVERLOAD:** Too much content; Poor Grouping is specifically about unclear relationships between elements
- **UNCOMPREHENDED ELEMENT:** A single element is unclear; Poor Grouping is about the relationship between elements

---

### FORCED SYNTAX
**Tenet:** UNDERSTANDABLE
**Assessment Tier:** 2 — AI can assess but needs full task flow screenshots

**Definition:** A sequence of actions cannot be completed in the order or manner the user expects or prefers.

**Can AI Find This?**
PARTIALLY. A single screenshot rarely reveals Forced Syntax — the trap is about constraints on sequence that only become apparent across multiple steps. AI can assess confidently when provided a complete multi-step flow. If only partial flow is visible, flag as `incomplete_flow_findings`.

**What to Look For:**
- Required fields that must be completed before an action can proceed, where the order feels unnatural
- Multi-step flows that lock the user into a rigid sequence with no way to skip or reorder
- Forms that require information the user doesn't have at that point in the flow
- Filters or options that must be set before a primary action, with no indication of this requirement upfront
- Search or sort requiring specific syntax or format (e.g., exact date format, required quotes)

**Examples:**
- A shopping filter that requires selecting a category before showing any other filters, when the user wants to filter by price first
- A checkout flow that requires account creation before showing shipping options

**Severity Guide:**
- **Critical:** The user cannot complete their task at all without following the forced sequence
- **Moderate:** The user must complete steps in an unexpected order, causing confusion but eventual completion
- **Minor:** A minor constraint on sequence that is mildly inconvenient but quickly understood

**Do Not Flag Unless:**
- You have screenshots showing multiple steps that clearly demonstrate the sequence constraint — stay silent if you only have partial flow evidence
- The sequence constraint is genuinely unexpected for the stated user type and task

**Distinguish From:**
- **UNNECESSARY STEPS:** About the count of steps; Forced Syntax is about the order/manner being constrained
- **MEMORY CHALLENGE:** About remembering information; Forced Syntax is about the sequence being locked

---

### MEMORY CHALLENGE
**Tenet:** UNDERSTANDABLE
**Assessment Tier:** 2 — AI can assess but needs full task flow screenshots

**Definition:** The user is required to remember information that is easy to forget.

**Can AI Find This?**
PARTIALLY. AI can detect Memory Challenge when provided multiple screenshots showing information that appears in one step but is absent in a later step where it is needed. A single screenshot is rarely sufficient to confirm this trap. Flag as `incomplete_flow_findings` if suspected.

**What to Look For:**
- Information shown on one screen that the user must recall on a later screen, with no persistent display
- Codes, IDs, reference numbers, or settings shown temporarily that the user must write down
- Multi-step processes where context from earlier steps is not carried forward
- Search results or comparison views that disappear when the user navigates away
- Configuration or preference screens where current settings are not shown alongside options being changed

**Examples:**
- A product comparison flow where the user must remember specs from one product page while navigating to another, with no side-by-side view
- An order confirmation code shown once that the user must remember to track the order

**Severity Guide:**
- **Critical:** The user must remember information that is critical to completing their task and has no alternative way to retrieve it
- **Moderate:** The user must remember information that creates friction but can be recovered with extra steps
- **Minor:** The user should remember something that is mildly inconvenient to forget

**Do Not Flag Unless:**
- You can identify the specific information the user must remember AND confirm it is not displayed persistently
- The information is genuinely easy to forget (not something universally known or inferable from context)

**Distinguish From:**
- **SYSTEM AMNESIA:** The SYSTEM forgets the user's prior work; Memory Challenge is when the USER must remember
- **INVISIBLE ELEMENT:** The control is missing; Memory Challenge is about information that must be held in mind

---

### FEEDBACK FAILURE
**Tenet:** UNDERSTANDABLE
**Assessment Tier:** 4 — Cannot assess from static screenshots. Requires live interaction.

**Definition:** The system fails to communicate to the user the consequence of their actions, or how to resolve a failed action.

**Important framing:** Feedback Failure is a *lens*, not a mechanism. There is almost always an underlying root trap causing the failure (e.g., INVISIBLE ELEMENT — the feedback indicator is absent; EFFECTIVELY INVISIBLE ELEMENT — the feedback exists but goes unnoticed; INCORRECT INFORMATION — the feedback communicates the wrong thing). When flagging Feedback Failure, try to identify the underlying root cause.

**Can AI Find This?**
NO from static screenshots. Feedback only manifests during interaction — it is the system's response to user action, which cannot be captured in a screenshot of a resting state. AI can flag static evidence suggesting feedback *might* be absent, but cannot confirm.

**What to Look For (for flagging potential instances only):**
- Buttons or controls that appear identical before and after being activated — no visible state change
- Form submission buttons with no loading indicator or confirmation state visible
- Error states where the error message does not appear in the screenshot (absence of feedback after an action)
- Toggle controls that show no visual difference between on/off states

**Examples:**
- A filter checkbox that looks identical whether checked or unchecked
- An "Add to Cart" button that shows no confirmation, loading state, or cart count change after being clicked

**Severity Guide:**
- ⚠️ **Do not assess severity from screenshots** — feedback only manifests during interaction. Note as `incomplete_flow_findings` if you see static evidence suggesting feedback may be absent.

**Do Not Flag Unless:**
- You can see a before/after state in multiple screenshots showing absence of feedback
- Or you can see a control that has no visible active/inactive state distinction

**Distinguish From:**
- **INVISIBLE ELEMENT:** The control to take an action is missing; Feedback Failure is about the response after action
- **SLOW OR NO RESPONSE:** About timing of response; Feedback Failure is about whether feedback is communicated at all

---

## TENET: COMFORTABLE
*"It's physically effortless"*

---

### PHYSICAL CHALLENGE
**Tenet:** COMFORTABLE
**Assessment Tier:** 1 (for sizing/spacing/contrast) / 4 (for ergonomic/posture issues) — see below

**Definition:** Some aspect of the system causes physical discomfort or makes it physically difficult or impossible for the user to complete actions.

**Can AI Find This?**
YES for screen-measurable issues: touch target sizing, spacing between targets, text size. These are visible in screenshots and have measurable standards (44x44px Apple, 48x48dp Material Design).
NO for ergonomic issues: repetitive strain, awkward posture, physical fatigue — these require live interaction or expert evaluation and cannot be assessed from screenshots.

**What to Look For:**
- Touch targets smaller than 44x44px (Apple guideline) or 48x48dp (Material Design) on mobile
- Interactive elements too close together, risking accidental activation of adjacent control
- Text that is too small to read without zooming (below 16px effective size on mobile)
- Horizontal scrolling required on a mobile layout where vertical is expected
- Controls placed at the extreme edges of a large screen requiring a long reach
- Dense form layouts requiring precise tapping in small areas

**Examples:**
- Filter checkboxes on a mobile product listing that are 20x20px with 4px spacing between them
- Navigation links in a footer that are 12px text with no padding, requiring precise tapping

**Severity Guide:**
- **Critical:** A required action cannot be reliably completed due to physical constraints (target too small to reliably hit)
- **Moderate:** The interaction is achievable but requires unusual care or multiple attempts
- **Minor:** Slightly suboptimal sizing or spacing that most users will manage but some will find frustrating

**Do Not Flag Unless:**
- You can see a specific control or target area that is visibly small or cramped
- The issue applies to the stated user's likely device (mobile screenshot vs desktop screenshot)

**Distinguish From:**
- **ACCIDENTAL ACTIVATION:** About triggering the wrong action; Physical Challenge is about difficulty triggering any action
- **INFORMATION OVERLOAD:** About too much content; Physical Challenge is specifically about interaction difficulty

---

### ACCIDENTAL ACTIVATION
**Tenet:** COMFORTABLE
**Assessment Tier:** 2 — Partial assessment possible; full assessment needs interaction

**Definition:** It's easy for the user to unintentionally trigger an action during normal use.

**Can AI Find This?**
PARTIALLY. AI can identify proximity problems — destructive actions placed too close to primary actions. AI CANNOT assess actual accidental trigger likelihood without interaction data. Note: Fitts' Law is two-sided — larger targets are easier to acquire intentionally AND easier to trigger accidentally during adjacent gestures.

**What to Look For:**
- Destructive actions (delete, clear, cancel) placed immediately adjacent to primary actions (save, submit, confirm) with no visual separation
- Swipe-to-delete or swipe-to-action patterns with no confirmation step visible
- Buttons that span large areas of the screen where accidental taps during scrolling are likely
- Drag-and-drop targets immediately adjacent to content the user is reading or selecting
- Form submission adjacent to form clearing

**Examples:**
- A "Clear All Filters" button placed directly next to the "Apply Filters" button with no spacing or visual distinction
- A "Delete Account" option in the same visual weight and proximity as "Save Changes"

**Severity Guide:**
- **Critical:** Accidental activation leads to irreversible data loss or a significantly disruptive outcome
- **Moderate:** Accidental activation is likely and causes rework but is recoverable
- **Minor:** Accidental activation is possible but unlikely, and recovery is easy

**Do Not Flag Unless:**
- You can identify the specific adjacent controls and the action that would be accidentally triggered
- The accidental action would have meaningful negative consequences for the user

**Distinguish From:**
- **IRREVERSIBLE ACTION:** About whether recovery is possible AFTER accidental activation; Accidental Activation is about the risk of triggering it
- **PHYSICAL CHALLENGE:** About difficulty completing intended actions; Accidental Activation is about ease of triggering unintended ones

---

## TENET: RESPONSIVE
*"I don't wait"*

---

### SLOW OR NO RESPONSE
**Tenet:** RESPONSIVE
**Assessment Tier:** 4 — Cannot assess from static screenshots. Requires live interaction or timing data.

**Definition:** The actual or perceived time it takes the system to respond exceeds what the user wants or expects.

**Can AI Find This?**
NO. Response timing cannot be measured from a screenshot. AI can only note the presence of loading indicators that confirm the system itself acknowledges latency.

**What to Look For (for flagging potential instances only):**
- Loading spinners, skeleton screens, or progress bars visible in screenshots — indicates system acknowledges latency exists
- Large numbers of images, carousels, or heavy content that would likely cause slow load times
- Search results pages with no indication of how long search took

**Severity Guide:**
- ⚠️ **Do not assess severity from screenshots.** Note potential performance concerns in `incomplete_flow_findings` only if there is direct visual evidence of loading states.

**Do Not Flag Unless:**
- A loading state IS visible in the screenshot (confirming the system itself acknowledges a wait)
- You have explicit timing information provided by the user

**Distinguish From:**
- **CAPTIVE WAIT:** About being unable to exit a wait; Slow or No Response is about the duration of the wait
- **FEEDBACK FAILURE:** About absence of any response; Slow or No Response is about a response that takes too long

---

### CAPTIVE WAIT
**Tenet:** RESPONSIVE
**Assessment Tier:** 4 — Cannot assess from static screenshots. Requires live interaction.

**Definition:** The system does not allow the user to advance or back out of a process at a time of their choosing.

**Can AI Find This?**
PARTIALLY. AI can flag visible wait states with no exit control. This is Tier 4 because full assessment requires live interaction to confirm the wait is mandatory, but AI can flag candidates from screenshots.

**What to Look For (for flagging potential instances only):**
- Progress bars or loading screens with no visible cancel button or back navigation
- Mandatory onboarding or tutorial flows where skip/exit options are not visible
- Splash screens or interstitials with no close or skip control

**Severity Guide:**
- ⚠️ **Do not assess severity from screenshots.** Flag potential instances in `incomplete_flow_findings`.

**Do Not Flag Unless:**
- A wait state IS visible in the screenshot AND no exit/cancel control is visible

**Distinguish From:**
- **SLOW OR NO RESPONSE:** About duration of wait; Captive Wait is about inability to exit the wait

---

## TENET: ACCURATE
*"I get the truth"*

---

### INCORRECT INFORMATION
**Tenet:** ACCURATE
**Assessment Tier:** 1 — AI can assess when factual errors are verifiable within the screenshot

**Definition:** Information presented to the user is factually wrong, incomplete, out-of-date, or contains errors.

**Can AI Find This?**
PARTIALLY. AI can detect contradictions within the same screenshot or across provided screenshots (e.g., two different prices for the same item). AI CANNOT verify information against external sources or confirm factual accuracy of claims it cannot independently check. Only flag clear visible contradictions or verifiable errors.

**What to Look For:**
- Prices, stock levels, or availability information that appears inconsistent within the same screen
- Contradictory information shown in different parts of the same UI (e.g., price shown differently in product card vs. product detail)
- Dates, deadlines, or time-sensitive information that appears stale (e.g., "Sale ends December 2024" when it is 2026)
- Product specifications that are visibly incomplete (e.g., missing required fields in a product listing)
- Error messages that describe the wrong problem or give incorrect remediation steps

**Examples:**
- A product card showing "$24.99" and the product detail page showing "$29.99" for the same item
- A filter showing "Free Same-Day Delivery" as an option when the product detail page shows "Ships in 5-7 days"

**Severity Guide:**
- **Critical:** The incorrect information directly causes the user to make a wrong decision about their primary task (e.g., wrong price leads to wrong purchase decision)
- **Moderate:** The incorrect information causes confusion or requires the user to verify elsewhere
- **Minor:** A minor factual inconsistency that is unlikely to affect task completion

**Do Not Flag Unless:**
- You can identify the specific piece of information AND explain why it is incorrect or contradictory
- Do not flag information you are uncertain about — only flag clear visible contradictions or verifiable errors

**Distinguish From:**
- **BAD PREDICTION:** The system guesses wrong about user intent; Incorrect Information is about factual content being wrong
- **UNCOMPREHENDED ELEMENT:** The label is unclear; Incorrect Information is about content that is clear but wrong

---

## TENET: EFFICIENT
*"I do less"*

---

### UNNECESSARY STEPS
**Tenet:** EFFICIENT
**Assessment Tier:** 2 — Requires full task flow; single screenshot rarely sufficient

**Definition:** The number of steps a user must take to achieve a goal is greater than it needs to be.

**Can AI Find This?**
PARTIALLY. AI can assess confidently when provided a complete multi-step flow and can identify steps that add no value toward the goal. A single screenshot is rarely sufficient. Flag as `incomplete_flow_findings` if only partial flow is visible.

**What to Look For:**
- Confirmation screens that ask the user to confirm an already-confirmed action
- Multi-page flows for simple tasks that could be completed on one screen
- Required account creation before completing a guest task
- Intermediate "Are you sure?" screens for low-risk actions
- Pagination when infinite scroll or a longer list would eliminate navigation steps
- Steps that collect information already known to the system (e.g., asking for address when it's saved)

**Examples:**
- A cat food filtering flow that requires: (1) select category, (2) select subcategory, (3) select life stage, (4) select brand — when most users just want to filter by one or two criteria simultaneously

**Severity Guide:**
- **Critical:** The unnecessary steps add so much friction that the task is likely to be abandoned
- **Moderate:** 2-4 extra steps that add meaningful time and effort but don't prevent completion
- **Minor:** 1 extra step that is mildly inefficient but quickly completed

**Do Not Flag Unless:**
- You can identify the specific steps AND explain what could be combined or eliminated
- You have enough screenshots to see the full flow — do not speculate about steps not shown
- Flag as `incomplete_flow_findings` if you only see partial evidence

**Distinguish From:**
- **FORCED SYNTAX:** About the ORDER of steps; Unnecessary Steps is about the COUNT
- **INFORMATION OVERLOAD:** About too much content on screen; Unnecessary Steps is about too many screens/actions

---

### INFORMATION OVERLOAD
**Tenet:** EFFICIENT
**Assessment Tier:** 1 — AI can assess from a single screenshot

**Definition:** Information presented to the user is understandable but there's more of it than there needs to be.

**Can AI Find This?**
YES. Visual density and complexity are directly measurable from screenshots. This is one of the most reliably AI-assessable traps. Note: what counts as "overload" is relative to the user's task — rich detail for an expert user may be overload for a novice.

**What to Look For:**
- Product listing pages with too many competing visual elements (images, badges, ratings, prices, labels) making scanning difficult
- Navigation menus with an excessive number of top-level items
- Forms with more fields than necessary for the task
- Filter panels with so many options that selecting the right ones requires significant effort
- Pages that mix multiple distinct tasks or content types without clear hierarchy
- Dense text blocks where key information is not surfaced

**Examples:**
- A PetSmart product listing showing 8 filter categories simultaneously, each with 5-10 options, presented as a flat list with no visual hierarchy
- A product card showing: image, brand name, product name (3 lines), rating, review count, price, sale price, savings amount, loyalty points, free shipping badge, same-day delivery badge — all at the same visual weight

**Severity Guide:**
- **Critical:** The overload prevents the user from identifying what they need to complete their task
- **Moderate:** The user can complete the task but must spend significant effort filtering the noise
- **Minor:** The page is busier than necessary but key information is still findable

**Do Not Flag Unless:**
- The volume of information is genuinely excessive relative to the user's task — don't flag rich content for expert users who need it
- You can identify specifically what information is surplus to the task

**Related Concepts:**
- **Hick's Law:** Decision time increases logarithmically with the number of choices available. A navigation menu with 12 top-level items doesn't take twice as long to parse as one with 6 — it takes logarithmically longer. Use this as a reasoning anchor when assessing whether a number of options constitutes overload.

**Distinguish From:**
- **DISTRACTION:** Specific elements pulling attention away; Information Overload is about volume across the whole screen
- **POOR GROUPING:** About unclear relationships; Information Overload is about sheer quantity

---

### SYSTEM AMNESIA
**Tenet:** EFFICIENT
**Assessment Tier:** 2 — Requires multi-session or multi-step evidence

**Definition:** The system fails to take advantage of the user's prior work, preferences, or context.

**Can AI Find This?**
PARTIALLY. AI can detect System Amnesia when provided multiple screenshots showing evidence that prior state has been lost. A single screenshot cannot reveal this trap. Flag as `incomplete_flow_findings` if you have indirect evidence (e.g., empty fields that should have been pre-populated based on context the user described).

**What to Look For:**
- Filters, sort preferences, or view settings that have reset from a previous session
- Search fields that are empty when the user returns, after they had entered a query
- Previously applied preferences (e.g., size, color) not carried forward to related products
- Account settings or personalization that have reverted
- Shopping cart empty despite a prior session with items added

**Examples:**
- A user who previously filtered for "Adult / Indoor / Under $30" cat food finding all filters reset when they navigate back to the product list
- A user's saved delivery address not pre-populated at checkout despite having ordered before

**Severity Guide:**
- **Critical:** The user must completely redo a significant amount of prior work to continue their task
- **Moderate:** One or two preferences must be re-set, adding meaningful friction
- **Minor:** A minor preference has reset that is quick to restore

**Do Not Flag Unless:**
- You have evidence across multiple screenshots that a prior state has been lost
- Single screenshots rarely reveal System Amnesia — flag as `incomplete_flow_findings` if you have partial evidence

**Distinguish From:**
- **MEMORY CHALLENGE:** The USER must remember; System Amnesia is when the SYSTEM forgets
- **UNNECESSARY STEPS:** About the count of steps generally; System Amnesia specifically about re-doing prior work

---

### BAD PREDICTION
**Tenet:** EFFICIENT
**Assessment Tier:** 1 — AI can assess when prediction results are visible

**Definition:** The system fails in its attempt to anticipate the user's intent, preference, or context; it guesses wrong.

**Can AI Find This?**
YES when prediction results are visible in the screenshot and the user's task is stated. AI can assess whether autocomplete, recommendations, or defaults match the stated task context. Note: do not speculate about predictions not shown — only flag what is visible.

**What to Look For:**
- Search autocomplete suggestions that are clearly irrelevant to the typed query
- Recommended products that don't match the user's stated task or evident browsing context
- Default filter or sort settings that don't match the most common use case
- Autofill suggestions that are incorrect or outdated
- "Customers also bought" or "You might like" recommendations that are off-target
- Default values in forms that are wrong for the majority of users

**Examples:**
- Searching "indoor cat food" and receiving autocomplete suggestions for cat litter and cat toys before cat food
- A "Recommended for You" section showing dog products to a user who has only browsed cat products

**Severity Guide:**
- **Critical:** A bad prediction actively misleads the user or causes them to take a wrong action
- **Moderate:** Bad predictions add noise the user must filter through to find what they need
- **Minor:** A slightly off prediction that the user easily ignores

**Do Not Flag Unless:**
- The prediction is visible in the screenshot and clearly misaligned with the stated user task
- Do not speculate about predictions not shown — only flag what is visible

**Distinguish From:**
- **INCORRECT INFORMATION:** Factual content is wrong; Bad Prediction is about the system's anticipatory behavior being wrong
- **INFORMATION OVERLOAD:** Too much content; Bad Prediction is about relevance of content

---

## TENET: PROTECTIVE
*"I stay in control"*

---

### IRREVERSIBLE ACTION
**Tenet:** PROTECTIVE
**Assessment Tier:** 1 — AI can assess from screenshots

**Definition:** The system does not allow the user to undo or reverse an action they have taken.

**Can AI Find This?**
YES. The absence of an undo mechanism is visible: no "Undo" toast, no confirmation with rollback option, no recovery path in the resulting state. Confirmation dialogs that warn "this cannot be undone" are direct evidence.

**What to Look For:**
- Destructive action buttons (Delete, Remove, Clear, Cancel Order) with no undo option visible in the resulting state
- Confirmation dialogs for destructive actions that warn "this cannot be undone"
- Actions that change system state permanently with no visible rollback path
- Form submissions that cannot be edited after submission
- Filter clearing that removes all applied filters with no undo

**Examples:**
- A "Remove from Cart" button that immediately removes the item with no "Undo" toast or option to re-add
- An "Empty Cart" button with a confirmation dialog that says "This action cannot be undone"

**Severity Guide:**
- **Critical:** The irreversible action results in significant data loss or a major unintended consequence the user cannot recover from
- **Moderate:** The action is irreversible but the consequence is moderate (e.g., removing a saved item)
- **Minor:** The action is technically irreversible but easy to redo (e.g., clearing a search field)

**Do Not Flag Unless:**
- You can identify the specific action AND confirm there is no visible undo mechanism
- The consequence of the irreversible action is meaningful to the user's task

**Note — when a confirmation dialog is insufficient:**
A simple "Are you sure?" dialog does not adequately protect against a truly irreversible, high-consequence action. For destructive operations that cannot be undone (e.g., deleting an account, permanently erasing data), the gold standard (Raskin's non-habituating confirmation) is requiring the user to type a specific word or phrase rather than clicking OK. A click can be triggered by habit or accident; typing a specific word cannot. If a design uses only a click-to-confirm dialog for a high-stakes irreversible action, that itself is a finding worth noting.

**Distinguish From:**
- **DATA LOSS:** About content the user created being lost; Irreversible Action is about a system action that cannot be undone
- **ACCIDENTAL ACTIVATION:** About triggering the action unintentionally; Irreversible Action is about inability to reverse it once triggered

---

### UNWANTED DISCLOSURE
**Tenet:** PROTECTIVE
**Assessment Tier:** 1 — AI can assess from screenshots when disclosure is visible

**Definition:** The system exposes personal data or behavior in a way that is harmful, embarrassing, or unexpected.

**Can AI Find This?**
YES when personal data is visibly present in the screenshot in a context where exposure is unexpected or unwanted. Key principle (Nissenbaum's Contextual Integrity): a privacy violation occurs when data flows outside the context in which it was originally shared. Data that was appropriate to share in one context is a violation when displayed in a different context.

**What to Look For:**
- Personal information (name, address, purchase history) displayed in a publicly visible or shared context
- "Recently viewed" or "Your browsing history" sections visible on a shared or public screen
- Social sharing features that expose more user data than the user would expect
- Default privacy settings that share more than users typically want
- Purchase history or health/personal data shown in a context where others may see the screen

**Examples:**
- A "Recently Viewed" section on a pet store homepage that shows personal browsing history in a layout visible to anyone looking at the screen
- A loyalty program that shows full name and purchase history in a non-private account summary

**Severity Guide:**
- **Critical:** Sensitive personal data (health, financial, private communications) is exposed
- **Moderate:** Personal preferences or behavior are exposed in a way the user may not expect or want
- **Minor:** Minor data exposure unlikely to cause embarrassment or harm

**Do Not Flag Unless:**
- Personal data is actually visible in the screenshot
- The context suggests the exposure is unexpected or potentially unwanted by the user

**Distinguish From:**
- **INCORRECT INFORMATION:** About data being wrong; Unwanted Disclosure is about correct data being shown in the wrong context

---

### DATA LOSS
**Tenet:** PROTECTIVE
**Assessment Tier:** 2 — Often requires multi-step evidence; partial assessment from single screenshot

**Definition:** The system fails to retain information or content the user expects to be preserved.

**Can AI Find This?**
PARTIALLY. AI can identify design patterns that put data at risk (long unsaved forms, absent save mechanisms) even from a single screenshot. But confirming actual loss requires multi-step evidence. Flag risk patterns as findings even without confirmation.

**What to Look For:**
- Forms with no auto-save that are long enough that a navigation away or timeout would lose all entered data
- Draft or in-progress content with no visible save mechanism
- Shopping cart items disappearing on navigation (evidence across multiple screenshots)
- Uploaded files or attachments not persisted after a page reload
- Filters or search queries lost when navigating back

**Examples:**
- A long checkout form with no auto-save indicator, where navigating back would lose all entered information
- A product review form with no draft save functionality

**Severity Guide:**
- **Critical:** The user loses significant work they cannot recover (long form, uploaded file, composed content)
- **Moderate:** The user loses moderate work requiring 2-5 minutes to redo
- **Minor:** The user loses minimal work (a short form, a search query)

**Do Not Flag Unless:**
- You can identify specific content that would be lost AND confirm there is no save mechanism visible
- The loss would be unexpected to the user

**Distinguish From:**
- **SYSTEM AMNESIA:** About preferences and context not being remembered across sessions; Data Loss is about active work being destroyed
- **IRREVERSIBLE ACTION:** About actions that cannot be undone; Data Loss is about content not being saved

---

## TENET: HABITUATING
*"It becomes automatic"*

The HABITUATING tenet is organized around three sub-properties:
- **Non-Redundant** → Gratuitous Redundancy
- **Consistent with Expectations** → Variable Outcome, Wandering Element, Inconsistent Appearance
- **Oriented** → Ambiguous Home

Habituation is built through the Power Law of Practice: mastery accumulates through repetition of the same action in the same context. Any trap in this tenet disrupts that accumulation — either by giving the user too many paths (redundancy), by making the path change (inconsistency), or by removing the anchor from which all navigation flows (ambiguous home).

---

### GRATUITOUS REDUNDANCY
**Tenet:** HABITUATING
**Assessment Tier:** 1 — AI can assess from a single screenshot

**Definition:** Multiple instances of the same interface element are presented to the user at the same time.

**Can AI Find This?**
YES. Duplication of the same element is directly visible in screenshots. This is one of the most reliably AI-assessable habituation traps.

**Key distinction — grammatical vs. gratuitous redundancy:**
Not all redundancy is a trap. *Grammatical redundancy* (offering both a menu item and a keyboard shortcut, or both a button and a right-click option) routes users through different paths to the same destination and is acceptable — these serve different user modes. *Gratuitous redundancy* duplicates the same element on the same path, forcing the user to choose between functionally identical options with no meaningful difference. Same destination, same path, multiple instances = gratuitous.

**Why it matters:**
The Power Law of Practice means repetition of the same action in the same way builds mastery. When two paths lead to the same place, users cannot habituate to either one — they must decide each time which to use, preventing the automation that makes interfaces feel effortless. Gratuitous Redundancy is also frequently a gateway trap: teams add redundancy to work around confusing taxonomy or navigation, masking underlying POOR GROUPING or AMBIGUOUS HOME problems.

**What to Look For:**
- The same action available in multiple places on the same screen without clear reason
- Navigation items duplicated in both a top nav and a sidebar leading to the same destination
- The same product information repeated multiple times in different sections of a page
- Multiple "Add to Cart" buttons for the same item on the same screen view
- The same call-to-action appearing in the header, body, and footer of a single page
- Multiple links or paths to the same destination within a single navigation context (e.g., Healthcare.gov with 3-4 links to the same page within a single menu)

**Examples:**
- A product detail page showing "Add to Cart" in the product hero, in a sticky bar, AND in a "You Might Like" section below — all for the same product, creating visual noise without adding value
- A filter panel showing "Sort by: Relevance" both in a dropdown and as a selected chip simultaneously
- A medical website with six different "Find a Location" links on the same page, each pointing to the same destination

**Severity Guide:**
- **Critical:** The redundancy causes the user to be confused about which instance to use, leading to errors
- **Moderate:** The redundancy adds visual noise that slows task completion
- **Minor:** Redundancy is present but doesn't meaningfully impede the user

**Do Not Flag Unless:**
- The same element appears multiple times AND there is no clear reason for the duplication (i.e., it is not serving different contexts or user needs)
- Intentional redundancy (e.g., mobile vs desktop nav, skip links for accessibility, keyboard shortcut alongside menu item) should not be flagged

**Distinguish From:**
- **INFORMATION OVERLOAD:** About volume of different content; Gratuitous Redundancy is specifically about the same content repeated
- **DISTRACTION:** About attention being pulled off task; Gratuitous Redundancy is about duplication specifically
- **AMBIGUOUS HOME:** When the redundancy involves competing starting points for navigation

---

### VARIABLE OUTCOME
**Tenet:** HABITUATING
**Assessment Tier:** 2 — Requires multi-step or multi-session evidence

**Definition:** The system responds differently and unexpectedly to the same user action at different times.

**Can AI Find This?**
PARTIALLY across multiple screenshots showing the same action producing different visible results. NO from a single screenshot. The most detectable form of this trap is visible mode indicators: if a mode exists that changes behavior but the mode indicator is absent or effectively invisible, flag that combination. For code review: scan state-handlers for places where the same action produces different branches.

**Key framing — mode errors:**
The most common cause of Variable Outcome is a mode error: the user has a mental model of the system state that doesn't match the actual state. CapsLock is the canonical example — the key produces different output depending on an invisible mode. Mode errors are particularly dangerous because the user receives identical feedback for the action regardless of which mode is active, making the inconsistency hard to detect. When Variable Outcome is present, look for: (1) whether a mode indicator exists, and (2) whether that indicator is effectively invisible (small, peripheral, easy to miss).

**What to Look For:**
- Identical controls that appear to behave differently depending on context, with no visible indicator of the difference
- Mode-dependent behavior where the mode is not clearly communicated
- Inconsistent results from repeated searches or filters
- Actions that sometimes require confirmation and sometimes don't
- A mode indicator that is present but visually de-emphasized (often also an EFFECTIVELY INVISIBLE ELEMENT)

**Examples:**
- A "Save" button that sometimes saves immediately and sometimes opens a dialog, with no visible indication of which will happen
- A product search that returns different results for the same query depending on whether filters are active, with no clear indication filters are in effect
- The iPhone's "shake to undo" gesture working inconsistently across apps — same gesture, different results
- The 2016 Chrysler Pacifica monostable gear shifter: the same physical motion produced different gear states depending on a non-obvious system mode; contributed to multiple deaths and a 1.1M vehicle recall

**Severity Guide:**
- **Critical:** The variable outcome causes the user to take a significantly wrong action (particularly when the inconsistency affects safety-critical or destructive operations)
- **Moderate:** The variable outcome causes confusion and requires recovery effort
- **Minor:** The variable outcome is surprising but quickly understood

**Do Not Flag Unless:**
- You have multi-step evidence showing the same action producing different outcomes
- Single screenshots rarely reveal Variable Outcome — flag as `incomplete_flow_findings` if suspected
- If flagging a mode error, confirm the mode indicator is absent or effectively invisible

**Distinguish From:**
- **FEEDBACK FAILURE:** About absence of feedback after an action; Variable Outcome is about inconsistent results across multiple actions
- **INVISIBLE ELEMENT:** About hidden functionality; Variable Outcome is about unpredictable behavior of visible functionality
- **EFFECTIVELY INVISIBLE ELEMENT:** Often the root cause when a mode indicator exists but goes unnoticed


---

### WANDERING ELEMENT
**Tenet:** HABITUATING
**Assessment Tier:** 2 — Requires multi-screenshot evidence showing the same element in different locations

**Definition:** The same interface element is presented in a different location at different times.

**Can AI Find This?**
PARTIALLY. AI can detect Wandering Element when provided multiple screenshots of the same element in different positions. A single screenshot CANNOT reveal this trap. Note: like Inconsistent Appearance, this trap is invisible to task-based evaluation — a user completing one task will encounter controls in one location and won't see that they appear elsewhere. Full detection requires a cross-context audit, not a task walkthrough.

**Why it matters:**
Humans form spatial memories for frequently used objects automatically. When a control appears in the same place every time, users reach for it without thinking. When it wanders, that spatial memory misfires — the user looks where the control was, finds nothing, and must consciously search. This is exactly the conscious deliberation that habituation is designed to eliminate. The Power Law of Practice cannot accumulate around a moving target.

**What to Look For:**
- Navigation items that change position between pages
- Action buttons (save, submit, cancel) in different locations on different steps of a flow
- The same filter or sort control appearing in different positions across different category pages
- Search bar that moves between pages (top of page on one screen, sidebar on another)
- The "Edit" control appearing at the top of one screen and the bottom of another

**Examples:**
- An "Add to Cart" button at the bottom right of the product card on the listing page, but at the top left on the product detail page
- A "Back" button that appears in the top left on most screens but the bottom center on one specific step
- iOS apps that inconsistently place search, filter, and "New item" controls in different positions across screens — users learn the position on one screen and look there on every other screen

**Severity Guide:**
- **Critical:** The element moves to a location where users consistently cannot find it, blocking task completion
- **Moderate:** The movement causes noticeable confusion and search behavior
- **Minor:** A subtle position change that most users adapt to quickly

**Do Not Flag Unless:**
- You have multiple screenshots of the same element in different positions
- A single screenshot cannot reveal Wandering Element — note as `incomplete_flow_findings` if suspected

**Distinguish From:**
- **INCONSISTENT APPEARANCE:** The element looks different; Wandering Element is specifically about position changing
- **INVISIBLE ELEMENT:** The element is absent; Wandering Element is about it being in the wrong place

---

### INCONSISTENT APPEARANCE
**Tenet:** HABITUATING
**Assessment Tier:** 1 within provided screenshots / full system requires cross-context audit (see note)

**Definition:** The same interface element is presented in a different visual or auditory style at different times.

**Can AI Find This?**
PARTIALLY. AI can detect visual inconsistencies within the set of provided screenshots. However, the full scope of this trap is invisible to task-based evaluation — a user completing one task sees controls in their forms for that task, and whether those same controls appear differently in other parts of the system is not visible in that flow. Full detection requires a cross-system visual audit, not a task walkthrough. Flag what is visible; note the limits of the assessment.

**Key effect:**
Inconsistency doesn't just slow habituation — it can temporarily break it. A user who has learned to recognize a control in one form may not recognize it in another form. The inconsistency requires the user to stop, identify, and consciously decide whether this is the same thing they have encountered before. Habit has failed and deliberation has resumed.

**What to Look For:**
- Buttons that perform the same function but have different colors, sizes, or styles across the UI
- Links styled inconsistently (some underlined, some not, some blue, some black)
- Icons for the same action rendered differently in different parts of the interface
- Heading styles that vary inconsistently across sections of the same page
- Form field styles that differ between sections without clear reason
- Two products shown with different amounts of information in their cards on the same listing page
- A mix of modern and legacy design language for equivalent controls (different visual eras in the same product)
- Sounds or audio cues for the same event that differ across contexts (e.g., a success chime in one flow, a different tone in another for the same outcome)

**Examples:**
- Primary "Add to Cart" buttons that are blue on one product card and orange on another on the same listing page
- Filter checkboxes that are square on the sidebar but round on the mobile filter overlay
- The Windows operating system (as of 2026): users navigating settings encounter modern Fluent Design menus alongside legacy Control Panel windows using 1990s-era 3D buttons and icons. Neither is incomprehensible in isolation, but no single automatic response can serve both
- iPhone apps inconsistently representing "New item": sometimes as the word "New," sometimes as a box-with-pen icon — users must re-identify the control each time

**Severity Guide:**
- **Critical:** The inconsistency directly causes the user to misidentify an element's function or status
- **Moderate:** The inconsistency creates confusion about whether elements are related or equivalent
- **Minor:** A minor style variation that doesn't affect comprehension

**Do Not Flag Unless:**
- You can identify the same element appearing with different visual treatments within the same session
- The inconsistency is meaningful — minor brand variation across sections is not the same as functionally misleading inconsistency

**Distinguish From:**
- **WANDERING ELEMENT:** About position; Inconsistent Appearance is about visual style
- **POOR GROUPING:** About unclear relationships; Inconsistent Appearance is about inconsistent visual treatment of equivalent elements

---

### AMBIGUOUS HOME
**Tenet:** HABITUATING
**Assessment Tier:** 1 — AI can assess from screenshots

**Definition:** The interface lacks a single, clear starting point that users can reliably return to from anywhere with one consistent action.

**Can AI Find This?**
YES. Competing navigation systems and multiple plausible starting points are directly visible in screenshots. This is one of the more reliably AI-assessable habituation traps.

**Key framing:**
A well-oriented interface provides a spatial and navigational anchor — a single home from which all habituation flows. When home is unambiguous, returning to it becomes one of the most deeply automatic actions a user can perform: same destination, same action, every time. When home is ambiguous, the user must consciously reason about where to go to start or restart — exactly the deliberation that habituation is designed to eliminate.

Ambiguous Home has two root causes, each from a different sub-tenet:
- **Multiple homes** = a Gratuitous Redundancy problem (too many starting points)
- **Inconsistent home action** = a Consistent Appearance/Variable Outcome problem (the way to reach home keeps changing)

**Recovery point:**
Home is not just where tasks begin — it is where users return when lost. Getting disoriented in an interface is a common experience. A single, always-accessible home makes recovery automatic: one action, same place, every time. Without it, users must reason their way back, which is the opposite of what a habituating interface should require. When assessing Ambiguous Home, consider not just task initiation but also whether the interface provides a reliable escape when the user doesn't know where they are.

**What to Look For:**
- Multiple navigation systems (top nav, sidebar nav, breadcrumb, bottom nav) that suggest different starting points
- Duplicate category structures in different parts of the interface
- A homepage or landing page where it is unclear where the primary task begins
- Multiple search bars serving the same or unclear purposes
- Competing CTAs of equal visual weight on a page where one should be primary
- A "Home" icon in a place users wouldn't expect, competing with a "Library" or "Dashboard" as the primary starting point

**Examples:**
- A product listing page with both a sidebar category tree AND a horizontal top-nav category bar AND breadcrumbs — three different navigation systems suggesting different "home" points
- A page with "Browse by Category", "Shop All", and "Featured Collections" all presented as equally primary starting points
- Windows 8: two different Start/Home experiences — one for mouse/keyboard, one for touch — sharing some structure but diverging enough to prevent a single automatic response
- Early Meta VR headsets (Oculus Rift era): three separate "homes" — a Library button (most users' mental starting point), an Explore button (represented by a home icon), and a Home button for the VR space itself. Later consolidated to a single unified home screen in the Quest
- Oculus Rift 2017: three separate homes confused users → Quest reduced to one

**Severity Guide:**
- **Critical:** The user cannot determine where to begin their task, causing abandonment
- **Moderate:** The user is slowed by uncertainty about which navigation path to follow
- **Minor:** Mild navigation ambiguity that most users resolve quickly

**Do Not Flag Unless:**
- Multiple competing navigation or orientation systems are visibly present
- The competition is at the same visual level — a primary nav and a secondary breadcrumb are not competing

**Related Traps (often co-occur):**
- **POOR GROUPING:** When multiple locations offer partially overlapping capabilities, users can't build a reliable mental model for where to go when
- **MEMORY CHALLENGE:** Without a clear home, users must remember where they are and how to get back
- **VARIABLE OUTCOME:** If the home action doesn't reliably take the user home, they won't habituate to its use
- **GRATUITOUS REDUNDANCY:** Duplicate means of re-orienting slow the habituation of any single path

**Related Concepts:**
- **Spatial Memory** (Scarr, Cockburn & Gutwin, 2013): Humans form spatial memories for frequently used objects and locations automatically and without effort. A stable home leverages this capacity — users navigate back to it without conscious thought. Ambiguous Home prevents spatial memory from forming around any single anchor point.

**Distinguish From:**
- **INFORMATION OVERLOAD:** About too much content generally; Ambiguous Home is specifically about competing orientation/navigation systems
- **POOR GROUPING:** About unclear element relationships; Ambiguous Home is about unclear starting points for tasks

---

## TENET: BEAUTIFUL
*"It's aesthetically pleasing"*

---

### POOR AESTHETIC
**Tenet:** BEAUTIFUL
**Assessment Tier:** 3 — Requires human judgment. Flag for human review; do not self-assess severity.

**Definition:** The system's sensory design, style, personality, or tone is judged as unpleasing or inappropriate by its intended users.

**Can AI Find This?**
ONLY FOR OBJECTIVE VIOLATIONS. AI should not flag Poor Aesthetic based on subjective judgment. The only cases where AI should raise this trap are specific, measurable violations: color contrast failures (WCAG standards), text that is illegible due to color choice, or visual design that is objectively broken (e.g., overlapping elements, unreadable text on background). For all holistic aesthetic judgment — overall attractiveness, appropriateness, tone, brand fit — stay silent and leave it to human review.

**Important:** You cannot reliably test for beauty before shipping. User feedback on aesthetics often reflects resistance to the unfamiliar rather than a reliable signal about lasting response. The Motorola Razr and Aeron chair both received broadly negative pre-launch aesthetic feedback and became defining products of their eras.

**Two dimensions of this trap:**
1. **Attractiveness** — the design is visually unpleasant
2. **Appropriateness** — the design is mismatched to its context, audience, or purpose

Both can fail independently. A design can be skillfully executed but wrong for its audience. Appropriateness is also time-sensitive: what feels current today can feel dated in three years. Tracking it requires knowing where aesthetic trends are going, not just where they have been.

**What to Look For:**
- Jarring color combinations or color choices clearly misaligned with the brand or product category
- Typography that is difficult to read or inconsistent with the tone of the product
- Layout that feels crowded or imbalanced in a way that affects overall perception
- Visual design that feels significantly dated relative to the stated user group's expectations
- Tone of copy that feels inappropriate for the context (too casual for a professional tool, too formal for a consumer app)
- Voice/personality mismatched to the product context (sycophantic, aggressive, or incongruent tone)

**Examples:**
- A children's educational app using dark, high-contrast corporate color schemes
- A premium luxury product using clip-art style product images
- The ChatGPT-4o 2025 update was broadly described as sycophantic — its personality tone was judged as mismatched to user expectations for a professional AI assistant. OpenAI rolled back the update within one week of release
- Voice assistants that present happy and sad information with the same intonation — prosody is aesthetics too
- Komar & Melamid (artists) commissioned large-scale surveys to identify the most and least liked components of paintings, then painted the statistically ideal picture. The results — blue-green landscapes with George Washington, grazing deer, and wholesome families — satisfied every measured preference and were clearly awful. Aggregating user aesthetic preferences does not produce beauty. This is why "test for aesthetics with users" is unreliable guidance.

**Severity Guide:**
- ⚠️ **DO NOT assign severity** — aesthetic judgment requires knowing the intended user group's taste and expectations, which cannot be assessed from screenshots alone. Flag with `flagged_for_human_review: true`.

**Do Not Flag Unless:**
- The aesthetic issue is pronounced enough that it would be broadly agreed upon — do not flag subjective preferences
- You can articulate why the aesthetic is misaligned with the stated user group specifically

**Related Concepts:**
- **Aesthetic-Usability Effect** (Tractinsky, Katz & Ikar, 2000; replicating Kurosu & Kashimura, 1995): Users perceive attractive interfaces as easier to use — and the relationship runs both directions. More usable interfaces are also perceived as more beautiful. Functional and aesthetic failure tend to co-occur: fix the other eight Tenets and aesthetic quality improves; neglect them and aesthetic quality suffers regardless of visual execution.
- **Processing Fluency:** Stimuli that are easy to process feel more pleasant. This underlies preferences for symmetry, clear visual hierarchy, and gestalt-respecting layouts — all of which reduce cognitive friction and increase perceived attractiveness.

**Distinguish From:**
- **INCONSISTENT APPEARANCE:** About functional inconsistency of elements; Poor Aesthetic is about the overall sensory quality
- **INFORMATION OVERLOAD:** About too much content; Poor Aesthetic is about the quality of the design, not the quantity
- **PHYSICAL CHALLENGE:** Specific measurable issues like color contrast and text readability are better classified there


---

## REVIEW NOTES FOR STEVE AND MIKE

The following sections need your input most urgently. Sections marked ⚠️ in the document above are where AI judgment is most unreliable and your corrections will have the biggest impact on analysis quality.

### Highest Priority — Confirm or Correct These

1. **EFFECTIVELY INVISIBLE ELEMENT severity** — This is the #1 source of false positives. The current draft says "never assign severity, always flag for human review." Is that the right call, or are there specific sub-cases where AI CAN be confident?

2. **POOR AESTHETIC** — Should this be completely suppressed from AI output? Or should AI flag only objective violations (contrast ratios, readability) and route everything else to human review?

3. **FORCED SYNTAX / VARIABLE OUTCOME / WANDERING ELEMENT** — All Tier 2/3. The draft says "flag as incomplete_flow_findings if you only see partial evidence." Is that the right behavior or do you want AI to stay silent on these entirely?

4. **Severity thresholds across all Tier 1 traps** — The Critical/Moderate/Minor criteria in this draft are the weakest part. They're logical but not validated against your real test cases. For each trap you've tested, please note: "Claude called this X severity, correct answer was Y severity, because Z."

5. **DISTRACTION tier** — Currently Tier 1 (assessable when task is stated). The book implies it may require knowledge of the user's goals outside the product, making it Tier 3 for some cases. Please confirm: should AI assess this when the task is stated, or always route to human review?

6. **PHYSICAL CHALLENGE carve-out** — Currently split (Tier 1 for sizing/spacing, Tier 4 for ergonomics). Please confirm this is the right split. Should AI flag any visible sizing issue, or only when it clearly violates published guidelines (44px, 48dp)?

### Lower Priority — Fill In When You Can

7. **Additional examples** — For every trap, 1-2 more real-world examples from your actual test cases would significantly improve accuracy. The examples currently in this draft are generic; yours are calibrated to real usage.

8. **False positive patterns** — For any trap where Claude has flagged something incorrectly in a real analysis, document it here: "Claude flagged X as [trap], but it wasn't because Y." These become the best "Do Not Flag Unless" guard conditions.

9. **Trap interaction patterns** — When multiple traps appear together in your real analyses, which combinations are most common? That helps Claude decide between related traps.

10. **CAPTIVE WAIT "Can AI find this?"** — The book source had "xxx" for this section, suggesting it was unfinished. Please advise on what visual evidence should trigger a flag.

11. **INCORRECT INFORMATION Canada Airlines example** — Referenced in prior session as a strong example. Please add when you have it.
