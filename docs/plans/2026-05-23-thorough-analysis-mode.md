# Thorough Analysis Mode Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a "Thorough" toggle to the form that runs one analysis pass per tenet/sub-tenet group in parallel, merges all findings, and returns a single report with dramatically better trap coverage and consistency.

**Architecture:** Instead of one broad pass across all 27 traps, Thorough mode fires 12 concurrent focused passes via `ThreadPoolExecutor` — UNDERSTANDABLE and HABITUATING are each split into their three sub-tenets so no group exceeds 5 traps, and the 6 remaining tenets each run as a single group. Results are merged and deduplicated before being passed to the existing Pass 2 enrichment. Temperature is already set to 0 on all API calls — no change needed there.

**The 12 analysis groups:**
| # | Group | Traps |
|---|-------|-------|
| 1 | UNDERSTANDABLE / Noticeable | INVISIBLE ELEMENT, EFFECTIVELY INVISIBLE ELEMENT, DISTRACTION |
| 2 | UNDERSTANDABLE / Comprehensible | UNCOMPREHENDED ELEMENT, INVITING DEAD END, POOR GROUPING, FORCED SYNTAX, MEMORY CHALLENGE |
| 3 | UNDERSTANDABLE / Confirmatory | FEEDBACK FAILURE |
| 4 | COMFORTABLE | (full tenet) |
| 5 | RESPONSIVE | (full tenet) |
| 6 | EFFICIENT | (full tenet) |
| 7 | ACCURATE | (full tenet) |
| 8 | PROTECTIVE | (full tenet) |
| 9 | HABITUATING / Non-Redundant | GRATUITOUS REDUNDANCY |
| 10 | HABITUATING / Consistent with Expectations | VARIABLE OUTCOME, WANDERING ELEMENT, INCONSISTENT APPEARANCE |
| 11 | HABITUATING / Oriented | AMBIGUOUS HOME |
| 12 | BEAUTIFUL | (full tenet) |

**Tech Stack:** Python `concurrent.futures.ThreadPoolExecutor`, `copy.deepcopy`, TypeScript `UserContext`, React form toggle, FastAPI `Form` param.

---

### Preliminary Note: Temperature Already Fixed

Check `backend/src/analyzer.py` lines 180, 397, and 699 — `temperature=0` is already present on all three `client.messages.create` calls. No changes needed for temperature.

---

### Task 1: Extract `_pass1` method from `analyze_design`

**Why:** `analyze_design` currently bundles the API call, parsing, Pass 2, formatting, and metadata into one method. Thorough mode needs to call the API 8 times (once per tenet) and only run Pass 2 once on the merged result. Extracting `_pass1` makes this clean.

**Files:**
- Modify: `backend/src/analyzer.py:116-243`

**Step 1: Identify the extraction boundary**

In `analyze_design`, the Pass 1 API call spans from "Step 2: Build prompts" through "Step 5: Parse response". This is lines ~134–243. The method should take the same inputs as `analyze_design` and return just the raw `report` dict.

**Step 2: Write the extracted `_pass1` method**

Add this method to `UITrapsAnalyzer` (place it before `_enrich_report`):

