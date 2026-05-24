# Flow-Aware Analysis Design

**Goal:** Enable the analyzer to evaluate multi-screen designs with awareness of the navigation connections between screens, producing flow-informed trap findings using the same output format as single-screen analysis.

**Date:** 2026-05-24

---

## Overview

Two input paths and two analysis modes, all producing standard trap cards in the existing report format. No schema changes. Flow findings are traps like any other — they reference multiple screens in their `location` field but appear alongside all other findings.

---

## Input Types (Card 1)

Three explicit choices replace the current implicit single/multi detection:

| Option | Description |
|---|---|
| **Screenshot(s)** | One or more screen images, analyzed individually. Current default behavior. |
| **Video / recording** | Screen recording analyzed as frames. Current behavior. |
| **Flow diagram** | Multiple screens connected by navigation lines. Accepts a Figma URL, a Figma export with arrows, or any flow diagram image from any tool. |

When **Flow diagram** is selected:
- Upload zone accepts images and PDFs as before
- The Figma link field becomes more prominent (preferred for this mode — gives structured connection data)
- A note appears: "If uploading an image, include all connected screens and their navigation arrows in a single file"
- The flow analysis mode toggle in Card 5 becomes active

When **Screenshot(s)** or **Video / recording** is selected, behavior is unchanged from today.

---

## Analysis Mode Toggle (Card 5)

Label: **Flow analysis mode**

Appears alongside existing Standard/Thorough coverage toggle. Disabled (grayed out, with tooltip "Select Flow diagram as your input type to enable") unless input type is Flow diagram.

| Mode | Hint text |
|---|---|
| **Screen analysis** | One pass per screen. Thorough per-screen findings, informed by the flow. Takes longer with more screens. |
| **Flow analysis** | One pass for the whole journey. Faster. Finds issues that span multiple screens but may miss finer per-screen detail. |

Default: Screen analysis.

---

## Figma URL Path

The `figma_analyzer.py` already extracts a full prototype flow graph (`{from_node, from_name, to_node, trigger}`) but `app.py` currently throws it away before calling the analyzer. The fix is three steps:

### Step 1 — Resolve destination IDs to frame names

Map `to_node` (raw Figma node ID) to the destination frame's human name using the `frames` list already returned by `analyze_figma_file()`. Produces connections like:

```
"Checkout button" → ON_CLICK → "Order Confirmation"
```

### Step 2 — Build per-frame flow context

For each frame, produce a plain-English context block:

```
Flow context for this screen:
- Reached from: Cart (via tap on "Checkout")
- Leads to: Order Confirmation (via tap on "Place Order")
- Leads to: Cart (via tap on "Back")
```

Also build a complete flow summary string for flow analysis mode:
```
Complete flow: Cart → Checkout → Order Confirmation → Home
Navigation map:
  Cart: "Checkout" button → Checkout
  Checkout: "Place Order" button → Order Confirmation, "Back" → Cart
  Order Confirmation: "Continue Shopping" → Home
```

### Step 3 — Pass to analyzer

- **Screen analysis mode:** inject per-frame context into each frame's prompt via `extra_context`. One API call per frame.
- **Flow analysis mode:** pass complete flow summary + all frame images into a single API call.

No new Figma API calls. No new dependencies. Cost: slightly larger prompt per frame in screen analysis mode.

---

## Flow Diagram Image Path

When the user uploads an image and selects Flow diagram input type, no structured connection data is available — the model reads the arrows visually.

### Screen analysis mode
Single prompt pass. The model is instructed to:
1. Identify individual screens in the image
2. Read connecting arrows to understand navigation structure
3. Analyze each screen for traps using its position in the flow as context

One API call total. Claude's vision capability handles the flow interpretation and trap analysis in a single pass.

### Flow analysis mode
Same single API call, but the prompt instructs the model to evaluate the journey end-to-end rather than screen-by-screen.

### Graceful degradation
If the model determines the image doesn't contain multiple connected screens (user selected the wrong input type), it reports this and analyzes what it can see as a single screen. No crash, no confusing output. The prompt should also instruct the model to flag if connecting arrows are unclear due to image quality.

---

## Prompt Engineering

Four prompt variations, all built on the existing trap analysis prompt with a new **Flow Context** section injected.

### Figma URL — Screen analysis (per-frame injection)

```
FLOW CONTEXT:
This screen sits within a multi-screen flow.
- Reached from: [Screen name] via [action on element]
- Leads to: [Screen name] via [action on element]
- Leads to: [Screen name] via [action on element]

Analyze this screen for traps. Use the flow context to inform your
findings — an element that appears ambiguous in isolation may be clear
given where the user came from, or vice versa.
```

### Figma URL — Flow analysis (single call, all frames)

```
FLOW ANALYSIS:
You are analyzing a complete user flow, not individual screens.
The flow is: [Screen A] → [Screen B] → [Screen C] → ...
Full navigation map: [complete connection list]

Evaluate the journey end-to-end. Focus on traps that only manifest
across multiple steps: UNNECESSARY STEPS, MEMORY CHALLENGE, SYSTEM
AMNESIA, FEEDBACK FAILURE at transitions, AMBIGUOUS HOME. Per-screen
traps are secondary — flag them only if clearly severe.
```

### Image — Screen analysis

Opens with:
```
This image contains a multi-screen flow diagram. Read the connecting
arrows to understand the navigation structure, then analyze each screen
for traps using its position in the flow as context.
```
Followed by the standard trap analysis prompt.

### Image — Flow analysis

Opens with:
```
This image contains a multi-screen flow diagram. Read the connecting
arrows to understand the navigation structure, then evaluate the
journey end-to-end. Focus on traps that only manifest across multiple
steps: UNNECESSARY STEPS, MEMORY CHALLENGE, SYSTEM AMNESIA, FEEDBACK
FAILURE at transitions, AMBIGUOUS HOME.
```
Followed by the standard trap analysis prompt.

All existing modifiers (tenet_filter, trap_filter, thorough_mode, verbosity) apply on top of these — no conflicts.

---

## Files to Change

| File | Change |
|---|---|
| `backend/src/figma_analyzer.py` | Add `build_flow_map(frames, flows)` — resolves node IDs to names, returns per-frame context dict and complete flow summary string |
| `backend/src/prompts.py` | Add `build_flow_context_section(flow_map, mode)` — produces prompt injection for screen or flow analysis mode |
| `backend/src/analyzer.py` | Add `analyze_flow_diagram(design_file, user_context, flow_map, mode)` — screen mode calls `_pass1` per screen with context; flow mode makes one call with all screens and complete map |
| `backend/app.py` | Update `analyze_figma` to pass `flows` through to analyzer; add `flow_mode` form field; update `unified_ask` to handle `input_type` and `flow_mode` |
| `frontend/src/api/types.ts` | Add `input_type: 'screenshot' \| 'video' \| 'flow_diagram'` and `flow_mode?: 'screen' \| 'flow'` to `UserContext` |
| `frontend/src/components/AnalyzerForm.tsx` | Add input type selector to Card 1; add flow analysis mode toggle to Card 5 |
| `frontend/src/api/client.ts` | Pass `input_type` and `flow_mode` in FormData |

---

## What This Does Not Change

- Output schema — flow findings are standard trap cards, `location` field references multiple screens where relevant
- Report format — no new sections, no restructuring
- Single-screen analysis path — completely unchanged
- Thorough mode — orthogonal, can be combined with either flow mode
- Multi-task — orthogonal, can be combined with flow analysis
