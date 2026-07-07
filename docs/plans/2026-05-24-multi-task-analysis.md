# Multi-Task Analysis Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the single Tasks text field with up to 3 user-named task rows (label + description), and restructure the output report into General Findings + per-task sections when multiple tasks are submitted.

**Architecture:** Task rows are serialized as a JSON array (`task_list`) and sent alongside the existing `tasks` string field (backward compat). The backend injects per-task attribution instructions into the prompt, and the formatter groups the "Traps Found" section by `task` field on each issue. Single-task behavior is unchanged throughout.

**Tech Stack:** React/TypeScript (frontend), FastAPI/Python (backend), Claude structured output via JSON schema

---

## Key facts before you start

- The active form file is `frontend/src/components/AnalyzerForm.tsx`. The task input is a single `<input>` named `userGoal` inside Card 2 (lines ~534–550).
- `assembleContext()` builds the `UserContext` object; it sets `tasks: userGoal`.
- The API call is `unifiedAsk` in `frontend/src/api/client.ts` (line 445: `formData.append('tasks', context.tasks)`).
- The FastAPI endpoint is `unified_ask` in `backend/app.py` (line 1852). It currently receives `tasks: Optional[str] = Form(None)`.
- The prompt is built in `backend/src/prompts.py`. Tasks are injected at line 1351: `{user_context['tasks']}`.
- The JSON schema for model output is `UI_ANALYSIS_SCHEMA` in `backend/src/schema.py`. It has `additionalProperties: False` — any new field on issues **must** be added here.
- The HTML report renderer is `format_report_as_html` in `backend/src/formatters.py`. The "Traps Found" section starts around line 2409. It renders issues as a flat list grouped by confidence (Higher/Lower). This is what we restructure for multi-task.
- `user_context` is passed into `format_report_as_html` as a second argument — we can read `task_list` from it in the formatter.

---

## Task 1: Add `task` field to issue schema

**Files:**
- Modify: `backend/src/schema.py` (lines 65–184, the three issue array definitions)

**Step 1: Add `task` property to each issue item**

In `UI_ANALYSIS_SCHEMA`, the `critical_issues`, `moderate_issues`, and `minor_issues` arrays each define an `items` object. Add a `task` property to each. The property definition is identical for all three.

In the `critical_issues` items `properties` dict (after `"confidence"` and before `"region"`), add:
```python
"task": {
    "type": "string",
    "description": (
        "Task this finding most directly relates to. "
        "Set to the exact task name from the WHAT IS THE TASK BEING EVALUATED section, "
        "or 'general' if the issue applies across all tasks or is not task-specific. "
        "Omit when only one task is defined."
    )
},
```

Repeat this addition in the `moderate_issues` items and `minor_issues` items blocks. Do NOT add `task` to the `required` list — it is optional.

**Step 2: Verify schema is valid**

Run: `python -c "from backend.src.schema import UI_ANALYSIS_SCHEMA; print('OK')"` from the repo root.
Expected: `OK`

**Step 3: Commit**
```
git add backend/src/schema.py
git commit -m "feat: add optional task field to issue schema for multi-task attribution"
```

---

## Task 2: Inject task attribution in the prompt

**Files:**
- Modify: `backend/src/prompts.py` (around lines 1343–1354)

**Step 1: Replace the single tasks line with conditional multi-task block**

Find this section (around line 1343):
```python
    context_text = f"""Please analyze this UI design using the UI Tenets & Traps framework.

CONTEXT PROVIDED BY USER:

1. WHO ARE THE USERS?
{user_context['users']}
{expertise_section}
{"3" if has_expertise else "2"}. WHAT IS THE TASK BEING EVALUATED?
{user_context['tasks']}

⚠️ IMPORTANT — TASK SCOPE: ...
```

Replace the `WHAT IS THE TASK BEING EVALUATED?` block with the following (keep everything else unchanged):