```python
def _pass1(
    self,
    design_file: str,
    user_context: Dict[str, str],
    timeout: int = 120,
    kb_version: str = "v2",
    verbosity: str = "standard",
    pass1_model: Optional[str] = None,
    chat_context: Optional[str] = None,
) -> Dict[str, Any]:
    """Run Pass 1 visual analysis and return the raw report dict."""
    _model_map = {"sonnet": self.model, "haiku": self.enrich_model}
    effective_model = _model_map.get(pass1_model or "", self.model)
    pass1_max_tokens = 3000 if verbosity == "brief" else 5000

    system_prompt = build_system_prompt(
        use_caching=self.use_caching, version=kb_version, image_count=1
    )

    if is_figma_url(design_file):
        raise NotImplementedError(
            "Figma URL support requires additional implementation. "
            "Please export your Figma design as PNG/JPG and upload the image file."
        )

    image_data = self._load_image(design_file)
    user_message = build_user_message(
        user_context, image_data, page_context=None, verbosity=verbosity
    )

    if chat_context and chat_context.strip():
        context_block = {
            "type": "text",
            "text": (
                "CRITICAL OVERRIDE — UPDATED CONTEXT FROM USER:\n"
                "The user has provided corrections or clarifications in a prior conversation. "
                "These corrections OVERRIDE any conflicting values in the structured context "
                "that follows (users, tasks, format, etc.). "
                "If the user corrected the user group, tasks, or any other context field, "
                "use their corrected values and DISREGARD the original values below.\n\n"
                f"{chat_context.strip()}\n\n"
                "--- END OF USER CORRECTIONS — use these when analyzing ---\n"
            )
        }
        user_message = [context_block] + list(user_message)

    schema = get_ui_analysis_schema()

    try:
        response = self.client.messages.create(
            model=effective_model,
            max_tokens=pass1_max_tokens,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            tools=[{
                "name": "ui_analysis_report",
                "description": "Submit the complete UI Tenets & Traps analysis report",
                "input_schema": schema
            }],
            tool_choice={"type": "tool", "name": "ui_analysis_report"},
            timeout=timeout
        )
    except Exception as e:
        raise Exception(f"Claude API call failed: {e}")

    tool_use_block = next(
        (block for block in response.content if block.type == "tool_use"), None
    )
    if not tool_use_block:
        response_text = response.content[0].text
        report = parse_claude_response(response_text)
    else:
        report = tool_use_block.input
        for field in ['summary_headline', 'summary_narrative',
                      'critical_issues', 'moderate_issues', 'minor_issues']:
            if field not in report:
                raise ValueError(f"Missing required field in response: {field}")
        if not isinstance(report.get('summary_headline'), str):
            report['summary_headline'] = ''
        if not isinstance(report.get('summary_narrative'), str):
            report['summary_narrative'] = ''
        for issue_field in ['critical_issues', 'moderate_issues', 'minor_issues']:
            if not isinstance(report[issue_field], list):
                raise ValueError(f"{issue_field} must be an array")
        for opt_field in ['positive_observations', 'potential_issues',
                          'traps_checked_not_found', 'flagged_for_human_review',
                          'incomplete_flow_findings']:
            if not isinstance(report.get(opt_field), list):
                report[opt_field] = []

    return report
```

**Step 3: Replace the equivalent block in `analyze_design`**

In `analyze_design`, replace everything from "Step 2: Build prompts" (line ~134) through "Step 5: Parse response" (line ~243) with a single call:

```python
# Step 2–5: Pass 1 visual analysis
report = self._pass1(
    design_file=design_file,
    user_context=user_context,
    timeout=timeout,
    kb_version=kb_version,
    verbosity=verbosity,
    pass1_model=pass1_model,
    chat_context=chat_context,
)
```

**Step 4: Verify the existing response metadata block still runs correctly**

After the refactor, `analyze_design` should still have "Step 6: Calculate metadata" — but note: `response` object is no longer in scope. The metadata block that reads `response.usage` must be moved inside `_pass1` or dropped. Since we won't expose per-tenet token counts in thorough mode, simplify: move the metadata calculation to use a fallback dict when `response` is unavailable, OR remove the token/cost fields from metadata entirely (they will be inaccurate in thorough mode anyway).

Simplest fix — replace the metadata block in `analyze_design` with:

```python
duration = time.time() - start_time
metadata = {
    "model": self.model,
    "duration_seconds": round(duration, 2),
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "user_id": user_id,
}
```

**Step 5: Run a quick smoke test**

```bash
cd backend
python -c "
from src.analyzer import UITrapsAnalyzer
a = UITrapsAnalyzer()
print('_pass1 method exists:', hasattr(a, '_pass1'))
print('analyze_design still exists:', hasattr(a, 'analyze_design'))
"
```
Expected: both `True`.

**Step 6: Commit**

```bash
git add backend/src/analyzer.py
git commit -m "refactor: extract _pass1 from analyze_design to enable tenet-parallel mode"
```

---

### Task 2: Add `_merge_reports` static method

**Why:** Thorough mode produces 10 group-specific reports. This function merges them into one, deduplicating issues by trap name and generating a synthetic summary.

**Files:**
- Modify: `backend/src/analyzer.py` (add static method to `UITrapsAnalyzer`)

