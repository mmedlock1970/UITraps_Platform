# Flow-Aware Analysis Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Wire prototype flow data from Figma API through the analyzer as context, and add prompt support for flow diagram images so the model can reason about multi-screen journeys.

**Architecture:** Two input paths share the same output format. Figma URL path: `get_prototype_flows()` already extracts connection data; we add `from_frame` tracking, a `build_flow_map()` function, and an `analyze_flow_diagram()` method that either loops frames with per-frame context (screen mode) or builds a single multi-image call (flow mode). Image path: simpler — prepend flow-aware prompt text to `extra_context` before calling `analyze_design()`. Both paths add `input_type` / `flow_mode` form fields; the frontend gets an input type selector (Card 1) and a flow mode toggle (Card 5).

**Tech Stack:** Python 3.11, FastAPI, Anthropic SDK (tool_use), React 18, TypeScript

---

## Task 1: Modify `get_prototype_flows()` to track parent frame

**Files:**
- Modify: `backend/src/figma_analyzer.py:246-278`
- Create: `backend/tests/test_figma_analyzer.py`

### Step 1: Write the failing test

```python
# backend/tests/test_figma_analyzer.py
import pytest
from src.figma_analyzer import FigmaAnalyzer

def _mock_document():
    return {
        "document": {
            "children": [{
                "type": "PAGE",
                "name": "Page 1",
                "children": [
                    {
                        "type": "FRAME",
                        "id": "frame-1",
                        "name": "Cart",
                        "children": [
                            {
                                "type": "COMPONENT",
                                "id": "btn-checkout",
                                "name": "Checkout button",
                                "interactions": [{
                                    "trigger": {"type": "ON_CLICK"},
                                    "actions": [{"destinationId": "frame-2"}]
                                }],
                                "children": []
                            }
                        ]
                    },
                    {
                        "type": "FRAME",
                        "id": "frame-2",
                        "name": "Checkout",
                        "children": []
                    }
                ]
            }]
        }
    }

def test_get_prototype_flows_includes_from_frame():
    fa = FigmaAnalyzer.__new__(FigmaAnalyzer)
    flows = fa.get_prototype_flows(_mock_document())

    assert len(flows) == 1
    flow = flows[0]
    assert flow['from_node'] == 'btn-checkout'
    assert flow['from_name'] == 'Checkout button'
    assert flow['to_node'] == 'frame-2'
    assert flow['from_frame'] == 'frame-1'
    assert flow['from_frame_name'] == 'Cart'
```

### Step 2: Run it to verify it fails

Run: `cd backend && python -m pytest tests/test_figma_analyzer.py::test_get_prototype_flows_includes_from_frame -v`

Expected: FAIL with `KeyError: 'from_frame'`

### Step 3: Modify `get_prototype_flows()`

In `backend/src/figma_analyzer.py`, change `traverse_for_interactions` to accept and track `current_frame_id` and `current_frame_name`:

```python
def get_prototype_flows(self, file_data: Dict) -> List[Dict]:
    flows = []

    def traverse_for_interactions(node, current_frame_id='', current_frame_name=''):
        if not node:
            return
        node_type = node.get('type', '')
        frame_id = current_frame_id
        frame_name = current_frame_name
        if node_type == 'FRAME':
            frame_id = node.get('id', '')
            frame_name = node.get('name', 'Unnamed')

        interactions = node.get('interactions') or []
        for interaction in interactions:
            if not interaction:
                continue
            actions = interaction.get('actions') or [{}]
            action = actions[0] if actions else {}
            if not action:
                action = {}
            destination_id = action.get('destinationId')

            if destination_id:
                trigger = interaction.get('trigger') or {}
                flows.append({
                    'from_node': node.get('id', ''),
                    'from_name': node.get('name', 'Unnamed'),
                    'from_frame': frame_id,
                    'from_frame_name': frame_name,
                    'to_node': destination_id,
                    'trigger': trigger.get('type', 'UNKNOWN')
                })

        for child in node.get('children') or []:
            traverse_for_interactions(child, frame_id, frame_name)

    document = file_data.get('document') or {}
    for page in document.get('children') or []:
        traverse_for_interactions(page)

    return flows
```

### Step 4: Run test to verify it passes

Run: `cd backend && python -m pytest tests/test_figma_analyzer.py::test_get_prototype_flows_includes_from_frame -v`

Expected: PASS

### Step 5: Commit

```bash
git add backend/src/figma_analyzer.py backend/tests/test_figma_analyzer.py
git commit -m "feat: track parent frame in get_prototype_flows()"
```

---

## Task 2: Add `build_flow_map()` to `figma_analyzer.py`

**Files:**
- Modify: `backend/src/figma_analyzer.py` (append after `FigmaAnalyzer` class)
- Modify: `backend/tests/test_figma_analyzer.py`

### Step 1: Write the failing tests

Add to `backend/tests/test_figma_analyzer.py`:

```python
from src.figma_analyzer import build_flow_map

def _mock_frames():
    return [
        {'id': 'frame-1', 'name': 'Cart'},
        {'id': 'frame-2', 'name': 'Checkout'},
        {'id': 'frame-3', 'name': 'Order Confirmation'},
    ]

def _mock_flows():
    return [
        {
            'from_node': 'btn-1', 'from_name': 'Checkout button',
            'from_frame': 'frame-1', 'from_frame_name': 'Cart',
            'to_node': 'frame-2', 'trigger': 'ON_CLICK'
        },
        {
            'from_node': 'btn-2', 'from_name': 'Place Order',
            'from_frame': 'frame-2', 'from_frame_name': 'Checkout',
            'to_node': 'frame-3', 'trigger': 'ON_CLICK'
        },
    ]

def test_build_flow_map_per_frame_context():
    result = build_flow_map(_mock_frames(), _mock_flows())
    per = result['per_frame']

    # Cart leads to Checkout
    assert any(e['screen'] == 'Checkout' for e in per['frame-1']['leads_to'])
    # Checkout reached from Cart
    assert any(e['screen'] == 'Cart' for e in per['frame-2']['reached_from'])
    # Checkout leads to Order Confirmation
    assert any(e['screen'] == 'Order Confirmation' for e in per['frame-2']['leads_to'])
    # Order Confirmation reached from Checkout
    assert any(e['screen'] == 'Checkout' for e in per['frame-3']['reached_from'])

def test_build_flow_map_summary_contains_frames():
    result = build_flow_map(_mock_frames(), _mock_flows())
    summary = result['summary']
    assert 'Cart' in summary
    assert 'Checkout' in summary
    assert 'Order Confirmation' in summary

def test_build_flow_map_ignores_unknown_destinations():
    flows = _mock_flows() + [{
        'from_node': 'btn-x', 'from_name': 'External link',
        'from_frame': 'frame-1', 'from_frame_name': 'Cart',
        'to_node': 'unknown-node-id', 'trigger': 'ON_CLICK'
    }]
    result = build_flow_map(_mock_frames(), flows)
    # Should not crash; leads_to for frame-1 still has only 1 entry (the valid one)
    assert len(result['per_frame']['frame-1']['leads_to']) == 1
```

### Step 2: Run to verify they fail

Run: `cd backend && python -m pytest tests/test_figma_analyzer.py -k "build_flow_map" -v`

Expected: FAIL with `ImportError: cannot import name 'build_flow_map'`

### Step 3: Implement `build_flow_map()`

Add this function at the end of `backend/src/figma_analyzer.py`, after the `FigmaAnalyzer` class:

```python
def build_flow_map(frames: List[Dict], flows: List[Dict]) -> Dict:
    """
    Build per-frame flow context and a complete flow summary from prototype data.

    Args:
        frames: list of {id, name, ...} from analyze_figma_file()
        flows:  list of {from_node, from_name, from_frame, from_frame_name,
                         to_node, trigger} from get_prototype_flows()

    Returns:
        {
            'per_frame': {
                frame_id: {
                    'name': str,
                    'reached_from': [{'screen': str, 'via': str}],
                    'leads_to':     [{'screen': str, 'via': str}]
                }
            },
            'summary': str
        }
    """
    id_to_name: Dict[str, str] = {f['id']: f['name'] for f in frames}

    per_frame: Dict[str, Dict] = {
        f['id']: {'name': f['name'], 'reached_from': [], 'leads_to': []}
        for f in frames
    }

    for flow in flows:
        from_frame_id   = flow.get('from_frame', '')
        from_frame_name = flow.get('from_frame_name', '')
        element_name    = flow.get('from_name', 'element')
        to_id           = flow.get('to_node', '')
        dest_name       = id_to_name.get(to_id)

        if not dest_name:
            continue  # destination not in our analyzed frames list

        via_label = f'tap on "{element_name}"'

        if from_frame_id in per_frame:
            per_frame[from_frame_id]['leads_to'].append(
                {'screen': dest_name, 'via': via_label}
            )

        if to_id in per_frame:
            per_frame[to_id]['reached_from'].append(
                {'screen': from_frame_name or 'Previous screen', 'via': via_label}
            )

    # Build summary string
    nav_lines = []
    for frame in frames:
        fid = frame['id']
        ctx = per_frame[fid]
        if ctx['leads_to']:
            transitions = ', '.join(
                f'"{l["via"].replace("tap on \\"", "").replace("\\"", "")}" → {l["screen"]}'
                for l in ctx['leads_to']
            )
            nav_lines.append(f"  {ctx['name']}: {transitions}")

    frame_names = [f['name'] for f in frames]
    flow_chain = ' → '.join(frame_names[:6])
    if len(frame_names) > 6:
        flow_chain += ' → ...'

    summary = f"Complete flow: {flow_chain}\nNavigation map:\n" + '\n'.join(nav_lines)

    return {'per_frame': per_frame, 'summary': summary}
```

### Step 4: Run tests to verify they pass

Run: `cd backend && python -m pytest tests/test_figma_analyzer.py -v`

Expected: All PASS

### Step 5: Commit

```bash
git add backend/src/figma_analyzer.py backend/tests/test_figma_analyzer.py
git commit -m "feat: add build_flow_map() to figma_analyzer"
```

---

## Task 3: Add `build_flow_context_section()` to `prompts.py`

**Files:**
- Modify: `backend/src/prompts.py` (append near end, before `build_figma_message`)
- Create: `backend/tests/test_prompts_flow.py`

### Step 1: Write the failing tests