```python
    _task_list = user_context.get('task_list') or []
    _multi_task = len(_task_list) > 1
    if _multi_task:
        _task_lines = []
        for _idx, _t in enumerate(_task_list, 1):
            _name = _t.get('name', '').strip()
            _desc = _t.get('description', '').strip()
            _task_lines.append(f"{_idx}. {(_name + ': ' + _desc) if _name else _desc}")
        _tasks_block = '\n'.join(_task_lines)
        _task_attribution = (
            "\n⚠️ MULTI-TASK ATTRIBUTION: Multiple tasks are defined above. "
            "For every finding in critical_issues, moderate_issues, and minor_issues, "
            "set the `task` field to the exact task name it most directly applies to "
            "(use the name exactly as written above, e.g. 'Checkout', not a paraphrase), "
            "or to 'general' if the issue applies equally across all tasks or is not "
            "task-specific. Every issue must have a `task` field when multiple tasks are defined."
        )
    else:
        _tasks_block = user_context['tasks']
        _task_attribution = ""
```

Then in `context_text`, change the tasks line from:
```python
{"3" if has_expertise else "2"}. WHAT IS THE TASK BEING EVALUATED?
{user_context['tasks']}
```
to:
```python
{"3" if has_expertise else "2"}. WHAT IS THE TASK BEING EVALUATED?
{_tasks_block}
{_task_attribution}
```

**Step 2: Verify the module imports without error**

Run: `python -c "from backend.src.prompts import build_analysis_prompt; print('OK')"` (adjust to the actual function name if different).

**Step 3: Commit**
```
git add backend/src/prompts.py
git commit -m "feat: inject multi-task attribution instructions into analysis prompt"
```

---

## Task 3: Parse task_list in the backend endpoint

**Files:**
- Modify: `backend/app.py` (function `unified_ask`, starting line 1852)

**Step 1: Add `task_list` form parameter**

In the `unified_ask` function signature, add this parameter after `thorough_mode`:
```python
task_list: Optional[str] = Form(None),
```

**Step 2: Parse task_list and inject into user_context**

There are two `user_context` dict constructions in `unified_ask` — one for single-image (around line 1958) and one for multi-image (search for the second occurrence). Apply the same change to both.

After the `task_list` param is available, add this parse block near the top of the `ANALYSIS` branch (before the first `user_context = {...}` line):

```python
_task_list_parsed = []
if task_list:
    try:
        _task_list_parsed = json.loads(task_list)
        if not isinstance(_task_list_parsed, list):
            _task_list_parsed = []
    except (json.JSONDecodeError, TypeError):
        _task_list_parsed = []
```

Then in each `user_context = {...}` dict, add:
```python
"task_list": _task_list_parsed,
```

**Step 3: Verify the server starts without error**

Start the backend: `cd backend && python app.py`
Expected: server starts on port 8000, no import errors.

**Step 4: Commit**
```
git add backend/app.py
git commit -m "feat: parse task_list JSON field in unified_ask endpoint"
```

---

## Task 4: Update TypeScript types

**Files:**
- Modify: `frontend/src/api/types.ts`

**Step 1: Add `task_list` to `UserContext`**

Find the `UserContext` interface (around line 112). Add after `tasks: string;`:
```typescript
task_list?: Array<{ name: string; description: string }>;
```

**Step 2: Verify TypeScript compiles**

Run: `cd frontend && npx tsc --noEmit`
Expected: no errors.

**Step 3: Commit**
```
git add frontend/src/api/types.ts
git commit -m "feat: add task_list to UserContext type"
```

---

## Task 5: Send task_list in API client

**Files:**
- Modify: `frontend/src/api/client.ts` (function `unifiedAsk`, around line 443)

**Step 1: Append task_list to FormData**

In `unifiedAsk`, inside the `if (context)` block, after the existing `formData.append('tasks', context.tasks)` line, add:
```typescript
if (context.task_list && context.task_list.length > 1) {
  formData.append('task_list', JSON.stringify(context.task_list));
}
```

**Step 2: Verify TypeScript compiles**

Run: `cd frontend && npx tsc --noEmit`
Expected: no errors.