**Step 1: Add the method**

Add this as a `@staticmethod` on `UITrapsAnalyzer`, before `_pass1`:

```python
@staticmethod
def _merge_reports(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple tenet-specific Pass 1 reports into one deduplicated report."""
    try:
        from .formatters import _normalize_trap_name
    except ImportError:
        from formatters import _normalize_trap_name

    merged: Dict[str, Any] = {
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

    seen_traps: set = set()
    for report in reports:
        for severity in ('critical_issues', 'moderate_issues', 'minor_issues'):
            for issue in report.get(severity) or []:
                norm = _normalize_trap_name(issue.get('trap_name', '') or '')
                if norm and norm not in seen_traps:
                    seen_traps.add(norm)
                    merged[severity].append(issue)

    seen_pos: set = set()
    for report in reports:
        for pos in report.get('positive_observations') or []:
            if pos and pos not in seen_pos:
                seen_pos.add(pos)
                merged['positive_observations'].append(pos)

    for field in ('potential_issues', 'flagged_for_human_review',
                  'incomplete_flow_findings', 'bugs_detected'):
        for report in reports:
            items = report.get(field) or []
            if items:
                merged[field] = items
                break

    n_crit = len(merged['critical_issues'])
    n_mod = len(merged['moderate_issues'])
    n_min = len(merged['minor_issues'])
    total = n_crit + n_mod + n_min

    if total == 0:
        merged['summary_headline'] = "No UI Traps detected"
        merged['summary_narrative'] = (
            "Thorough tenet-by-tenet analysis found no usability issues."
        )
    else:
        parts = (
            ([f"{n_crit} critical"] if n_crit else []) +
            ([f"{n_mod} moderate"] if n_mod else []) +
            ([f"{n_min} minor"] if n_min else [])
        )
        merged['summary_headline'] = (
            f"{total} UI Trap{'s' if total != 1 else ''} found: {', '.join(parts)}"
        )
        merged['summary_narrative'] = (
            f"Thorough tenet-by-tenet analysis identified {total} "
            f"issue{'s' if total != 1 else ''} across the full framework "
            f"({', '.join(parts)})."
        )

    return merged
```

**Step 2: Smoke test**

```bash
cd backend
python -c "
from src.analyzer import UITrapsAnalyzer
r1 = {'critical_issues': [{'trap_name': 'POOR GROUPING', 'tenet': 'COMFORTABLE'}],
      'moderate_issues': [], 'minor_issues': [], 'positive_observations': []}
r2 = {'critical_issues': [{'trap_name': 'POOR GROUPING', 'tenet': 'COMFORTABLE'},
                           {'trap_name': 'DISTRACTION', 'tenet': 'UNDERSTANDABLE'}],
      'moderate_issues': [], 'minor_issues': [], 'positive_observations': []}
merged = UITrapsAnalyzer._merge_reports([r1, r2])
assert len(merged['critical_issues']) == 2, 'Expected 2 unique traps'
print('Merge dedup: OK')
print('Headline:', merged['summary_headline'])
"
```
Expected: `Merge dedup: OK` and a headline showing 2 traps.

**Step 3: Commit**

```bash
git add backend/src/analyzer.py
git commit -m "feat: add _merge_reports to UITrapsAnalyzer for tenet-parallel dedup"
```

---

### Task 3: Add trap-level prompt filter to `prompts.py`

**Why:** The existing `tenet_filter` tells the model "evaluate only UNDERSTANDABLE traps." For the three UNDERSTANDABLE sub-groups we need finer control: "evaluate only THESE specific traps." This requires a new `trap_filter` field in `user_context` that generates a different prompt instruction.

**Files:**
- Modify: `backend/src/prompts.py` — inside `build_user_message`

**Step 1: Find the `tenet_filter_section` block**

In `build_user_message`, locate these lines (around line 1252):

```python
tenet_filter_raw = user_context.get('tenet_filter', '')
if isinstance(tenet_filter_raw, list):
    tenet_list = [t.strip().upper() for t in tenet_filter_raw if t.strip()]
else:
    tenet_list = [t.strip().upper() for t in str(tenet_filter_raw).split(',') if t.strip()]
tenet_filter_section = f"""
⚠️ TENET SCOPE — RESTRICTED ANALYSIS:
Evaluate ONLY the following Tenets: {', '.join(tenet_list)}.
Do not report findings for traps that fall under any other Tenet. Traps outside these Tenets should be treated as out of scope and omitted from all output sections.
""" if tenet_list else ""
```