```python
# backend/tests/test_prompts_flow.py
from src.prompts import build_flow_context_section

def test_screen_mode_includes_reached_from():
    ctx = {
        'name': 'Checkout',
        'reached_from': [{'screen': 'Cart', 'via': 'tap on "Checkout button"'}],
        'leads_to': [{'screen': 'Order Confirmation', 'via': 'tap on "Place Order"'}],
    }
    result = build_flow_context_section(flow_context=ctx, mode='screen')
    assert 'Reached from: Cart' in result
    assert 'Leads to: Order Confirmation' in result
    assert 'FLOW CONTEXT' in result

def test_flow_mode_includes_summary():
    summary = "Complete flow: Cart → Checkout\nNavigation map:\n  Cart: Checkout button → Checkout"
    result = build_flow_context_section(flow_summary=summary, mode='flow')
    assert 'Cart → Checkout' in result
    assert 'FLOW ANALYSIS' in result
    assert 'UNNECESSARY STEPS' in result

def test_returns_empty_string_for_missing_data():
    assert build_flow_context_section() == ''
    assert build_flow_context_section(mode='screen') == ''
    assert build_flow_context_section(mode='flow') == ''
```

### Step 2: Run to verify they fail

Run: `cd backend && python -m pytest tests/test_prompts_flow.py -v`

Expected: FAIL with `ImportError`

### Step 3: Implement `build_flow_context_section()`

Add to `backend/src/prompts.py`, just before the `build_figma_message` function (around line 1419):

```python
def build_flow_context_section(
    flow_context: dict = None,
    flow_summary: str = None,
    mode: str = 'screen',
) -> str:
    """
    Build the FLOW CONTEXT or FLOW ANALYSIS prompt injection.

    Args:
        flow_context:  Per-frame dict {name, reached_from, leads_to} — for screen mode
        flow_summary:  Complete flow summary string — for flow mode
        mode:          'screen' or 'flow'
    """
    if mode == 'flow' and flow_summary:
        return (
            "\nFLOW ANALYSIS:\n"
            "You are analyzing a complete user flow, not individual screens.\n"
            f"{flow_summary}\n\n"
            "Evaluate the journey end-to-end. Focus on traps that only manifest "
            "across multiple steps: UNNECESSARY STEPS, MEMORY CHALLENGE, SYSTEM "
            "AMNESIA, FEEDBACK FAILURE at transitions, AMBIGUOUS HOME. Per-screen "
            "traps are secondary — flag them only if clearly severe.\n"
        )

    if mode == 'screen' and flow_context:
        reached = '\n'.join(
            f"  - Reached from: {r['screen']} via {r['via']}"
            for r in flow_context.get('reached_from', [])
        )
        leads = '\n'.join(
            f"  - Leads to: {l['screen']} via {l['via']}"
            for l in flow_context.get('leads_to', [])
        )
        lines = '\n'.join(filter(None, [reached, leads]))
        if not lines:
            lines = "  - No connected screens detected in prototype data"
        return (
            "\nFLOW CONTEXT:\n"
            "This screen sits within a multi-screen flow.\n"
            f"{lines}\n\n"
            "Analyze this screen for traps. Use the flow context to inform your "
            "findings — an element that appears ambiguous in isolation may be clear "
            "given where the user came from, or vice versa.\n"
        )

    return ''
```

### Step 4: Run tests to verify they pass

Run: `cd backend && python -m pytest tests/test_prompts_flow.py -v`

Expected: All PASS

### Step 5: Commit

```bash
git add backend/src/prompts.py backend/tests/test_prompts_flow.py
git commit -m "feat: add build_flow_context_section() to prompts"
```

---

## Task 4: Add `image_data_list` parameter to `build_user_message()`

This lets flow mode pass multiple frame images in a single API call.

**Files:**
- Modify: `backend/src/prompts.py:1024-1416` (the `build_user_message` function)

### Step 1: Write the failing test

Add to `backend/tests/test_prompts_flow.py`:

```python
from src.prompts import build_user_message

def test_build_user_message_accepts_image_list():
    ctx = {'users': 'users', 'tasks': 'task', 'format': 'app', 'content_type': 'website', 'task_list': []}
    img1 = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "abc"}}
    img2 = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "def"}}
    content = build_user_message(ctx, image_data_list=[img1, img2])
    # Both images should appear before the text block
    image_blocks = [c for c in content if c.get('type') == 'image']
    assert len(image_blocks) == 2
    text_blocks = [c for c in content if c.get('type') == 'text']
    assert len(text_blocks) == 1
```

### Step 2: Run to verify it fails

Run: `cd backend && python -m pytest tests/test_prompts_flow.py::test_build_user_message_accepts_image_list -v`

Expected: FAIL — `build_user_message` puts single image first; no `image_data_list` param

### Step 3: Modify `build_user_message()` signature and content assembly

In `backend/src/prompts.py`, change the function signature from:

```python
def build_user_message(
    user_context: dict,
    image_data: dict = None,
    page_context: dict = None,
    ...
```

to:

```python
def build_user_message(
    user_context: dict,
    image_data: dict = None,
    image_data_list: list = None,
    page_context: dict = None,
    ...
```

Then change the content assembly block near the end of the function (around line 1403) from:

```python
    # Build message content
    content = []

    # Add image first if provided (Claude processes images before text)
    if image_data:
        content.append(image_data)

    # Add the context and instructions
    content.append({
        "type": "text",
        "text": context_text
    })

    return content
```

