# User Issues Report Mode Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a "User Issues" report style that synthesizes KB-detected Trap findings into user-centric problem descriptions, grouping related Traps under a single headline with root cause attribution.

**Architecture:** Pass 1 (Trap detection) and Pass 2 (enrichment) run unchanged. When `report_style=issues` is selected, a new Pass 3 synthesis step takes the enriched per-Trap findings and groups Traps that share a common design element/problem into user-centric issues — with the grouping driven by Claude reasoning over confirmed KB findings, not generic UX assessment. A new formatter renders the issues HTML layout. The existing Trap-view report is unaffected.

**Tech Stack:** Python/FastAPI backend, Anthropic SDK (claude-haiku-4-5-20251001 for Pass 3), React/TypeScript frontend, HTML/CSS report generation in formatters.py.

---

## Task 1: Add USER_ISSUES_SCHEMA to schema.py

**Files:**
- Modify: `backend/src/schema.py` (append after `UI_ANALYSIS_SCHEMA`)

**Step 1: Write a failing test**

Create `tests/unit/test_user_issues_schema.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend/src'))

from schema import get_user_issues_schema, VALID_TRAP_NAMES, VALID_TENET_NAMES

def test_schema_exists():
    schema = get_user_issues_schema()
    assert schema is not None

def test_schema_required_fields():
    schema = get_user_issues_schema()
    required = schema["required"]
    assert "summary_headline" in required
    assert "summary_narrative" in required
    assert "issues" in required
    assert "positive_observations" in required
    assert "traps_checked_not_found" in required

def test_issue_item_required_fields():
    schema = get_user_issues_schema()
    issue_schema = schema["properties"]["issues"]["items"]
    required = issue_schema["required"]
    assert "headline" in required
    assert "severity" in required
    assert "confidence" in required
    assert "root_cause_trap" in required
    assert "description" in required
    assert "recommendation" in required

def test_root_cause_trap_structure():
    schema = get_user_issues_schema()
    rct = schema["properties"]["issues"]["items"]["properties"]["root_cause_trap"]
    assert "trap_name" in rct["properties"]
    assert "tenet" in rct["properties"]
    assert "definition" in rct["properties"]
    assert rct["properties"]["trap_name"]["enum"] == VALID_TRAP_NAMES
```

**Step 2: Run test to verify it fails**

```
cd backend
python -m pytest ../tests/unit/test_user_issues_schema.py -v
```
Expected: FAIL with `ImportError: cannot import name 'get_user_issues_schema'`

**Step 3: Add the schema to `backend/src/schema.py`**

Append after the closing brace of `UI_ANALYSIS_SCHEMA` (after line 414):

```python
# Schema for Pass 3 user-issues synthesis output
USER_ISSUES_SCHEMA = {
    "type": "object",
    "properties": {
        "summary_headline": {
            "type": "string",
            "description": "One sentence capturing the most significant user-facing issue. Use measured language: 'appears to', 'may affect'. Do NOT write a count."
        },
        "summary_narrative": {
            "type": "string",
            "description": "A single paragraph (3-5 sentences) summarising the overall picture for a reader who has not yet seen the findings. Use hedged language throughout."
        },
        "issues": {
            "type": "array",
            "description": "User-facing problems, each grouping one or more related Traps that share a common design element or underlying problem.",
            "items": {
                "type": "object",
                "properties": {
                    "headline": {
                        "type": "string",
                        "description": "One sentence describing the problem in user-relatable terms, tied to the specific design and context. Avoid Trap jargon. Use measured language."
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "moderate", "minor"],
                        "description": "Severity of the issue — take the highest severity among the grouped Traps."
                    },
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Confidence in this issue — take the lowest confidence among the grouped Traps."
                    },
                    "root_cause_trap": {
                        "type": "object",
                        "description": "The Trap that best represents the root cause of this issue. Required even for single-Trap issues.",
                        "properties": {
                            "trap_name": {
                                "type": "string",
                                "enum": VALID_TRAP_NAMES,
                                "description": "Trap name — MUST be one of the 27 valid trap names"
                            },
                            "tenet": {
                                "type": "string",
                                "enum": VALID_TENET_NAMES
                            },
                            "definition": {
                                "type": "string",
                                "description": "One-sentence definition of this Trap as it applies to the observed problem."
                            }
                        },
                        "required": ["trap_name", "tenet", "definition"]
                    },
                    "contributing_traps": {
                        "type": "array",
                        "description": "Additional Traps whose definitions are also satisfied by this same design problem. Empty array if none.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "trap_name": {
                                    "type": "string",
                                    "enum": VALID_TRAP_NAMES
                                },
                                "tenet": {
                                    "type": "string",
                                    "enum": VALID_TENET_NAMES
                                },
                                "definition": {
                                    "type": "string",
                                    "description": "One-sentence definition of this Trap as it applies to the observed problem."
                                }
                            },
                            "required": ["trap_name", "tenet", "definition"]
                        }
                    },
                    "description": {
                        "type": "string",
                        "description": "2-4 sentences describing the issue from the user's perspective. What does the user encounter? Why does it cause a problem? Use measured language."
                    },
                    "recommendation": {
                        "type": "string",
                        "description": "2-3 sentences suggesting how the issue might be addressed. Use advisory language: 'one approach would be', 'consider', 'it may help to'."
                    },
                    "region": {
                        "type": "object",
                        "description": "Bounding box of the design element that best illustrates this issue. Normalized 0.0-1.0, origin top-left. Omit if no single element can be bounded or crop would not add evidence.",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "width": {"type": "number"},
                            "height": {"type": "number"},
                            "caption": {"type": "string", "description": "What the crop shows and how it illustrates this issue."}
                        },
                        "required": ["x", "y", "width", "height"]
                    }
                },
                "required": ["headline", "severity", "confidence", "root_cause_trap", "contributing_traps", "description", "recommendation"]
            }
        },
        "positive_observations": {
            "type": "array",
            "items": {"type": "string"}
        },
        "traps_checked_not_found": {
            "type": "array",
            "description": "Pass-through from the underlying Trap analysis — traps evaluated and not found.",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {"type": "string"},
                    "testable": {"type": "boolean"}
                },
                "required": ["trap_name", "testable"]
            }
        }
    },
    "required": [
        "summary_headline",
        "summary_narrative",
        "issues",
        "positive_observations",
        "traps_checked_not_found"
    ],
    "additionalProperties": False
}


def get_user_issues_schema():
    """Get the JSON schema for Pass 3 user-issues synthesis output."""
    return USER_ISSUES_SCHEMA
```

