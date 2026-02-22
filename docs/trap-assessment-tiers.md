# Trap Assessment Tiers

> **Living Document** — Last updated: 2026-02-21
>
> This classification may evolve as AI capabilities improve or our understanding deepens.

## Overview

Not all UI Traps can be reliably detected by AI analysis of static screenshots. This document classifies the 27 UI Traps into four tiers based on what type of evidence and judgment is required to assess them.

### The Core Problem

AI vision models can identify visual patterns, but they cannot:
- Know what humans have learned over a lifetime of using interfaces
- Understand cultural conventions and regional terminology
- Predict human attention patterns and scanning behavior
- Experience timing, system responsiveness, or live interactions

This leads to **false positives** when AI asserts findings about things that require human judgment.

### The Solution

Classify traps by assessment requirements and adjust AI behavior accordingly:
- **Tier 1**: Assert findings confidently
- **Tier 2**: Caveat that complete flows may reveal more
- **Tier 3**: Flag for human review, don't assert
- **Tier 4**: Explicitly state cannot assess from screenshots

---

## Tier 1: AI-Assessable (Rule-Based, Single/Few Screenshots)

**AI behavior**: Assert findings confidently with evidence.

These traps are objective and rule-based. AI can assess them from visible evidence in one or a few screenshots.

| Trap | Why AI Can Assess | Evidence Required |
|------|-------------------|-------------------|
| **INVISIBLE ELEMENT** | Literally not visible | Element absence in screenshot |
| **PHYSICAL CHALLENGE** | Measurable | Touch targets < 44px, contrast ratios, text size |
| **INCONSISTENT APPEARANCE** | Visual comparison | Same element styled differently across frames |
| **INFORMATION OVERLOAD** | Measurable density | Text-to-action ratio, visual hierarchy |
| **IRREVERSIBLE ACTION** | Rule-based | Missing confirmation for destructive actions |
| **DATA LOSS** | Rule-based | No save/warning before data-clearing actions |
| **WANDERING ELEMENT** | Compare across frames | Same element in different positions |
| **AMBIGUOUS HOME** | Rule-based | Multiple competing "home" navigation options |
| **INCORRECT INFO** | Factual verification | Demonstrably false information visible |
| **BAD PREDICTION** | Rule-based | Predictions that contradict visible evidence |
| **POOR GROUPING** | Gestalt principles | Proximity, similarity, common region violations |

### Implementation Notes

For **POOR GROUPING**, use the 8 Gestalt principles as objective rules:
1. **Proximity** — Related elements closer than unrelated
2. **Similarity** — Same-function elements share visual properties
3. **Common Region** — Elements in same container perceived as related
4. **Continuity** — Eye follows aligned visual paths
5. **Figure-Ground** — Foreground distinguishable from background
6. **Closure** — Incomplete shapes resolve into forms
7. **Common Fate** — Elements moving together perceived as related
8. **Symmetry** — Symmetrical layouts perceived as stable

If no Gestalt principle is violated, it is NOT Poor Grouping.

---

## Tier 2: Requires Complete Flows (Rule-Based, But Needs Full Task Sequences)

**AI behavior**: Flag findings with caveat — "Based on provided screenshots. Full task flow may reveal additional issues or context."

These traps are rule-based and AI CAN assess them, but only with complete task flows. Screenshots may be missing intermediate steps, making detection unreliable.

| Trap | Why Full Flow Needed | What Might Be Missing |
|------|---------------------|----------------------|
| **UNNECESSARY STEP** | Steps happen between screenshots | Intermediate screens in multi-step process |
| **FORCED SYNTAX** | Can span many steps | Full input sequence showing syntax requirements |
| **GRATUITOUS REDUNDANCY** | May span interactions | Multiple paths to same action across flow |
| **MEMORY CHALLENGE** | Need to see what user must remember | Earlier screens showing info user must recall |
| **SYSTEM AMNESIA** | Need to see what user entered earlier | Previous inputs that system should remember |
| **VARIABLE OUTCOME** | Same action, different results | Multiple flows showing inconsistent behavior |