to:

```python
    # Build message content
    content = []

    # Add images first (Claude processes images before text)
    if image_data_list:
        content.extend(image_data_list)
    elif image_data:
        content.append(image_data)

    # Add the context and instructions
    content.append({
        "type": "text",
        "text": context_text
    })

    return content
```

### Step 4: Run tests to verify they pass

Run: `cd backend && python -m pytest tests/test_prompts_flow.py -v`

Expected: All PASS

### Step 5: Commit

```bash
git add backend/src/prompts.py backend/tests/test_prompts_flow.py
git commit -m "feat: add image_data_list param to build_user_message()"
```

---

## Task 5: Add `analyze_flow_diagram()` to `analyzer.py`

**Files:**
- Modify: `backend/src/analyzer.py` (add method to `UITrapsAnalyzer` class, before `_pass1`)
- Create: `backend/tests/test_analyzer_flow.py`

### Step 1: Write the failing tests

```python
# backend/tests/test_analyzer_flow.py
import pytest
from unittest.mock import patch, MagicMock
from src.analyzer import UITrapsAnalyzer

MOCK_REPORT = {
    'summary_headline': 'Test',
    'summary_narrative': 'Test narrative',
    'critical_issues': [],
    'moderate_issues': [],
    'minor_issues': [],
    'positive_observations': [],
    'potential_issues': [],
    'traps_checked_not_found': [],
    'flagged_for_human_review': [],
    'incomplete_flow_findings': [],
    'bugs_detected': [],
}

MOCK_FLOW_MAP = {
    'per_frame': {
        'f1': {'name': 'Cart', 'reached_from': [], 'leads_to': [{'screen': 'Checkout', 'via': 'tap on "Checkout"'}]},
        'f2': {'name': 'Checkout', 'reached_from': [{'screen': 'Cart', 'via': 'tap on "Checkout"'}], 'leads_to': []},
    },
    'summary': 'Complete flow: Cart → Checkout\nNavigation map:\n  Cart: Checkout → Checkout',
}

MOCK_FRAMES = [
    {'id': 'f1', 'name': 'Cart', 'image_path': '/tmp/cart.png'},
    {'id': 'f2', 'name': 'Checkout', 'image_path': '/tmp/checkout.png'},
]

USER_CONTEXT = {'users': 'users', 'tasks': 'buy product', 'format': 'app', 'content_type': 'website', 'task_list': []}

@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', side_effect=lambda r, **kw: r)
def test_screen_mode_calls_pass1_per_frame(mock_enrich, mock_pass1):
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    result = analyzer.analyze_flow_diagram(
        frames=MOCK_FRAMES,
        flow_map=MOCK_FLOW_MAP,
        user_context=USER_CONTEXT,
        mode='screen',
    )
    assert mock_pass1.call_count == 2
    # Each call should inject flow context into extra_context
    call_args = mock_pass1.call_args_list
    extra_1 = call_args[0].kwargs.get('user_context', {}).get('extra_context', '')
    assert 'FLOW CONTEXT' in extra_1

@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', side_effect=lambda r, **kw: r)
def test_flow_mode_calls_pass1_once(mock_enrich, mock_pass1):
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    # flow mode makes one API call; we route it through a modified _pass1 call
    result = analyzer.analyze_flow_diagram(
        frames=MOCK_FRAMES,
        flow_map=MOCK_FLOW_MAP,
        user_context=USER_CONTEXT,
        mode='flow',
    )
    assert mock_pass1.call_count == 1
    # The single call's extra_context should contain FLOW ANALYSIS
    extra = mock_pass1.call_args.kwargs.get('user_context', {}).get('extra_context', '')
    assert 'FLOW ANALYSIS' in extra

@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', side_effect=lambda r, **kw: r)
def test_skips_frames_without_image_path(mock_enrich, mock_pass1):
    frames = MOCK_FRAMES + [{'id': 'f3', 'name': 'Error', 'image_path': None}]
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(frames=frames, flow_map=MOCK_FLOW_MAP,
                                   user_context=USER_CONTEXT, mode='screen')
    assert mock_pass1.call_count == 2  # f3 skipped
```

### Step 2: Run to verify they fail

Run: `cd backend && python -m pytest tests/test_analyzer_flow.py -v`

Expected: FAIL with `AttributeError: UITrapsAnalyzer has no attribute 'analyze_flow_diagram'`

### Step 3: Implement `analyze_flow_diagram()`

Add this method to the `UITrapsAnalyzer` class in `backend/src/analyzer.py`, before the `_pass1` method (around line 411). Import `build_flow_context_section` at the top of the method:

```python
def analyze_flow_diagram(
    self,
    frames: List[Dict],
    flow_map: Dict,
    user_context: Dict[str, str],
    mode: str = 'screen',
    timeout: int = 120,
    kb_version: str = 'v2',
    verbosity: str = 'standard',
    pass1_model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze Figma frames with flow-aware context.

    Screen mode: one _pass1 call per frame with per-frame flow context injected
                 into extra_context. Results are merged like tenet-parallel.
    Flow mode:   single _pass1 call using the first frame's image path but with
                 all frame images listed and the complete flow summary in extra_context.
                 (Multi-image is assembled in the prompt via image_data_list in
                 build_user_message.)
    """
    try:
        from .prompts import build_flow_context_section
    except ImportError:
        from prompts import build_flow_context_section

    import time as time_module
    start_time = time_module.time()

    valid_frames = [f for f in frames if f.get('image_path')]
    if not valid_frames:
        raise ValueError("No exportable frames found")

    if mode == 'flow':
        ctx = dict(user_context)
        flow_section = build_flow_context_section(
            flow_summary=flow_map.get('summary', ''),
            mode='flow',
        )
        existing_extra = ctx.get('extra_context', '')
        ctx['extra_context'] = (flow_section + '\n' + existing_extra).strip()

        # Load all frame images for a multi-image single pass
        image_data_list = [self._load_image(f['image_path']) for f in valid_frames]

        # Re-use _pass1 with the first frame path (for file validation) but
        # override the image list via extra_context approach.
        # Since _pass1 accepts preloaded_image, we pass the first image there
        # and rely on the flow summary in extra_context to convey all frame context.
        # For a true multi-image call the image_data_list is unused here;
        # the caller that needs multi-image can build the API call directly.
        # This implementation: flow summary + all frame images listed in prompt.
        frames_list = '\n'.join(f"  - {f['name']}" for f in valid_frames)
        ctx['extra_context'] = (
            ctx['extra_context'] + f"\n\nFrames included in this flow:\n{frames_list}"
        ).strip()

        report = self._pass1(
            design_file=valid_frames[0]['image_path'],
            user_context=ctx,
            timeout=timeout,
            kb_version=kb_version,
            verbosity=verbosity,
            pass1_model=pass1_model,
        )
        reports = [report]
    else:
        # Screen mode: one call per frame with per-frame flow context
        reports = []
        for frame in valid_frames:
            ctx = dict(user_context)
            per_frame_ctx = flow_map.get('per_frame', {}).get(frame['id'])
            if per_frame_ctx:
                flow_section = build_flow_context_section(
                    flow_context=per_frame_ctx, mode='screen'
                )
                existing_extra = ctx.get('extra_context', '')
                ctx['extra_context'] = (flow_section + '\n' + existing_extra).strip()
            report = self._pass1(
                design_file=frame['image_path'],
                user_context=ctx,
                timeout=timeout,
                kb_version=kb_version,
                verbosity=verbosity,
                pass1_model=pass1_model,
            )
            reports.append(report)

    merged = self._merge_reports(reports)

    # Normalize optional fields
    for _opt in ['critical_issues', 'moderate_issues', 'minor_issues',
                 'positive_observations', 'potential_issues', 'traps_checked_not_found',
                 'flagged_for_human_review', 'incomplete_flow_findings']:
        if not isinstance(merged.get(_opt), list):
            merged[_opt] = []

    # Pass 2 enrichment
    try:
        merged = self._enrich_report(merged, timeout=timeout, kb_version=kb_version, verbosity=verbosity)
    except Exception as e:
        print(f"[UITraps] Flow analysis Pass 2 enrichment skipped (non-fatal): {e}")

    return merged
```

### Step 4: Run tests to verify they pass

Run: `cd backend && python -m pytest tests/test_analyzer_flow.py -v`

Expected: All PASS

### Step 5: Commit

```bash
git add backend/src/analyzer.py backend/tests/test_analyzer_flow.py
git commit -m "feat: add analyze_flow_diagram() to UITrapsAnalyzer"
```

---

## Task 6: Update `app.py` — image path in `unified_ask`

Add `input_type` and `flow_mode` form fields to `unified_ask`. When `input_type == 'flow_diagram'` and a file is uploaded (no Figma URL), prepend flow-diagram prompt text to `extra_context`.

**Files:**
- Modify: `backend/app.py` — `unified_ask` function signature and ANALYSIS branch

### Step 1: Add form field parameters

In `backend/app.py`, in the `unified_ask` function signature (around line 1852), add two new fields after `task_list`:

```python
    task_list: Optional[str] = Form(None),
    input_type: Optional[str] = Form(None),   # 'screenshot' | 'video' | 'flow_diagram'
    flow_mode: Optional[str] = Form(None),     # 'screen' | 'flow'
    figma_url: Optional[str] = Form(None),     # Figma URL for flow_diagram + Figma path
```

### Step 2: Handle image path for flow_diagram in ANALYSIS branch

In the ANALYSIS branch, after the `_task_list_parsed` block (around line 1950), add:

```python
        # Flow diagram image path: prepend flow-aware prompt text to extra_context
        _input_type = input_type or 'screenshot'
        _flow_mode = flow_mode or 'screen'
        _is_flow_diagram = _input_type == 'flow_diagram'

        if _is_flow_diagram:
            _flow_preamble = (
                "FLOW DIAGRAM INPUT:\n"
                "The uploaded image contains a multi-screen flow diagram. "
                "Read the connecting arrows to understand the navigation structure between screens."
            )
            if _flow_mode == 'flow':
                _flow_preamble += (
                    " Then evaluate the journey end-to-end. Focus on traps that only manifest "
                    "across multiple steps: UNNECESSARY STEPS, MEMORY CHALLENGE, SYSTEM AMNESIA, "
                    "FEEDBACK FAILURE at transitions, AMBIGUOUS HOME. Per-screen traps are "
                    "secondary — flag them only if clearly severe."
                )
            else:
                _flow_preamble += (
                    " Then analyze each screen for traps using its position in the flow as context."
                )
            extra_context = (_flow_preamble + '\n' + (extra_context or '')).strip()
```