**Step 2: Add trap-level filter handling directly after**

```python
trap_filter_raw = user_context.get('trap_filter', '')
if isinstance(trap_filter_raw, list):
    trap_list = [t.strip().upper() for t in trap_filter_raw if t.strip()]
else:
    trap_list = [t.strip().upper() for t in str(trap_filter_raw).split(',') if t.strip()]

if trap_list:
    # Trap-level filter overrides tenet filter (more specific)
    tenet_filter_section = f"""
⚠️ TRAP SCOPE — RESTRICTED ANALYSIS:
Evaluate ONLY the following specific traps: {', '.join(trap_list)}.
Do not report findings for any other trap. All other traps are out of scope and must be omitted from every output section.
"""
```

**Step 3: Smoke test**

```bash
cd backend
python -c "
from src.prompts import build_user_message
ctx = {'users': 'test', 'tasks': 'test', 'format': 'PNG',
       'trap_filter': ['INVISIBLE ELEMENT', 'DISTRACTION']}
msg = build_user_message(ctx, image_data=None)
text = ' '.join(b.get('text','') for b in msg if isinstance(b, dict))
assert 'INVISIBLE ELEMENT' in text and 'DISTRACTION' in text
assert 'TRAP SCOPE' in text
print('trap_filter prompt injection: OK')
"
```
Expected: `trap_filter prompt injection: OK`.

**Step 4: Commit**

```bash
git add backend/src/prompts.py
git commit -m "feat: add trap_filter prompt injection to build_user_message"
```

---

### Task 4: Add `_run_tenet_parallel` method

**Why:** This orchestrates the 10 concurrent `_pass1` calls and returns a merged report ready for Pass 2.

**Files:**
- Modify: `backend/src/analyzer.py`

**Step 1: Add the `_ANALYSIS_GROUPS` constant near the top of the class (before `__init__`)**

Each entry is a dict with a `label` for logging and either a `tenet` key (whole tenet) or a `traps` key (specific trap names for sub-tenet groups).

```python
# Analysis groups for thorough_mode=True.
# UNDERSTANDABLE and HABITUATING are split by sub-tenet; no group exceeds 5 traps.
_ANALYSIS_GROUPS = [
    # UNDERSTANDABLE — 3 sub-tenet groups
    {'label': 'UNDERSTANDABLE/Noticeable',
     'traps': ['INVISIBLE ELEMENT', 'EFFECTIVELY INVISIBLE ELEMENT', 'DISTRACTION']},
    {'label': 'UNDERSTANDABLE/Comprehensible',
     'traps': ['UNCOMPREHENDED ELEMENT', 'INVITING DEAD END', 'POOR GROUPING',
               'FORCED SYNTAX', 'MEMORY CHALLENGE']},
    {'label': 'UNDERSTANDABLE/Confirmatory',
     'traps': ['FEEDBACK FAILURE']},
    # Full tenets
    {'label': 'COMFORTABLE',  'tenet': 'COMFORTABLE'},
    {'label': 'RESPONSIVE',   'tenet': 'RESPONSIVE'},
    {'label': 'EFFICIENT',    'tenet': 'EFFICIENT'},
    {'label': 'ACCURATE',     'tenet': 'ACCURATE'},
    {'label': 'PROTECTIVE',   'tenet': 'PROTECTIVE'},
    # HABITUATING — 3 sub-tenet groups
    {'label': 'HABITUATING/Non-Redundant',
     'traps': ['GRATUITOUS REDUNDANCY']},
    {'label': 'HABITUATING/Consistent-with-Expectations',
     'traps': ['VARIABLE OUTCOME', 'WANDERING ELEMENT', 'INCONSISTENT APPEARANCE']},
    {'label': 'HABITUATING/Oriented',
     'traps': ['AMBIGUOUS HOME']},
    # Full tenet
    {'label': 'BEAUTIFUL',    'tenet': 'BEAUTIFUL'},
]
```