**Step 3: Commit**
```
git add frontend/src/api/client.ts
git commit -m "feat: send task_list JSON field in unifiedAsk when multiple tasks defined"
```

---

## Task 6: Replace Tasks field in the form with multi-task rows

**Files:**
- Modify: `frontend/src/components/AnalyzerForm.tsx`

This is the largest change. Follow carefully.

**Step 1: Replace `userGoal` state with a tasks array**

Remove:
```typescript
const [userGoal, setUserGoal] = useState('');
```

Add:
```typescript
const [tasks, setTasks] = useState<Array<{ name: string; description: string }>>([
  { name: '', description: '' },
]);
```

Add three task-management helpers (place these after `toggleTenet`):
```typescript
const addTask = useCallback(() => {
  setTasks(prev => prev.length < 3 ? [...prev, { name: '', description: '' }] : prev);
}, []);

const removeTask = useCallback((index: number) => {
  setTasks(prev => prev.length > 1 ? prev.filter((_, i) => i !== index) : prev);
}, []);

const updateTask = useCallback((index: number, field: 'name' | 'description', value: string) => {
  setTasks(prev => prev.map((t, i) => i === index ? { ...t, [field]: value } : t));
}, []);
```

**Step 2: Update validation**

In `validate()`, change:
```typescript
if (!userGoal.trim()) e.userGoal = 'Required';
```
to:
```typescript
if (!tasks[0]?.description.trim()) e.userGoal = 'Required';
```

And update the deps array of `validate`:
```typescript
}, [files, screenName, platform, productDomain, expLevel, techSavvy, frequency, tasks]);
```

**Step 3: Update `assembleContext` signature and call**

In the `assembleContext` function signature (the `fields` parameter type), replace:
```typescript
  userGoal: string;
```
with:
```typescript
  taskList: Array<{ name: string; description: string }>;
```

In the destructuring inside `assembleContext`, replace `userGoal` with `taskList`.

Replace this line in the return value:
```typescript
    tasks: userGoal,
```
with:
```typescript
    tasks: taskList
      .filter(t => t.description.trim())
      .map(t => (t.name.trim() ? `${t.name}: ${t.description}` : t.description))
      .join('. '),
    task_list: taskList.filter(t => t.description.trim()).length > 1
      ? taskList.filter(t => t.description.trim())
      : undefined,
```

**Step 4: Update `handleSubmit` call to `assembleContext`**

In `handleSubmit`, change the `assembleContext` call to pass `taskList: tasks` instead of `userGoal`.

Update the `useCallback` deps array for `handleSubmit`: replace `userGoal` with `tasks`.

**Step 5: Replace the Tasks UI field in Card 2**

Find and replace the entire `userGoal` field block (the `<div className={styles.field}>` containing the `userGoal` input, around lines 534–550). Replace with:

```tsx
<div className={`${styles.field} ${styles.span2}`}>
  <label className={styles.fieldLabel}>
    <span className={styles.req} />
    User task(s) to evaluate
  </label>
  <p className={styles.fieldHint}>
    The specific outcome(s) users are trying to achieve on this screen or flow.
    Adding a second or third task will increase analysis time but produces
    a report with a General Findings section plus one section per task.
  </p>
  {tasks.map((task, i) => (
    <div key={i} className={styles.taskRow}>
      <div className={styles.taskRowInputs}>
        <input
          type="text"
          className={styles.input}
          placeholder={`Task ${i + 1} name (e.g., Complete checkout)`}
          value={task.name}
          onChange={e => updateTask(i, 'name', e.target.value)}
          disabled={disabled}
        />
        <input
          type="text"
          className={`${styles.input} ${i === 0 && errors.userGoal ? styles.inputError : ''}`}
          placeholder="Describe what the user is trying to accomplish…"
          value={task.description}
          onChange={e => updateTask(i, 'description', e.target.value)}
          disabled={disabled}
        />
      </div>
      {tasks.length > 1 && (
        <button
          type="button"
          className={styles.taskRemoveBtn}
          onClick={() => removeTask(i)}
          disabled={disabled}
          title="Remove task"
        >×</button>
      )}
    </div>
  ))}
  {tasks.length < 3 && (
    <button
      type="button"
      className={styles.taskAddBtn}
      onClick={addTask}
      disabled={disabled}
    >
      + Add task
    </button>
  )}
  {errors.userGoal && <p className={styles.fieldError}>{errors.userGoal}</p>}
</div>
```