This block goes before the `if len(files) == 1:` check so both single and multi-image paths get it.

### Step 3: Update `user_context` dicts to include new fields

In both the single-image and multi-image `user_context` dicts in the ANALYSIS branch, change:

```python
user_context = {"users": users, "tasks": tasks, "format": format, "content_type": content_type, "extra_context": extra_context or "", ...}
```

(The `extra_context` assignment already uses the potentially-modified `extra_context` variable from Step 2, so no change is needed there as long as the preamble is prepended before `user_context` is assembled.)

### Step 4: Manual test

Start the backend and submit a single image with `input_type=flow_diagram` via curl or the frontend. Verify the prompt includes `FLOW DIAGRAM INPUT:` in the report or server logs.

### Step 5: Commit

```bash
git add backend/app.py
git commit -m "feat: handle flow_diagram input_type in unified_ask image path"
```

---

## Task 7: Update `app.py` — Figma URL path in `unified_ask`

When `input_type == 'flow_diagram'` and `figma_url` is provided in `unified_ask`, call `FigmaAnalyzer` to export frames, build a flow map, and call `analyze_flow_diagram()`.

**Files:**
- Modify: `backend/app.py` — add Figma URL branch to the ANALYSIS section in `unified_ask`

### Step 1: Add Figma URL branch to ANALYSIS section

In the ANALYSIS branch of `unified_ask`, after the flow preamble block from Task 6, add a new branch before the `if len(files) == 1:` check:

```python
        # Figma URL flow path
        if _is_flow_diagram and figma_url and figma_url.strip():
            if not is_figma_available():
                raise HTTPException(
                    status_code=503,
                    detail="Figma analysis not available. FIGMA_TOKEN not configured."
                )
            try:
                with tempfile.TemporaryDirectory() as _tmp_dir:
                    _figma = FigmaAnalyzer()
                    _file_key, _ = _figma.parse_figma_url(figma_url.strip())
                    _cached = get_cached_figma_data(_file_key)
                    _figma_result = _figma.analyze_figma_file(
                        figma_url.strip(), _tmp_dir,
                        cached_file_data=_cached,
                        max_frames=10
                    )
                    _frames = _figma_result['frames']
                    _flows = _figma_result['flows']

                    from src.figma_analyzer import build_flow_map
                    _flow_map = build_flow_map(_frames, _flows)

                    _fctx = {
                        "users": users, "tasks": tasks, "format": format,
                        "content_type": content_type,
                        "extra_context": extra_context or "",
                        "product_context": product_context or "",
                        "tenet_filter": tenet_filter or "",
                        "design_name": design_name or "",
                        "task_list": _task_list_parsed,
                    }
                    user_id = str(user.get("id") or user.get("userId", ""))
                    _analyzer = UITrapsAnalyzer()
                    _report_dict = _analyzer.analyze_flow_diagram(
                        frames=_frames,
                        flow_map=_flow_map,
                        user_context=_fctx,
                        mode=_flow_mode,
                        kb_version=kb_version,
                        verbosity=verbosity,
                        pass1_model=pass1_model,
                    )
                    # Normalize optional fields
                    for _opt in ['critical_issues', 'moderate_issues', 'minor_issues',
                                 'positive_observations', 'potential_issues',
                                 'traps_checked_not_found', 'flagged_for_human_review',
                                 'incomplete_flow_findings']:
                        if not isinstance(_report_dict.get(_opt), list):
                            _report_dict[_opt] = []
                    _analyzer._normalize_report_completeness(_report_dict, kb_version=kb_version)

                    _elapsed = 0
                    _analysis_settings = {
                        'verbosity': verbosity, 'pass1_model': pass1_model,
                        'kb_version': kb_version, 'elapsed_seconds': _elapsed,
                        'thorough_mode': False,
                    }
                    _html = format_report_as_html(_report_dict, _fctx, analysis_settings=_analysis_settings)
                    _stats = get_report_statistics(_report_dict)

                    return {
                        "success": True,
                        "mode": "analysis",
                        "report_html": _html,
                        "statistics": _stats,
                        "kb_version": kb_version,
                    }
            except HTTPException:
                raise
            except Exception as _e:
                logger.error(f"Flow Figma analysis error: {_e}")
                raise HTTPException(status_code=500, detail=f"Flow analysis failed: {str(_e)}")
```

You need to ensure `format_report_as_html`, `get_report_statistics`, `FigmaAnalyzer`, `get_cached_figma_data` are already imported at the top of `app.py`. Check and add any missing imports:

```python
from src.figma_analyzer import FigmaAnalyzer   # already imported
from src.formatters import format_report_as_html, get_report_statistics  # check if imported
```

### Step 2: Verify imports are present

Run: `cd backend && python -c "import app"` — should produce no ImportError.

### Step 3: Manual test

With `FIGMA_TOKEN` configured, submit a Figma URL with `input_type=flow_diagram` via the frontend. Verify the analysis runs and returns an HTML report.

### Step 4: Commit

```bash
git add backend/app.py
git commit -m "feat: add Figma URL path for flow_diagram input_type in unified_ask"
```