### Implementation Notes

For these traps, output to a separate `incomplete_flow_findings` array with:
- What was observed
- What additional screenshots would help confirm
- Current confidence level (typically "low" or "medium")

**VARIABLE OUTCOME** specifically requires seeing the same action performed multiple times with different results. A single flow cannot reveal this trap.

---

## Tier 3: Requires Human Judgment (Convention, Memory, Lived Experience)

**AI behavior**: Flag for human review. Do NOT assert as confirmed findings.

These traps depend on knowledge that comes from being human — conventions learned over a lifetime, cultural context, intuitive expectations. AI cannot reliably assess these.

| Trap | Why Human Judgment Needed | What AI Cannot Know |
|------|--------------------------|---------------------|
| **UNCOMPREHENDED ELEMENT** | Cultural/regional knowledge | Whether target users understand specific terminology |
| **INVITING DEAD END** | Learned UI conventions | Whether CTA text matches user expectations |
| **DISTRACTION** | Human attention patterns | What actually pulls attention during real tasks |
| **EFFECTIVELY INVISIBLE ELEMENT** | Scanning behavior | What real users would notice vs. miss |
| **POOR AESTHETIC** | Subjective taste | Whether design meets cultural/brand standards |

### Implementation Notes

Output to `flagged_for_human_review` array with:
- `trap_name`: One of the 5 above
- `observation`: Factual description (no assumptions about confusion)
- `why_human_review_needed`: What human knowledge is required
- `question_for_reviewer`: Yes/no question for human to answer

**Example output:**
```json
{
  "trap_name": "UNCOMPREHENDED ELEMENT",
  "observation": "The term 'Tabs' appears in the page title without definition",
  "why_human_review_needed": "Cannot determine if target users (including new residents from other states) would understand this regional term",
  "question_for_reviewer": "Would your target users understand that 'Tabs' means vehicle registration stickers?"
}
```

### The Underlying Principle

These traps require knowing "what humans just know from living as humans":
- **Memory**: What terminology people have learned
- **Convention**: What UI patterns people expect
- **Experience**: What people have seen work before
- **Taste**: What people find aesthetically pleasing

AI has training data but not lived experience. Asserting findings on these traps leads to false positives.

---

## Tier 4: Cannot Assess from Static Screenshots (Needs Actual Interaction)

**AI behavior**: Explicitly state "Cannot assess from static screenshots" in `traps_checked_not_found`.

These traps require timing data, system responses, or live interaction that static images cannot capture.

| Trap | Why Interaction Needed | What's Missing |
|------|----------------------|----------------|
| **FEEDBACK FAILURE** | Need system response to action | Whether system provides feedback when user acts |
| **SLOW OR NO RESPONSE** | Need timing data | How long system takes to respond |
| **CAPTIVE WAIT** | Need timing + interaction | Whether user can escape waiting state |
| **ACCIDENTAL ACTIVATION** | Need interaction observation | Whether actions are too easy to trigger accidentally |

### Implementation Notes

These traps should appear in `traps_checked_not_found` with a note:
> "Requires interaction testing — cannot assess from static screenshots"

**Exception**: If multiple frames clearly show a state transition (e.g., before/after clicking), some assessment may be possible. But timing and feel cannot be evaluated.

---

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-02-21 | Initial 4-tier classification | Reduce false positives from AI overclaiming |
| 2026-02-21 | Moved VARIABLE OUTCOME to Tier 2 | Requires multiple flows to detect same-action-different-result |

## Future Considerations

As AI capabilities evolve, some traps may move between tiers:
- Better context understanding might enable Tier 3 → Tier 2 movement
- Video analysis might enable Tier 4 → Tier 2 movement
- Improved attention modeling might help with EFFECTIVELY INVISIBLE ELEMENT

This document should be reviewed quarterly and updated based on:
1. Observed false positive patterns
2. New AI capabilities
3. Refined understanding of trap detection requirements