**Step 6: Add CSS for task rows**

Open `frontend/src/components/AnalyzerForm.module.css`. Add at the end:

```css
.taskRow {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 10px;
}

.taskRowInputs {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.taskRemoveBtn {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border: 1px solid #d9d5ce;
  border-radius: 6px;
  background: #fff;
  color: #8a8680;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}

.taskRemoveBtn:hover {
  border-color: #b0aca5;
  color: #333;
}

.taskAddBtn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px dashed #b0aca5;
  border-radius: 6px;
  background: transparent;
  color: #5a5650;
  font-size: 0.88em;
  cursor: pointer;
  margin-top: 2px;
}

.taskAddBtn:hover {
  border-color: #6b6660;
  color: #222;
}
```

**Step 7: Verify TypeScript compiles**

Run: `cd frontend && npx tsc --noEmit`
Expected: no errors.

**Step 8: Commit**
```
git add frontend/src/components/AnalyzerForm.tsx frontend/src/components/AnalyzerForm.module.css
git commit -m "feat: replace single Tasks field with multi-task rows (up to 3, user-named)"
```

---

## Task 7: Restructure "Traps Found" section in formatter for multi-task

**Files:**
- Modify: `backend/src/formatters.py` (around lines 2409–2455)

**Step 1: Understand current structure**

The "Traps Found" block currently looks like:
```python
all_confirmed = (
    [('critical', i) for i in report.get('critical_issues', [])] +
    [('moderate', i) for i in report.get('moderate_issues', [])] +
    [('minor', i) for i in report.get('minor_issues', [])]
)
# ... split into high_conf / low_conf ...
if high_conf or low_conf:
    html.append("<div class='issues-section'>")
    html.append("<h2>Traps Found</h2>")
    # ... renders cards ...
    html.append("</div>")
```

**Step 2: Add a helper function above the "Traps Found" block**

Just before the `all_confirmed = (` line, add this helper:

```python
def _render_confidence_groups(issues_with_sev, finding_counter_start=1):
    """Render a list of (sev_class, issue) tuples as Higher/Lower confidence sub-groups.
    Returns (html_fragment_list, next_finding_number)."""
    _frag = []
    _sev_order = {'critical': 0, 'moderate': 1, 'minor': 2}
    _hc = sorted(
        [(s, i) for s, i in issues_with_sev if i.get('confidence', '').lower() == 'high'],
        key=lambda x: _sev_order.get(x[0], 2)
    )
    _lc = sorted(
        [(s, i) for s, i in issues_with_sev if i.get('confidence', '').lower() != 'high'],
        key=lambda x: _sev_order.get(x[0], 2)
    )
    _n = finding_counter_start
    if _hc:
        _frag.append("<h3 class='confidence-group-header'>Higher confidence</h3>")
        for sev_class, issue in _hc:
            render_trap_card(issue, sev_class, _n)
            _frag.extend(html)  # render_trap_card appends to outer html; see note below
            _n += 1
    if _lc:
        _frag.append("<h3 class='confidence-group-header'>Lower confidence</h3>")
        for sev_class, issue in _lc:
            render_trap_card(issue, sev_class, _n)
            _n += 1
    return _n
```