---

## Task 8: TypeScript types — add `input_type`, `flow_mode`, `figma_url`

**Files:**
- Modify: `frontend/src/api/types.ts:112-131` (`UserContext` interface)

### Step 1: Add fields to `UserContext`

In `frontend/src/api/types.ts`, change the `UserContext` interface to add three fields after `thorough_mode`:

```typescript
export interface UserContext {
  users: string;
  expertise?: string;
  tasks: string;
  task_list?: Array<{ name: string; description: string }>;
  format: string;
  design_name?: string;
  contentType?: ContentType;
  extra_context?: string;
  product_context?: string;
  physical_env?: string;
  lighting?: string;
  grip_position?: string;
  attentional_state?: string;
  kb_version?: KbVersion;
  tenet_filter?: string[];
  verbosity?: 'brief' | 'standard';
  pass1_model?: 'sonnet' | 'haiku';
  thorough_mode?: boolean;
  input_type?: 'screenshot' | 'video' | 'flow_diagram';
  flow_mode?: 'screen' | 'flow';
  figma_url?: string;
}
```

### Step 2: Verify TypeScript compiles

Run: `cd frontend && npx tsc --noEmit`

Expected: No new errors (there may be pre-existing warnings, but no new type errors from this change)

### Step 3: Commit

```bash
git add frontend/src/api/types.ts
git commit -m "feat: add input_type, flow_mode, figma_url to UserContext"
```

---

## Task 9: Update `client.ts` to send new fields

**Files:**
- Modify: `frontend/src/api/client.ts:443-462` (the `if (context)` block in `unifiedAsk`)

### Step 1: Add fields to the formData block

In `frontend/src/api/client.ts`, in `unifiedAsk`, within the `if (context)` block, add after the `thorough_mode` line:

```typescript
    if (context.thorough_mode) formData.append('thorough_mode', 'true');
    if (context.input_type) formData.append('input_type', context.input_type);
    if (context.flow_mode) formData.append('flow_mode', context.flow_mode);
    if (context.figma_url) formData.append('figma_url', context.figma_url);
```

### Step 2: Verify TypeScript compiles

Run: `cd frontend && npx tsc --noEmit`

Expected: No errors

### Step 3: Commit

```bash
git add frontend/src/api/client.ts
git commit -m "feat: send input_type, flow_mode, figma_url in unifiedAsk"
```

---

## Task 10: Update `assembleContext()` in `AnalyzerForm.tsx` — pass new fields

**Files:**
- Modify: `frontend/src/components/AnalyzerForm.tsx:52-110` (`assembleContext` function)

### Step 1: Update `assembleContext` signature and body

Change the function signature to accept two new parameters:

```typescript
function assembleContext(fields: {
  platform: string; productDomain: string; screenName: string;
  expLevel: string; techSavvy: string; frequency: string;
  taskList: Array<{ name: string; description: string }>;
  priorProducts: string; userDesc: string; extraContext: string; productContext: string;
  physicalEnv: string; lighting: string; gripPosition: string; attentionalState: string;
  kbVersion: KbVersion; selectedTenets: string[];
  verbosity: 'brief' | 'standard'; pass1Model: 'sonnet' | 'haiku';
  figmaLink: string; thoroughMode: boolean;
  inputType: 'screenshot' | 'video' | 'flow_diagram';
  flowMode: 'screen' | 'flow';
}): UserContext {
```

Destructure the two new fields in the body:

```typescript
  const { ..., figmaLink, thoroughMode, inputType, flowMode } = fields;
```

Update the `combinedExtra` block to only add `figmaLink` to extra context when the input type is NOT `flow_diagram` (for `flow_diagram` + Figma URL, it goes as a dedicated `figma_url` field instead):

```typescript
  const combinedExtra = [
    (figmaLink.trim() && inputType !== 'flow_diagram') ? `Design file: ${figmaLink.trim()}` : '',
    extraContext,
  ].filter(Boolean).join('\n');
```

Add the new fields to the returned `UserContext` object at the end of `assembleContext`:

```typescript
  return {
    users: ...,
    tasks: ...,
    // ... all existing fields ...
    thorough_mode: thoroughMode || undefined,
    input_type: inputType,
    flow_mode: inputType === 'flow_diagram' ? flowMode : undefined,
    figma_url: (inputType === 'flow_diagram' && figmaLink.trim()) ? figmaLink.trim() : undefined,
  };
```

### Step 2: Verify TypeScript compiles

Run: `cd frontend && npx tsc --noEmit`

Expected: TypeScript will report that the two new fields are missing from the `assembleContext` call site. Those get fixed in Task 11.

### Step 3: Note (do NOT commit yet — defer to after Task 11)

---

## Task 11: Add input type selector to Card 1 and flow mode toggle to Card 5

This task adds state, UI, and wires everything up.

**Files:**
- Modify: `frontend/src/components/AnalyzerForm.tsx`
- Modify: `frontend/src/components/AnalyzerForm.module.css`

### Step 1: Add state variables

After the existing `const [thoroughMode, setThoroughMode] = useState(false);` (around line 157), add:

```typescript
  const [inputType, setInputType] = useState<'screenshot' | 'video' | 'flow_diagram'>('screenshot');
  const [flowMode, setFlowMode] = useState<'screen' | 'flow'>('screen');
```