**Step 2: Add `_run_tenet_parallel` method**

Add after `_merge_reports`:

```python
def _run_tenet_parallel(
    self,
    design_file: str,
    user_context: Dict[str, str],
    timeout: int = 120,
    kb_version: str = "v2",
    verbosity: str = "standard",
    pass1_model: Optional[str] = None,
    chat_context: Optional[str] = None,
) -> Dict[str, Any]:
    """Run one _pass1 per analysis group concurrently, return merged report."""
    import concurrent.futures
    from copy import deepcopy

    groups = list(self._ANALYSIS_GROUPS)
    print(f"[UITraps] Thorough mode: running {len(groups)} parallel sub-analyses")

    def analyze_one(group: dict) -> Dict[str, Any]:
        ctx = deepcopy(user_context)
        if 'traps' in group:
            # Sub-tenet group: filter to specific trap names
            ctx['trap_filter'] = group['traps']
            ctx.pop('tenet_filter', None)
        else:
            # Full tenet group
            ctx['tenet_filter'] = [group['tenet']]
            ctx.pop('trap_filter', None)
        return self._pass1(
            design_file=design_file,
            user_context=ctx,
            timeout=timeout,
            kb_version=kb_version,
            verbosity=verbosity,
            pass1_model=pass1_model,
            chat_context=chat_context,
        )

    reports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(groups)) as executor:
        future_to_group = {executor.submit(analyze_one, g): g for g in groups}
        for future in concurrent.futures.as_completed(future_to_group):
            label = future_to_group[future]['label']
            try:
                reports.append(future.result())
                print(f"[UITraps] Group complete: {label}")
            except Exception as e:
                print(f"[UITraps] Group failed ({label}): {e}")

    if not reports:
        raise Exception("All parallel sub-analyses failed")

    return self._merge_reports(reports)
```

**Step 3: Smoke test**

```bash
cd backend
python -c "
from src.analyzer import UITrapsAnalyzer
a = UITrapsAnalyzer()
print('_run_tenet_parallel exists:', hasattr(a, '_run_tenet_parallel'))
print('_ANALYSIS_GROUPS count:', len(a._ANALYSIS_GROUPS))
sub = [g for g in a._ANALYSIS_GROUPS if 'traps' in g]
tenet = [g for g in a._ANALYSIS_GROUPS if 'tenet' in g]
print(f'Sub-tenet groups: {len(sub)}, tenet groups: {len(tenet)}')
"
```
Expected: 12 groups, 6 sub-tenet (3 UNDERSTANDABLE + 3 HABITUATING), 6 full tenet.

**Step 4: Commit**

```bash
git add backend/src/analyzer.py
git commit -m "feat: add _run_tenet_parallel with 10-group UNDERSTANDABLE sub-tenet split"
```

---

### Task 4: Wire `thorough_mode` into `analyze_design`

**Why:** `analyze_design` is the public entry point. Adding `thorough_mode=True` here makes it branch to `_run_tenet_parallel` instead of `_pass1`.

**Files:**
- Modify: `backend/src/analyzer.py:78-90` (method signature) and the Pass 1 call block

**Step 1: Update `analyze_design` signature**

Add `thorough_mode: bool = False` parameter:

```python
def analyze_design(
    self,
    design_file: str,
    user_context: Dict[str, str],
    timeout: int = 120,
    user_id: Optional[str] = None,
    page_context: Optional[Dict[str, Any]] = None,
    chat_context: Optional[str] = None,
    kb_version: str = "v2",
    verbosity: str = "standard",
    pass1_model: Optional[str] = None,
    thorough_mode: bool = False,
) -> Dict[str, Any]:
```

**Step 2: Replace the Pass 1 call to branch on `thorough_mode`**

Replace the single `self._pass1(...)` call (added in Task 1) with:

```python
# Step 2–5: Pass 1 visual analysis
if thorough_mode:
    report = self._run_tenet_parallel(
        design_file=design_file,
        user_context=user_context,
        timeout=timeout,
        kb_version=kb_version,
        verbosity=verbosity,
        pass1_model=pass1_model,
        chat_context=chat_context,
    )
else:
    report = self._pass1(
        design_file=design_file,
        user_context=user_context,
        timeout=timeout,
        kb_version=kb_version,
        verbosity=verbosity,
        pass1_model=pass1_model,
        chat_context=chat_context,
    )
```