**Note on implementation pattern**: `render_trap_card` already appends directly to the outer `html` list (it's a closure). So we don't need to collect fragments separately — we just call `render_trap_card` and it appends to `html`. The restructuring is in _how we organize the h2/h3 section headers_ around those calls. The helper above is a guide to the logic; the actual implementation inlines the confidence split into the per-task loop rather than an extracted function (avoids closure complications).

**Step 3: Replace the "Traps Found" block with multi-task-aware version**

Replace the entire block from `all_confirmed = (` through the closing `html.append("</div>")` of the Traps Found section with:

```python
    # ── Traps Found ──
    all_confirmed = (
        [('critical', i) for i in report.get('critical_issues', [])] +
        [('moderate', i) for i in report.get('moderate_issues', [])] +
        [('minor', i) for i in report.get('minor_issues', [])]
    )
    sev_order = {'critical': 0, 'moderate': 1, 'minor': 2}

    # Fold potential_issues into the lower-confidence pool
    potential_pool = []
    for p in report.get('potential_issues', []):
        norm = dict(p)
        if 'problem' not in norm and 'observation' in norm:
            norm['problem'] = norm.pop('observation')
        norm.setdefault('confidence', 'low')
        if not norm.get('headline') and norm.get('trap_name'):
            norm['headline'] = norm['trap_name'].title()
        potential_pool.append(('minor', norm))

    _task_list = (user_context or {}).get('task_list') or []
    _multi_task = len(_task_list) > 1

    html.append("<div class='issues-section'>")
    html.append("<h2>Traps Found</h2>")

    if not all_confirmed and not potential_pool:
        html.append("<p class='none-found'>No confirmed traps found ✓</p>")
    elif _multi_task:
        # Build per-task and general buckets
        task_names = [t.get('name') or t.get('description', f'Task {i+1}')
                      for i, t in enumerate(_task_list)]

        def _match_task(issue_task_field):
            if not issue_task_field or issue_task_field.lower() == 'general':
                return None
            itf_lower = issue_task_field.lower()
            for tn in task_names:
                if tn.lower() == itf_lower or tn.lower() in itf_lower or itf_lower in tn.lower():
                    return tn
            return None  # unmatched → general

        general_issues = []
        per_task = {tn: [] for tn in task_names}
        for sev_class, issue in all_confirmed + potential_pool:
            matched = _match_task(issue.get('task', ''))
            if matched:
                per_task[matched].append((sev_class, issue))
            else:
                general_issues.append((sev_class, issue))

        finding_num = 0

        def _render_group(items):
            nonlocal finding_num
            hc = sorted(
                [(s, i) for s, i in items if i.get('confidence', '').lower() == 'high'],
                key=lambda x: sev_order.get(x[0], 2)
            )
            lc = sorted(
                [(s, i) for s, i in items if i.get('confidence', '').lower() != 'high'],
                key=lambda x: sev_order.get(x[0], 2)
            )
            if hc:
                html.append("<h3 class='confidence-group-header'>Higher confidence</h3>")
                for sc, iss in hc:
                    finding_num += 1
                    render_trap_card(iss, sc, finding_num)
            if lc:
                html.append("<h3 class='confidence-group-header'>Lower confidence</h3>")
                for sc, iss in lc:
                    finding_num += 1
                    render_trap_card(iss, sc, finding_num)

        # General Findings first
        if general_issues:
            html.append("<h3 class='task-section-header'>General Findings</h3>")
            html.append("<p class='task-section-desc'>These findings apply across all tasks or are not task-specific.</p>")
            _render_group(general_issues)

        # Per-task sections
        for tn in task_names:
            bucket = per_task.get(tn, [])
            if bucket:
                html.append(f"<h3 class='task-section-header'>Task: {tn}</h3>")
                _render_group(bucket)

    else:
        # Single-task: existing flat confidence split
        high_conf = sorted(
            [(s, i) for s, i in all_confirmed if i.get('confidence', '').lower() == 'high'],
            key=lambda x: sev_order.get(x[0], 2)
        )
        low_conf = sorted(
            [(s, i) for s, i in all_confirmed if i.get('confidence', '').lower() != 'high'],
            key=lambda x: sev_order.get(x[0], 2)
        ) + potential_pool

        finding_num = 0
        if high_conf:
            html.append("<h3 class='confidence-group-header'>Higher confidence</h3>")
            for sev_class, issue in high_conf:
                finding_num += 1
                render_trap_card(issue, sev_class, finding_num)
        if low_conf:
            html.append("<h3 class='confidence-group-header'>Lower confidence</h3>")
            for sev_class, issue in low_conf:
                finding_num += 1
                render_trap_card(issue, sev_class, finding_num)

    html.append("</div>")
```

**Step 4: Add CSS for task-section headers**

In `get_report_base_css()` (around line 726), inside the returned CSS string, add:

```css
.task-section-header {
    font-size: 1.05em;
    font-weight: 700;
    color: #2c2a27;
    margin: 28px 0 4px;
    padding-bottom: 6px;
    border-bottom: 2px solid #e4e1dc;
}
.task-section-desc {
    color: #8a8680;
    font-size: 0.88em;
    margin: 0 0 14px;
}
```

**Step 5: Update "Evaluation Details" task display for multi-task**

In the "Evaluation Details" section (around line 2137), replace:
```python
        raw_tasks = user_context.get('tasks', 'N/A')
        task_list = parse_tasks(raw_tasks)
        html.append("<p><strong>Task(s) evaluated:</strong></p>")
        html.append("<ul>")
        for task in task_list:
            html.append(f"<li>{task}</li>")
        html.append("</ul>")
```
with:
```python
        _tl = user_context.get('task_list') or []
        if len(_tl) > 1:
            html.append("<p><strong>Task(s) evaluated:</strong></p>")
            html.append("<ul>")
            for _t in _tl:
                _n = _t.get('name', '').strip()
                _d = _t.get('description', '').strip()
                html.append(f"<li><strong>{_n}</strong>{': ' + _d if _d else ''}</li>" if _n else f"<li>{_d}</li>")
            html.append("</ul>")
        else:
            raw_tasks = user_context.get('tasks', 'N/A')
            task_list_display = parse_tasks(raw_tasks)
            html.append("<p><strong>Task(s) evaluated:</strong></p>")
            html.append("<ul>")
            for task in task_list_display:
                html.append(f"<li>{task}</li>")
            html.append("</ul>")
```

**Step 6: Commit**
```
git add backend/src/formatters.py
git commit -m "feat: restructure Traps Found section into General + per-task sections for multi-task reports"
```

---

## Task 8: Manual end-to-end test

**Step 1: Start both servers**
- Backend: `cd backend && python app.py`
- Frontend: `cd frontend && npm run dev`
- Open: http://localhost:5173

**Step 2: Single-task smoke test**
- Submit a screenshot with only one task row filled in
- Verify the report looks identical to before (flat confidence groups, no task headers)
- Verify "Task(s) evaluated" in Evaluation Details shows the single task correctly

**Step 3: Two-task test**
- Fill in two task rows:
  - Task 1 name: `Checkout`, description: `Complete a purchase`
  - Task 2 name: `Find order`, description: `Locate a past order in order history`
- Submit a screenshot
- Verify the report has:
  - A "General Findings" section (may be empty if model attributes all issues)
  - A "Task: Checkout" section
  - A "Task: Find order" section
  - Each section has Higher/Lower confidence sub-headers where applicable
- Verify "Task(s) evaluated" in Evaluation Details shows both tasks with their names and descriptions

**Step 4: Commit any CSS tweaks observed during testing**
```
git add -p
git commit -m "fix: visual tweaks to multi-task report sections"
```

---

## Task 9: Push

```
git push
```

---

## Notes

- The `_render_group` inner function uses `nonlocal finding_num` to keep finding numbers sequential across all sections (General → Task 1 → Task 2). This means finding #3 in "Task: Checkout" continues from where General Findings left off — intentional so PDF-viewers can reference "Finding 5" unambiguously.
- If the model returns a `task` field value that doesn't exactly match any task name (e.g. it paraphrases), `_match_task` fuzzy-matches on substring containment. Unmatched issues fall into General.
- `additionalProperties: False` in the schema means the schema must list `task` — otherwise Claude's response will fail schema validation and the analysis will error. Task 1 (schema update) must land before any multi-task analysis is attempted.