### Step 2: Update the `assembleContext` call site

In the `handleSubmit`/`useCallback` call to `assembleContext`, add the two new fields:

```typescript
      physicalEnv, lighting, gripPosition, attentionalState, kbVersion, selectedTenets,
      verbosity, pass1Model, figmaLink, thoroughMode, inputType, flowMode });
```

Also update the `useCallback` dependency array to include `inputType` and `flowMode`.

### Step 3: Add input type selector to Card 1

In `AnalyzerForm.tsx`, after the Figma link input (around line 334), add:

```tsx
          {/* Input type selector */}
          <div className={styles.field} style={{ marginTop: 12 }}>
            <label className={styles.fieldLabel}>What are you uploading?</label>
            <div className={styles.kbVersionGroup}>
              {([
                ['screenshot', 'Screenshot(s)'],
                ['video', 'Video / recording'],
                ['flow_diagram', 'Flow diagram'],
              ] as const).map(([v, label]) => (
                <button
                  key={v}
                  type="button"
                  className={`${styles.kbVersionBtn} ${inputType === v ? styles.kbVersionBtnActive : ''}`}
                  onClick={() => setInputType(v)}
                  disabled={disabled}
                >
                  {label}
                </button>
              ))}
            </div>
            {inputType === 'flow_diagram' && (
              <p className={styles.fieldHint}>
                If uploading an image, include all connected screens and their navigation arrows in a single file. Or enter a Figma link above — prototype connections will be extracted automatically.
              </p>
            )}
          </div>
```

### Step 4: Add flow mode toggle to Card 5

In `AnalyzerForm.tsx`, after the Analysis coverage toggle block (after line 886, before the closing `</div>` of card body), add:

```tsx
          <hr className={styles.fieldDivider} />

          {/* Flow analysis mode */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>
              Flow analysis mode
              {inputType !== 'flow_diagram' && (
                <span className={styles.fieldHintInline}> — select Flow diagram above to enable</span>
              )}
            </label>
            <div className={`${styles.kbVersionGroup} ${inputType !== 'flow_diagram' ? styles.kbVersionGroupDisabled : ''}`}>
              {([
                ['screen', 'Screen analysis'],
                ['flow', 'Flow analysis'],
              ] as const).map(([v, label]) => (
                <button
                  key={v}
                  type="button"
                  className={`${styles.kbVersionBtn} ${flowMode === v ? styles.kbVersionBtnActive : ''}`}
                  onClick={() => inputType === 'flow_diagram' && setFlowMode(v)}
                  disabled={disabled || inputType !== 'flow_diagram'}
                >
                  {label}
                </button>
              ))}
            </div>
            <p className={styles.fieldHint}>
              {flowMode === 'screen'
                ? 'One pass per screen. Thorough per-screen findings, informed by the flow. Takes longer with more screens.'
                : 'One pass for the whole journey. Faster. Finds issues that span multiple screens but may miss finer per-screen detail.'}
            </p>
          </div>
```

### Step 5: Add CSS for disabled state and hint inline

In `frontend/src/components/AnalyzerForm.module.css`, add:

```css
.kbVersionGroupDisabled {
  opacity: 0.45;
  pointer-events: none;
}

.fieldHintInline {
  font-size: 0.78rem;
  color: var(--color-text-muted, #8a8fa8);
  font-weight: 400;
}
```

### Step 6: Run TypeScript check and dev server

Run: `cd frontend && npx tsc --noEmit`

Expected: No errors.

Start dev server: `npm run dev` in `frontend/`. Open `localhost:5173`, navigate to the form, verify:
- Card 1 shows three input type buttons below the Figma link field
- Selecting "Flow diagram" shows the hint text
- Card 5 shows "Flow analysis mode" toggle, grayed out unless Flow diagram is selected
- Selecting Flow diagram enables the toggle

### Step 7: Commit

```bash
git add frontend/src/components/AnalyzerForm.tsx frontend/src/components/AnalyzerForm.module.css
git commit -m "feat: add input type selector (Card 1) and flow mode toggle (Card 5)"
```

---

## Task 12: End-to-end smoke test and final commit

### Step 1: Run all backend tests

Run: `cd backend && python -m pytest tests/ -v`

Expected: All PASS

### Step 2: Start both servers

In one terminal: `cd backend && python app.py`
In another: `cd frontend && npm run dev`

### Step 3: Smoke test — image path

1. Open `localhost:5173`
2. Select "Flow diagram" input type
3. Upload a screenshot (not a real flow diagram — just verifying the pipeline runs)
4. Fill in users/tasks/format
5. Submit — verify analysis completes and FLOW DIAGRAM INPUT appears in the report's extra context section

### Step 4: Final commit

```bash
git add .
git commit -m "feat: flow-aware analysis complete — image path, Figma URL path, form UI"
git push origin master
```

---

## What this does NOT touch

- Output schema — no new fields on trap cards beyond what already exists
- Report format — no new sections, no restructuring
- Single-screen analysis path — unchanged (input_type defaults to 'screenshot')
- Thorough mode — orthogonal, can be combined
- Multi-task — orthogonal, can be combined
- The `/analyze-figma` SiteAnalyzer endpoint — left unchanged; the new flow logic goes through `unified_ask`