**Step 3: Pass `thorough_mode` through to `_analysis_settings` for the report metadata**

Find the `_analysis_settings` dict (added in a previous session) and add:

```python
_analysis_settings = {
    'verbosity': verbosity,
    'pass1_model': pass1_model,
    'kb_version': kb_version,
    'elapsed_seconds': _elapsed,
    'thorough_mode': thorough_mode,   # ← add this line
}
```

**Step 4: Smoke test (no API call)**

```bash
cd backend
python -c "
import inspect
from src.analyzer import UITrapsAnalyzer
sig = inspect.signature(UITrapsAnalyzer.analyze_design)
assert 'thorough_mode' in sig.parameters
print('thorough_mode param present: OK')
"
```

**Step 5: Commit**

```bash
git add backend/src/analyzer.py
git commit -m "feat: wire thorough_mode into analyze_design branching to tenet-parallel"
```

---

### Task 5: Plumb `thorough_mode` through `app.py`

**Files:**
- Modify: `backend/app.py` — the `unified_ask` function's Form params and both `analyze_design` call sites

**Step 1: Add the Form param**

In `unified_ask`, find the block of `Form(...)` parameters (around line 1868) and add:

```python
thorough_mode: Optional[bool] = Form(None),
```

**Step 2: Pass it to both `analyze_design` call sites**

There are two `analyze_design` calls in the single-image analysis branch:
1. The `kb_version == "both"` branch (two calls inside `asyncio.gather`)
2. The standard single-call branch

For the standard branch (around line 2006), add:
```python
result = get_analyzer().analyze_design(
    design_file=tmp_path, user_context=user_context,
    chat_context=chat_context, kb_version=kb_version,
    verbosity=verbosity, pass1_model=pass1_model,
    thorough_mode=bool(thorough_mode),
)
```

For the `"both"` branch, add `thorough_mode=bool(thorough_mode)` to both lambda calls.

**Step 3: Verify with a dry-run import**

```bash
cd backend
python -c "import app; print('app imports OK')"
```
Expected: `app imports OK` (no errors).

**Step 4: Commit**

```bash
git add backend/app.py
git commit -m "feat: plumb thorough_mode Form param through app.py to analyzer"
```

---

### Task 6: Show "Analysis mode: Thorough" in the report

**Files:**
- Modify: `backend/src/formatters.py` — the timestamp rendering block

**Step 1: Find the timestamp block**

In `format_report_as_html`, locate the block that builds `_ts_lines` (added in a previous session). It currently outputs Report detail, Analysis model, Knowledge base, Time to complete.

**Step 2: Add the analysis mode line**

Add before the `elapsed_seconds` line:

```python
if analysis_settings.get('thorough_mode'):
    _ts_lines.append("Analysis mode: Thorough")
```

**Step 3: Commit**

```bash
git add backend/src/formatters.py
git commit -m "feat: add 'Analysis mode: Thorough' to report metadata when thorough_mode is on"
```

---

### Task 7: Add `thorough_mode` to the TypeScript types

**Files:**
- Modify: `frontend/src/api/types.ts:112-129` — `UserContext` interface

**Step 1: Add the field**

```typescript
export interface UserContext {
  users: string;
  expertise?: string;
  tasks: string;
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
  thorough_mode?: boolean;   // ← add this line
}
```

**Step 2: Run TypeScript check**

```bash
cd frontend
npx tsc --noEmit
```
Expected: no new errors.

**Step 3: Commit**

```bash
git add frontend/src/api/types.ts
git commit -m "feat: add thorough_mode to UserContext type"
```

---

### Task 8: Send `thorough_mode` from the API client

**Files:**
- Modify: `frontend/src/api/client.ts:443-458` — the `if (context)` block in `unifiedAsk`

**Step 1: Add to the `formData` block**

After the `pass1_model` line:

```typescript
if (context.thorough_mode) formData.append('thorough_mode', 'true');
```

**Step 2: Verify with TypeScript check**

```bash
cd frontend
npx tsc --noEmit
```
Expected: no errors.