**Step 4: Run test to verify it passes**

```
cd backend
python -m pytest ../tests/unit/test_user_issues_schema.py -v
```
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add backend/src/schema.py tests/unit/test_user_issues_schema.py
git commit -m "feat: add USER_ISSUES_SCHEMA for Pass 3 synthesis output"
```

---

## Task 2: Add Pass 3 synthesis prompts to prompts.py

**Files:**
- Modify: `backend/src/prompts.py` (append two new functions at the end)

**Step 1: Write a failing test**

Add to `tests/unit/test_user_issues_schema.py`:

```python
from prompts import build_synthesis_system_prompt, build_synthesis_user_message

def test_synthesis_system_prompt_exists():
    prompt = build_synthesis_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 100

def test_synthesis_user_message_structure():
    mock_report = {
        "critical_issues": [],
        "moderate_issues": [
            {
                "trap_name": "GRATUITOUS REDUNDANCY",
                "tenet": "HABITUATING",
                "headline": "Two nav bars duplicate site navigation.",
                "location": "Top of page",
                "problem": "Two horizontal navigation bars appear simultaneously.",
                "recommendation": "Consolidate into one.",
                "confidence": "medium"
            }
        ],
        "minor_issues": [],
        "positive_observations": ["Clean typography"],
        "traps_checked_not_found": [{"trap_name": "DISTRACTION", "testable": True}]
    }
    msg = build_synthesis_user_message(mock_report)
    assert "GRATUITOUS REDUNDANCY" in msg
    assert "HABITUATING" in msg
```

Run: `python -m pytest ../tests/unit/test_user_issues_schema.py::test_synthesis_system_prompt_exists -v`
Expected: FAIL with ImportError

**Step 2: Add the functions to `backend/src/prompts.py`**

Append at the end of the file:

```python
def build_synthesis_system_prompt() -> str:
    """
    System prompt for Pass 3: synthesise per-Trap findings into user-centric issues.

    The synthesis is grounded in the confirmed Trap findings from Pass 1+2.
    Claude must not introduce new problems not supported by the Trap findings.
    """
    return """You are a UI usability analyst synthesising confirmed findings from a structured Trap analysis.

You will receive a set of confirmed UI Trap findings — each one was identified by applying the UI Tenets & Traps knowledge base to the submitted design. Your job is to group related findings into user-facing issues and write each issue in plain language.

CRITICAL RULES:
1. Only report problems that are grounded in the confirmed Trap findings provided. Do not introduce new problems not supported by the Trap data.
2. Group two or more Trap findings into a single issue ONLY when they describe the same design element or share the same underlying cause on the same part of the interface. Do not group findings that happen to be the same severity — they must share a root.
3. Single-Trap findings that do not share a root with another finding become single-Trap issues (contributing_traps is empty array).
4. For each issue, identify the root_cause_trap — the Trap whose definition most directly names the source of the problem. Contributing Traps are downstream consequences or co-occurring effects of the same root.
5. Write headlines and descriptions in user terms — describe what the user experiences, not Trap names or UX jargon.
6. Preserve traps_checked_not_found and positive_observations from the input unchanged.
7. Use measured language throughout: 'appears to', 'may cause', 'could prevent', 'seems likely'."""