**Step 3: Commit**

```bash
git add frontend/src/api/client.ts
git commit -m "feat: send thorough_mode in unifiedAsk form data"
```

---

### Task 9: Add the toggle to the form (Card 5)

**Files:**
- Modify: `frontend/src/components/AnalyzerForm.tsx`

**Step 1: Add state**

In the Card 5 state block (around line 141), add:

```typescript
const [thoroughMode, setThoroughMode] = useState(false);
```

**Step 2: Add `thorough_mode` to `assembleContext`**

In the `assembleContext` function signature, add `thoroughMode: boolean` to the fields destructured. In the return value:

```typescript
thorough_mode: thoroughMode || undefined,
```

**Step 3: Pass it in `handleSubmit`**

Add `thoroughMode` to the `assembleContext(...)` call:

```typescript
const context = assembleContext({
  ...,   // existing fields
  thoroughMode,
});
```

Add `thoroughMode` to the `useCallback` dependency array.

**Step 4: Add the toggle UI in Card 5**

Place it after the knowledge base version divider, before the submit card. Follow the exact same pattern as the existing Report detail / Analysis model toggles:

```tsx
<hr className={styles.fieldDivider} />

{/* Thorough analysis mode */}
<div className={styles.field}>
  <label className={styles.fieldLabel}>Analysis coverage</label>
  <div className={styles.kbVersionGroup}>
    {([false, true] as const).map(v => (
      <button
        key={String(v)}
        type="button"
        className={`${styles.kbVersionBtn} ${thoroughMode === v ? styles.kbVersionBtnActive : ''}`}
        onClick={() => setThoroughMode(v)}
        disabled={disabled}
      >
        {v ? 'Thorough' : 'Standard'}
      </button>
    ))}
  </div>
  <p className={styles.fieldHint}>
    {!thoroughMode && 'Single-pass analysis. Fast, good coverage for most designs.'}
    {thoroughMode && 'Runs one pass per Tenet in parallel, then merges findings. More consistent results, ~same speed. Recommended for final reviews.'}
  </p>
</div>
```

**Step 5: Run TypeScript check**

```bash
cd frontend
npx tsc --noEmit
```
Expected: no errors.

**Step 6: Commit**

```bash
git add frontend/src/components/AnalyzerForm.tsx
git commit -m "feat: add Thorough analysis mode toggle to form Card 5"
```

---

### Task 10: End-to-end test

**Step 1: Start both servers**

Terminal 1:
```bash
cd backend
python app.py
```

Terminal 2:
```bash
cd frontend
npm run dev
```

**Step 2: Run a standard analysis first**

- Open `localhost:5173`
- Upload a screenshot, fill the form
- Leave "Analysis coverage" on **Standard**
- Submit and confirm report renders normally

**Step 3: Run a thorough analysis**

- Click **New Analysis**
- Upload the same screenshot
- Switch "Analysis coverage" to **Thorough**
- Submit
- Expected: analysis runs (may take 60–90s)
- Expected: report shows **Analysis mode: Thorough** in the metadata timestamp block
- Expected: report contains more findings than the standard run (verify this against the standard run on the same image)

**Step 4: Check backend logs**

Look for lines like:
```
[UITraps] Thorough mode: running 8 tenet sub-analyses in parallel
[UITraps] Tenet complete: UNDERSTANDABLE
[UITraps] Tenet complete: COMFORTABLE
...
[UITraps] Pass 2: enriching N trap(s)...
```

**Step 5: Final commit if all looks good**

```bash
git add -A
git commit -m "feat: thorough analysis mode — tenet-parallel execution complete"
```

---

### Cost and Performance Notes

- **Standard mode**: 1 Pass 1 call (~3000–5000 output tokens) + 1 Pass 2 call
- **Thorough mode**: 12 parallel Pass 1 calls (~300–800 output tokens each) + 1 Pass 2 call
- **Wall-clock time**: similar to standard (parallel); sub-tenet groups produce shorter output than a full-tenet call so individual calls finish faster
- **Token cost**: roughly 2–3× standard due to 12 system-prompt loads (mostly cached reads at $0.30/M)
- **Coverage improvement**: expected ~85–95% of available traps vs ~50–60% in standard mode