def build_synthesis_user_message(pass2_report: Dict[str, Any]) -> str:
    """
    User message for Pass 3: provides the confirmed Trap findings for synthesis.
    """
    sections = []
    sections.append("## Confirmed Trap Findings from Trap Analysis\n")
    sections.append("Group these findings into user-facing issues. Each finding was confirmed by applying the UI Tenets & Traps knowledge base.\n")

    for severity_key, label in [
        ("critical_issues", "CRITICAL"),
        ("moderate_issues", "MODERATE"),
        ("minor_issues", "MINOR"),
    ]:
        findings = pass2_report.get(severity_key, [])
        if not findings:
            continue
        sections.append(f"\n### {label} Findings\n")
        for f in findings:
            sections.append(
                f"- **{f.get('trap_name', '')}** ({f.get('tenet', '')})\n"
                f"  Location: {f.get('location', '')}\n"
                f"  Headline: {f.get('headline', '')}\n"
                f"  Problem: {f.get('problem', '')}\n"
                f"  Recommendation: {f.get('recommendation', '')}\n"
                f"  Confidence: {f.get('confidence', '')}\n"
            )

    pos = pass2_report.get("positive_observations", [])
    if pos:
        sections.append("\n### Positive Observations (pass through unchanged)\n")
        for p in pos:
            sections.append(f"- {p}\n")

    not_found = pass2_report.get("traps_checked_not_found", [])
    if not_found:
        sections.append("\n### Traps Checked Not Found (pass through unchanged)\n")
        for item in not_found:
            if isinstance(item, dict):
                sections.append(f"- {item.get('trap_name', '')} (testable: {item.get('testable', True)})\n")
            else:
                sections.append(f"- {item}\n")

    sections.append("\n---\n")
    sections.append("Synthesise these findings into user-facing issues using the ui_issues_report tool.")

    return "".join(sections)
```

**Step 3: Run tests**

```
cd backend
python -m pytest ../tests/unit/test_user_issues_schema.py -v
```
Expected: All tests PASS

**Step 4: Commit**

```bash
git add backend/src/prompts.py tests/unit/test_user_issues_schema.py
git commit -m "feat: add Pass 3 synthesis prompts for user-issues report mode"
```

---

## Task 3: Add `_synthesize_issues()` to analyzer.py and wire into `analyze_design()`

**Files:**
- Modify: `backend/src/analyzer.py`

**Step 1: Add the import for the new schema and prompts at the top of the try block (around line 28)**

The existing import block already imports from `.prompts` and `.schema`. Add the new names:

In the `try` block (line 26-31), add to the prompts import:
```python
from .prompts import (
    build_system_prompt, build_user_message, build_figma_message,
    INTERACTION_ANALYSIS_SYSTEM_PROMPT, build_interaction_message,
    build_enrichment_system_prompt, build_enrichment_user_message,
    build_synthesis_system_prompt, build_synthesis_user_message,   # NEW
)
```

And to the schema import:
```python
from .schema import get_ui_analysis_schema, get_interaction_analysis_schema, get_user_issues_schema  # NEW
```

Do the same in the `except ImportError` fallback block (lines 33-44).

**Step 2: Add `report_style` parameter to `analyze_design()` signature**

Add to the method signature (after `thorough_mode: bool = False,` around line 94):
```python
report_style: str = "trap",   # "trap" = existing per-Trap layout | "issues" = user-centric grouping
```

**Step 3: Add the `_synthesize_issues()` method**

Add after the `_enrich_report()` method (after line ~780):

```python
def _synthesize_issues(
    self,
    enriched_report: Dict[str, Any],
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    Pass 3: Synthesise enriched per-Trap findings into user-centric issues.

    Groups Traps that share a common design element or root cause into a
    single user-facing issue. Grounds all synthesis in the confirmed Trap
    findings — does not introduce new problems.

    Args:
        enriched_report: Pass 1+2 report (per-Trap findings)
        timeout: API call timeout in seconds

    Returns:
        User-issues report matching USER_ISSUES_SCHEMA.
        Falls back to None on failure (caller uses trap-view report).
    """
    # Check there are confirmed findings to synthesise
    total = sum(
        len(enriched_report.get(k, []))
        for k in ("critical_issues", "moderate_issues", "minor_issues")
    )
    if total == 0:
        return None

    system_prompt = build_synthesis_system_prompt()
    user_message = build_synthesis_user_message(enriched_report)
    schema = get_user_issues_schema()

    print(f"[UITraps] Pass 3: synthesising {total} Trap finding(s) into user issues")

    response = self.client.messages.create(
        model=self.enrich_model,   # Haiku — text only
        max_tokens=4096,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
        tools=[
            {
                "name": "ui_issues_report",
                "description": "Submit the synthesised user-issues report",
                "input_schema": schema
            }
        ],
        tool_choice={"type": "tool", "name": "ui_issues_report"},
        timeout=timeout
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "ui_issues_report":
            issues_report = block.input
            # Pass through the region crops from the source image
            self._crop_issue_regions_for_issues(issues_report, enriched_report)
            return issues_report

    return None


def _crop_issue_regions_for_issues(
    self,
    issues_report: Dict[str, Any],
    enriched_report: Dict[str, Any],
) -> None:
    """
    Attach base64 region crops to issues_report items.

    Reuses the design_file stored on the enriched_report metadata if available,
    otherwise skips cropping silently.
    """
    design_file = enriched_report.get("_design_file")
    if not design_file:
        return
    for issue in issues_report.get("issues", []):
        region = issue.get("region")
        if region:
            try:
                from .formatters import _crop_region_b64
                issue["region"]["_crop_b64"] = _crop_region_b64(design_file, region)
            except Exception:
                pass
```

**Step 4: Store design_file on report for Pass 3 cropping**

In `analyze_design()`, after the `_pass1()` / `_run_tenet_parallel()` call (around line 155), add:
```python
report["_design_file"] = design_file   # used by Pass 3 region cropping
```

**Step 5: Wire Pass 3 into `analyze_design()` after Pass 2**

After the Pass 2 try/except block (around line 171), add:

```python
# Step 8b: Pass 3 — synthesise into user-issues format (only when requested)
issues_report = None
if report_style == "issues":
    try:
        issues_report = self._synthesize_issues(report, timeout=timeout)
    except Exception as e:
        print(f"[UITraps] Pass 3 synthesis skipped (non-fatal): {e}")
```

**Step 6: Thread `issues_report` through the output generation**

Further down in `analyze_design()` (around line 198), the HTML is generated. Replace:
```python
html_report = format_report_as_html(report, user_context, analysis_settings=_analysis_settings)
```
With:
```python
if issues_report is not None:
    html_report = format_issues_report_as_html(issues_report, user_context, analysis_settings=_analysis_settings)
else:
    html_report = format_report_as_html(report, user_context, analysis_settings=_analysis_settings)
```

Also add the import at the top of the try block:
```python
from .formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, format_issues_report_as_html, get_report_statistics
```

**Step 7: Commit**

```bash
git add backend/src/analyzer.py
git commit -m "feat: add Pass 3 _synthesize_issues() and wire report_style into analyze_design()"
```

---

## Task 4: Add `format_issues_report_as_html()` to formatters.py

**Files:**
- Modify: `backend/src/formatters.py` (add new function, reuse existing HTML scaffolding)

**Step 1: Write a failing test**

Add to `tests/unit/test_user_issues_schema.py`:

```python
from formatters import format_issues_report_as_html

def test_format_issues_report_basic():
    mock_issues_report = {
        "summary_headline": "Navigation structure creates competing paths.",
        "summary_narrative": "Two navigation systems appear to present users with duplicate routes.",
        "issues": [
            {
                "headline": "Two separate navigation bars appear to duplicate site-level navigation.",
                "severity": "moderate",
                "confidence": "medium",
                "root_cause_trap": {
                    "trap_name": "GRATUITOUS REDUNDANCY",
                    "tenet": "HABITUATING",
                    "definition": "Multiple instances of interface elements that complete the same action are presented at the same time."
                },
                "contributing_traps": [
                    {
                        "trap_name": "AMBIGUOUS HOME",
                        "tenet": "HABITUATING",
                        "definition": "The interface presents competing locations for getting oriented."
                    }
                ],
                "description": "The page presents two horizontal navigation bars simultaneously.",
                "recommendation": "Consider consolidating into a single navigation system."
            }
        ],
        "positive_observations": ["Clean typography"],
        "traps_checked_not_found": [{"trap_name": "DISTRACTION", "testable": True}]
    }
    mock_context = {"users": "Test users", "tasks": "Test tasks", "format": "Website screenshot"}
    html = format_issues_report_as_html(mock_issues_report, mock_context)
    assert "<html" in html
    assert "GRATUITOUS REDUNDANCY" in html
    assert "AMBIGUOUS HOME" in html
    assert "ROOT CAUSE" in html
    assert "Two separate navigation bars" in html
    assert "Traps Not Found" in html
```

Run: `python -m pytest ../tests/unit/test_user_issues_schema.py::test_format_issues_report_basic -v`
Expected: FAIL with ImportError

**Step 2: Add `format_issues_report_as_html()` to `backend/src/formatters.py`**

Append the function before `get_report_statistics()`. It shares the HTML head/CSS from `format_report_as_html` — extract shared styles into a helper or duplicate the minimal set needed. The function renders:

- Same page header (logo, title, summary)
- Issues cards in new layout (see structure below)
- Same "Traps Not Found" / "Needs More Context" sections (reuse existing logic)
- Same footer

```python
def format_issues_report_as_html(
    issues_report: Dict[str, Any],
    user_context: Dict[str, Any],
    analysis_settings: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Render the user-issues synthesis (Pass 3) as an HTML report.

    Issue card layout per finding:
      FINDING N
      [headline]
      Severity dot + label | Confidence label
      TRAPS
        [ROOT CAUSE bar] TRAP NAME — definition
        [contributing bar] TRAP NAME — definition  (stacked, one per trap)
      DESCRIPTION
        [text]
        [optional region crop]
      RECOMMENDATION
        [text]
    """
    from datetime import datetime
    html = []

    # ── Reuse the same <head> CSS as the main report ──────────────────────────
    # Build an identical page shell — same variables, same layout containers
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head><meta charset='UTF-8'>")
    html.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append("<title>UI Traps Analysis — Issue View</title>")
    html.append("<style>")
    html.append(_ISSUES_REPORT_CSS)
    html.append("</style>")
    html.append("</head><body>")
    html.append("<div class='report-container'>")

    # ── Header ────────────────────────────────────────────────────────────────
    html.append("<div class='report-header'>")
    html.append("<h1>UI Tenets &amp; Traps Analysis</h1>")
    html.append("<p class='report-subtitle'>Issue View</p>")
    html.append(f"<p class='report-date'>{datetime.now().strftime('%B %d, %Y')}</p>")
    html.append("</div>")

    # ── Summary ───────────────────────────────────────────────────────────────
    headline = _cap_terms(issues_report.get("summary_headline", ""))
    narrative = _cap_terms(issues_report.get("summary_narrative", ""))
    html.append("<div class='summary-section'>")
    html.append(f"<h2 class='summary-headline'>{headline}</h2>")
    html.append(f"<p class='summary-narrative'>{narrative}</p>")
    html.append("</div>")

    # ── Issues ────────────────────────────────────────────────────────────────
    issues = issues_report.get("issues", [])
    if issues:
        html.append("<div class='issues-section'>")
        html.append(f"<p class='section-intro'>{len(issues)} issue{'s' if len(issues) != 1 else ''} identified.</p>")
        for idx, issue in enumerate(issues, 1):
            html.append(_render_issue_card_html(idx, issue))
        html.append("</div>")

    # ── Positive observations ─────────────────────────────────────────────────
    pos = issues_report.get("positive_observations", [])
    if pos:
        html.append("<div class='positives-section'>")
        html.append("<h2>What Works Well</h2>")
        html.append("<ul>")
        for p in pos:
            html.append(f"<li>{_cap_terms(p)}</li>")
        html.append("</ul>")
        html.append("</div>")

    # ── Traps not found (reuse existing logic) ────────────────────────────────
    raw_items = issues_report.get('traps_checked_not_found', [])
    tested_ok = []
    untestable = []
    for item in raw_items:
        if isinstance(item, str):
            tested_ok.append(item)
        elif item.get('testable', True):
            tested_ok.append(item['trap_name'])
        else:
            untestable.append(item)

    if tested_ok:
        html.append("<div class='traps-not-found'>")
        html.append("<h2>Traps Not Found</h2>")
        html.append("<p class='section-intro'>The following traps were specifically evaluated and do not appear to be present.</p>")
        html.append("<ul class='trap-name-list'>")
        for trap in tested_ok:
            tenet = _tenet_for(trap)
            html.append(f"<li>{_tenet_pill_html(trap, tenet)}</li>")
        html.append("</ul></div>")

    if untestable:
        html.append("<div class='traps-not-found'>")
        html.append("<h2>Needs More Context</h2>")
        html.append("<p class='section-intro'>The following traps could not be fully evaluated from the submitted materials.</p>")
        html.append("<ul class='trap-name-list'>")
        for item in untestable:
            tenet = _tenet_for(item['trap_name'])
            html.append(f"<li>{_tenet_pill_html(item['trap_name'], tenet)}</li>")
        html.append("</ul></div>")

    # ── Footer ────────────────────────────────────────────────────────────────
    html.append("<div class='footer confidentiality-notice'>")
    html.append("<p><em>Generated using UI Tenets &amp; Traps proprietary framework</em></p>")
    html.append("</div>")
    html.append("</div></body></html>")
    return "\n".join(html)


def _render_issue_card_html(idx: int, issue: Dict[str, Any]) -> str:
    """Render one issue card for the user-issues report."""
    out = []
    severity = issue.get("severity", "moderate")
    confidence = issue.get("confidence", "medium")
    headline = _cap_terms(issue.get("headline", ""))
    description = _cap_terms(issue.get("description", ""))
    recommendation = _cap_terms(issue.get("recommendation", ""))

    sev_color = {"critical": "#c0392b", "moderate": "#e67e22", "minor": "#27ae60"}.get(severity, "#888")

    out.append(f"<div class='issue-card'>")
    out.append(f"<div class='issue-number'>FINDING {idx}</div>")
    out.append(f"<div class='issue-headline'>{headline}</div>")
    out.append(
        f"<div class='issue-meta'>"
        f"<span class='severity-dot' style='background:{sev_color}'></span>"
        f"<span class='severity-label'>{severity.capitalize()}</span>"
        f"<span class='meta-divider'>|</span>"
        f"<span class='confidence-label'>Confidence: {confidence.capitalize()}</span>"
        f"</div>"
    )

    # Traps section
    root = issue.get("root_cause_trap", {})
    contributing = issue.get("contributing_traps", [])
    if root:
        out.append("<div class='issue-traps-section'>")
        out.append("<div class='traps-label'>TRAPS</div>")
        out.append(_render_trap_bar_html(root, is_root=True))
        for trap in contributing:
            out.append(_render_trap_bar_html(trap, is_root=False))
        out.append("</div>")

    # Description
    out.append("<div class='issue-body-section'>")
    out.append("<div class='body-label'>DESCRIPTION</div>")
    out.append(f"<p>{description}</p>")

    # Region crop
    region = issue.get("region", {})
    crop_b64 = region.get("_crop_b64") if region else None
    caption = region.get("caption", "") if region else ""
    if crop_b64:
        out.append(f"<figure class='region-crop'>")
        out.append(f"<img src='{crop_b64}' alt='Design detail'/>")
        if caption:
            out.append(f"<figcaption>{caption}</figcaption>")
        out.append("</figure>")

    out.append("</div>")

    # Recommendation
    out.append("<div class='issue-body-section'>")
    out.append("<div class='body-label'>RECOMMENDATION</div>")
    out.append(f"<p>{recommendation}</p>")
    out.append("</div>")

    out.append("</div>")  # .issue-card
    return "\n".join(out)


def _render_trap_bar_html(trap: Dict[str, Any], is_root: bool) -> str:
    """Render a tenet-colored trap bar for an issue card."""
    trap_name = trap.get("trap_name", "")
    tenet = trap.get("tenet", "")
    definition = trap.get("definition", "")
    color = TENET_COLORS.get(tenet.upper(), "#4a4744")

    root_label = "<span class='root-cause-label'>ROOT CAUSE</span>" if is_root else ""
    return (
        f"<div class='trap-bar' style='border-left: 4px solid {color}'>"
        f"<div class='trap-bar-header'>"
        f"{root_label}"
        f"<span class='trap-bar-name' style='color:{color}'>{trap_name.upper()}</span>"
        f"</div>"
        f"<div class='trap-bar-definition'>{definition}</div>"
        f"</div>"
    )


_ISSUES_REPORT_CSS = """
  /* ── Base reset and typography ───────────────────────────────────────── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         font-size: 15px; line-height: 1.6; color: #1a1a1a; background: #f5f5f5; }
  .report-container { max-width: 860px; margin: 0 auto; padding: 32px 24px; }

  /* ── Header ─────────────────────────────────────────────────────────── */
  .report-header { margin-bottom: 32px; }
  .report-header h1 { font-size: 1.6em; font-weight: 700; color: #111; }
  .report-subtitle { font-size: 0.9em; color: #666; margin-top: 2px; }
  .report-date { font-size: 0.85em; color: #888; margin-top: 4px; }

  /* ── Summary ─────────────────────────────────────────────────────────── */
  .summary-section { background: #fff; border-radius: 10px; padding: 24px; margin-bottom: 28px;
                     box-shadow: 0 1px 4px rgba(0,0,0,.07); }
  .summary-headline { font-size: 1.15em; font-weight: 700; color: #111; margin-bottom: 10px; }
  .summary-narrative { color: #444; line-height: 1.7; }

  /* ── Issues section ──────────────────────────────────────────────────── */
  .issues-section { margin-bottom: 28px; }
  .section-intro { color: #666; font-size: 0.9em; margin-bottom: 16px; }

  /* ── Issue card ──────────────────────────────────────────────────────── */
  .issue-card { background: #fff; border-radius: 10px; padding: 0;
                margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.08);
                overflow: hidden; }
  .issue-number { font-size: 0.72em; font-weight: 700; letter-spacing: .08em;
                  color: #888; padding: 16px 20px 4px; text-transform: uppercase; }
  .issue-headline { font-size: 1.08em; font-weight: 700; color: #111;
                    padding: 0 20px 10px; line-height: 1.4; }
  .issue-meta { display: flex; align-items: center; gap: 8px;
                padding: 0 20px 14px; }
  .severity-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  .severity-label { font-size: 0.88em; font-weight: 600; color: #333; }
  .meta-divider { color: #ccc; font-size: 0.85em; }
  .confidence-label { font-size: 0.85em; color: #666; }

  /* ── Traps block ─────────────────────────────────────────────────────── */
  .issue-traps-section { border-top: 1px solid #f0f0f0; padding: 14px 20px; }
  .traps-label { font-size: 0.72em; font-weight: 700; letter-spacing: .08em;
                 color: #888; text-transform: uppercase; margin-bottom: 10px; }
  .trap-bar { padding: 10px 14px; margin-bottom: 8px; border-radius: 4px;
              background: #fafafa; border-left-width: 4px; border-left-style: solid; }
  .trap-bar:last-child { margin-bottom: 0; }
  .trap-bar-header { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
  .root-cause-label { font-size: 0.68em; font-weight: 700; letter-spacing: .06em;
                      text-transform: uppercase; color: #fff;
                      background: #333; border-radius: 3px; padding: 2px 6px; }
  .trap-bar-name { font-size: 0.85em; font-weight: 700; letter-spacing: .04em; }
  .trap-bar-definition { font-size: 0.83em; color: #555; line-height: 1.5; }

  /* ── Description / Recommendation ───────────────────────────────────── */
  .issue-body-section { border-top: 1px solid #f0f0f0; padding: 14px 20px; }
  .body-label { font-size: 0.72em; font-weight: 700; letter-spacing: .08em;
                color: #888; text-transform: uppercase; margin-bottom: 8px; }
  .issue-body-section p { color: #333; line-height: 1.7; }

  /* ── Region crop ─────────────────────────────────────────────────────── */
  .region-crop { margin: 12px 0 4px; }
  .region-crop img { max-width: 380px; border-radius: 6px;
                     border: 1px solid #e0e0e0; display: block; }
  .region-crop figcaption { font-size: 0.8em; color: #777;
                             font-style: italic; margin-top: 6px; }

  /* ── Positives ───────────────────────────────────────────────────────── */
  .positives-section { background: #fff; border-radius: 10px; padding: 20px;
                       margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.07); }
  .positives-section h2 { font-size: 1em; font-weight: 700; margin-bottom: 10px; }
  .positives-section li { color: #444; margin-bottom: 4px; }

  /* ── Traps not found ─────────────────────────────────────────────────── */
  .traps-not-found { background: #fff; border-radius: 10px; padding: 20px;
                     margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.07); }
  .traps-not-found h2 { font-size: 1em; font-weight: 700; margin-bottom: 6px; }
  .trap-name-list { list-style: none; display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
  .tenet-pill { display: inline-block; color: #fff; font-size: 0.78em; font-weight: 700;
                letter-spacing: .04em; padding: 4px 10px; border-radius: 4px; }

  /* ── Footer ──────────────────────────────────────────────────────────── */
  .footer { border-top: 1px solid #e0e0e0; padding-top: 16px; margin-top: 28px;
            font-size: 0.82em; color: #888; }
"""
```

**Step 3: Run tests**

```
cd backend
python -m pytest ../tests/unit/test_user_issues_schema.py -v
```
Expected: All tests PASS

**Step 4: Commit**

```bash
git add backend/src/formatters.py
git commit -m "feat: add format_issues_report_as_html() for user-issues report layout"
```

---

## Task 5: Add `report_style` parameter to the backend API endpoints

**Files:**
- Modify: `backend/app.py` — two endpoints: `/api/analyze` and `/api/ask`

**Step 1: Find the two endpoint Form parameter blocks**

Search for `kb_version: str = Form("v2")` — it appears at approximately lines 1909 and 2265. Add `report_style` alongside it in both places:

```python
report_style: str = Form("trap"),   # "trap" | "issues"
```

**Step 2: Pass `report_style` through to `analyze_design()` calls**

Every call to `analyzer.analyze_design(...)` should include:
```python
report_style=report_style,
```

There are approximately 4 call sites in the file. Search for `analyze_design(` and add the parameter to each.

**Step 3: Manual smoke test** (no automated test for API wiring)

Start the backend: `cd backend && python app.py`

Send a request with `report_style=issues` using curl or the frontend (after Task 6). Verify the response `html` field contains `class='issue-card'` instead of the existing trap card structure.

**Step 4: Commit**

```bash
git add backend/app.py
git commit -m "feat: add report_style parameter to /api/analyze and /api/ask endpoints"
```

---

## Task 6: Add `report_style` to frontend types and the AnalyzerForm toggle

**Files:**
- Modify: `frontend/src/api/types.ts`
- Modify: `frontend/src/components/AnalyzerForm.tsx`
- Modify: `frontend/src/api/client.ts` (wherever `UserContext` fields are serialised into FormData)

**Step 1: Add type to `types.ts`**

In `UserContext` interface (around line 112), add after `thorough_mode`:
```typescript
report_style?: 'trap' | 'issues';
```

**Step 2: Add state and toggle to `AnalyzerForm.tsx`**

In the form state (look for where `thoroughMode`, `verbosity`, etc. are declared), add:
```typescript
const [reportStyle, setReportStyle] = useState<'trap' | 'issues'>('trap');
```

In `assembleContext()` (or wherever `UserContext` is assembled), add:
```typescript
report_style: reportStyle,
```

In the JSX, add a toggle in the options section (alongside the existing Thorough Mode / KB Version toggles):

```tsx
{/* Report Style toggle */}
<div className={styles.optionRow}>
  <label className={styles.optionLabel}>Report Style</label>
  <div className={styles.toggleGroup}>
    <button
      type="button"
      className={`${styles.toggleBtn} ${reportStyle === 'trap' ? styles.active : ''}`}
      onClick={() => setReportStyle('trap')}
    >
      By Trap
    </button>
    <button
      type="button"
      className={`${styles.toggleBtn} ${reportStyle === 'issues' ? styles.active : ''}`}
      onClick={() => setReportStyle('issues')}
    >
      By Issue
    </button>
  </div>
</div>
```

**Step 3: Serialise in `client.ts`**

Find where `UserContext` fields are appended to `FormData` (search for `formData.append`). Add:
```typescript
if (context.report_style) formData.append('report_style', context.report_style);
```

**Step 4: Start dev servers and manually test**

```
# Terminal 1
cd backend && python app.py

# Terminal 2
cd frontend && npm run dev
```

Open http://localhost:5173, upload a design, select "By Issue" in Report Style, run analysis. Verify the report renders issue cards with FINDING N headers, trap bars, ROOT CAUSE labels, and no trap card artwork.

**Step 5: Commit**

```bash
git add frontend/src/api/types.ts frontend/src/components/AnalyzerForm.tsx frontend/src/api/client.ts
git commit -m "feat: add By Issue / By Trap toggle to AnalyzerForm and wire report_style to API"
```

---

## Task 7: End-to-end verification

**Manual test checklist:**

1. Run analysis in **By Trap** mode — verify existing report is completely unchanged.
2. Run analysis in **By Issue** mode on a design known to have multiple confirmed findings:
   - [ ] FINDING N headers appear
   - [ ] Each finding has Severity dot + label and Confidence label
   - [ ] TRAPS section shows at least one trap bar
   - [ ] Root cause trap has ROOT CAUSE badge and appears first
   - [ ] Contributing traps (if any) are stacked below without ROOT CAUSE badge
   - [ ] DESCRIPTION and RECOMMENDATION sections appear
   - [ ] Region crop appears when a region was provided
   - [ ] "Traps Not Found" section appears at the bottom
   - [ ] No trap card artwork (no base64 PNG images of cards)
3. Run analysis in **By Issue** mode on a design with zero confirmed findings — verify report renders gracefully (no issues section, just summary and not-found).
4. Verify the By Trap toggle immediately switches back to the existing report format.

**Step: Commit any fixes found during verification**

```bash
git add -p   # stage only the fixes
git commit -m "fix: [describe what broke during verification]"
```

---

## Notes for implementer

- `_crop_region_b64` is an existing helper in `formatters.py` — verify its signature before calling it in `_crop_issue_regions_for_issues()`. It may need the original image file path.
- The `tests/unit/` directory does not yet exist — create it with an empty `__init__.py`.
- `build_synthesis_user_message` uses `Dict` from `typing` — confirm the import is present at the top of `prompts.py`.
- If the region crop helper is not easily extracted from the existing formatter, it is acceptable to omit Pass 3 region crops in the first implementation and add them as a follow-up.
