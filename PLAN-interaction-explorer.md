# Implementation Plan: Moment-by-Moment UI Interaction Analysis

## Executive Summary

Your current analyzer takes **static screenshots** and misses crucial interaction patterns that humans naturally observe: hover states, click feedback, form validation, loading transitions, and responsive behavior. The advice you received recommends a **tiered approach** that builds on your existing Playwright infrastructure.

This plan implements **Approach 1** (Playwright Interaction Explorer) as the foundation, with optional **Approach 2** (Gemini video analysis) as an enhancement. Approach 3 (Claude Computer Use) is deferred for a premium tier.

---

## Current Architecture (What You Have)

```
URL → WebCrawler (static screenshots) → SiteAnalyzer → UITrapsAnalyzer (Claude Vision) → Report
```

**Key files:**
- `web_crawler.py` - Playwright crawling with static `page.screenshot()`
- `site_analyzer.py` - Multi-page orchestration with page role classification
- `analyzer.py` - Claude API calls with tool-forced structured output
- `prompts.py` - Already has `VIDEO_ANALYSIS_GUIDANCE` for multi-frame analysis
- `schema.py` - Already has `frame_quality_notes` and `bugs_detected` fields

**Good news:** Your existing infrastructure supports multi-image analysis. We're extending it, not replacing it.

---

## Target Architecture

```
URL → WebCrawler
         ↓
    InteractionExplorer  ←── NEW: captures hover/click/scroll/form/responsive
         ↓
    Screenshot Sequences (labeled: before_hover, during_hover, etc.)
         ↓
    SiteAnalyzer (enhanced)
         ↓
    UITrapsAnalyzer (multi-image prompts per interaction)
         ↓
    Report (with new "Interaction Analysis" section)
```

---

## Phase 1: InteractionExplorer Module (Week 1-2)

### 1.1 Create `backend/src/interaction_explorer.py`

A new module that systematically captures UI states during interactions.

**Interaction types to capture:**

| Type | What It Captures | Screenshots | Traps It Detects |
|------|------------------|-------------|------------------|
| Hover sweep | Hover states on interactive elements | 2 per element (before + during) | FEEDBACK FAILURE, INVISIBLE ELEMENT |
| Click feedback | Click response and state changes | 3 per element (before + immediate + settled) | FEEDBACK FAILURE, ACCIDENTAL ACTIVATION |
| Form validation | Validation messages on invalid input | 3 per form (empty + filled + errors) | DATA LOSS, UNCOMPREHENDED ELEMENT |
| Scroll behavior | Sticky headers, parallax, content reveal | 4-5 per page (0%, 25%, 50%, 75%, 100%) | WANDERING ELEMENT |
| Responsive | Layout at mobile/tablet/desktop | 3 per page (375px, 768px, 1440px) | PHYSICAL CHALLENGE |

**Key classes:**

```python
@dataclass
class InteractionCapture:
    element_description: str
    interaction_type: str  # "hover", "click", "form", "scroll", "responsive"
    screenshots: list[bytes]  # ordered sequence
    labels: list[str]         # "before_hover", "during_hover", etc.
    dom_changes: Optional[str] = None
    video_path: Optional[str] = None

class InteractionExplorer:
    def __init__(self, page: Page): ...
    async def explore_hover_states(self, max_elements: int = 20) -> None
    async def explore_click_feedback(self, max_elements: int = 10) -> None
    async def explore_form_validation(self) -> None
    async def explore_scroll_behavior(self) -> None
    async def explore_responsive_behavior(self) -> None
    async def run_full_exploration(self) -> list[InteractionCapture]
```

### 1.2 Integrate with WebCrawler

Modify `web_crawler.py` to optionally run interaction exploration:

```python
class WebCrawler:
    def __init__(
        self,
        # ... existing params ...
        enable_interaction_capture: bool = False,  # NEW
        interaction_config: Optional[dict] = None   # NEW
    ):
```

### 1.3 Files to create/modify:

| File | Action | Description |
|------|--------|-------------|
| `backend/src/interaction_explorer.py` | CREATE | Core interaction capture logic |
| `backend/src/web_crawler.py` | MODIFY | Add `enable_interaction_capture` flag |
| `backend/src/site_analyzer.py` | MODIFY | Handle interaction sequences |

---

## Phase 2: Multi-Image Claude Analysis (Week 2-3)

### 2.1 Update `prompts.py`

Add new prompt template for interaction sequence analysis:

```python
INTERACTION_ANALYSIS_PROMPT = """You are analyzing a UI interaction sequence.

You are given {n_images} screenshots captured during a {interaction_type} interaction
with the element: {element_description}

The screenshots are labeled: {labels}

Analyze this interaction for usability issues including:
- Is there adequate visual feedback for the interaction?
- Are state transitions clear and perceivable?
- Is the response time acceptable?
- Are hover/focus states visually distinct and accessible?
- Do animations/transitions aid comprehension?
- Is the resulting state change predictable?

Identify any UI Traps present in this interaction sequence.
Return your findings using the interaction_analysis_report tool."""
```

### 2.2 Update `schema.py`

Add new schema for interaction-specific findings:

```python
INTERACTION_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "interaction_type": {"type": "string"},
        "element_analyzed": {"type": "string"},
        "feedback_quality": {
            "type": "object",
            "properties": {
                "has_visual_feedback": {"type": "boolean"},
                "feedback_timing": {"type": "string", "enum": ["immediate", "delayed", "none"]},
                "feedback_clarity": {"type": "string", "enum": ["clear", "subtle", "confusing", "none"]}
            }
        },
        "state_transition": {
            "type": "object",
            "properties": {
                "is_predictable": {"type": "boolean"},
                "is_reversible": {"type": "boolean"},
                "maintains_context": {"type": "boolean"}
            }
        },
        "traps_detected": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {"type": "string"},
                    "severity": {"type": "string", "enum": ["critical", "moderate", "minor"]},
                    "observation": {"type": "string"},
                    "recommendation": {"type": "string"}
                }
            }
        },
        "accessibility_concerns": {"type": "array", "items": {"type": "string"}}
    }
}
```

### 2.3 Update `analyzer.py`

Add method for multi-image interaction analysis:

```python
def analyze_interaction_sequence(
    self,
    images: list[dict],  # Multiple base64 images
    labels: list[str],
    element_description: str,
    interaction_type: str,
    user_context: dict
) -> dict:
```

### 2.4 Files to create/modify:

| File | Action | Description |
|------|--------|-------------|
| `backend/src/prompts.py` | MODIFY | Add `INTERACTION_ANALYSIS_PROMPT` |
| `backend/src/schema.py` | MODIFY | Add `INTERACTION_ANALYSIS_SCHEMA` |
| `backend/src/analyzer.py` | MODIFY | Add `analyze_interaction_sequence()` |
| `backend/src/formatters.py` | MODIFY | Format interaction findings in reports |

---

## Phase 3: Report Enhancement (Week 3)

### 3.1 Update Report Structure

Add new "Interaction Analysis" section to reports:

```
## Interaction Analysis

### Hover States
- Button "Submit" shows subtle color change (MINOR: consider more prominent feedback)
- Navigation links have clear hover states ✓

### Click Feedback
- Form submit shows loading spinner immediately ✓
- "Add to Cart" lacks immediate feedback (MODERATE: FEEDBACK FAILURE)

### Form Validation
- Inline validation on email field ✓
- Password requirements only shown on error (MINOR: show proactively)

### Responsive Behavior
- Navigation collapses to hamburger at mobile ✓
- Text becomes cramped at 375px (MODERATE: PHYSICAL CHALLENGE)
```

### 3.2 Files to modify:

| File | Action | Description |
|------|--------|-------------|
| `backend/src/formatters.py` | MODIFY | Add interaction section to markdown/HTML |
| `frontend/src/components/ReportViewer.tsx` | MODIFY | Display interaction analysis |

---

## Phase 4: Gemini Video Analysis (Week 3-4, Optional)

### 4.1 Create `backend/src/animation_analyzer.py`

For capturing and analyzing animations/transitions that screenshot sequences miss:

```python
import google.generativeai as genai

class AnimationAnalyzer:
    def __init__(self, google_api_key: Optional[str] = None):
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    async def analyze_animation_quality(
        self,
        video_path: str,
        context: str
    ) -> dict:
        """Analyze recorded interaction video for animation quality."""
```

### 4.2 Integration with Playwright video recording

```python
# In interaction_explorer.py
async def capture_with_video(self, interaction_fn):
    """Record video during interaction for animation analysis."""
    context = await browser.new_context(record_video_dir="/tmp/videos/")
    # ... perform interaction ...
    video_path = await page.video.path()
    return video_path
```

### 4.3 Files to create:

| File | Action | Description |
|------|--------|-------------|
| `backend/src/animation_analyzer.py` | CREATE | Gemini video analysis |
| `backend/requirements.txt` | MODIFY | Add `google-generativeai` |

---

## API Endpoint Changes

### New/Modified Endpoints

```python
# Modify existing /analyze-url endpoint
@app.post("/analyze-url")
async def analyze_url(request: UrlAnalysisRequest):
    # Add optional parameter
    enable_interaction_analysis: bool = True  # Default ON

# New endpoint for interaction-only analysis (useful for re-analysis)
@app.post("/analyze-interactions")
async def analyze_interactions(request: InteractionAnalysisRequest):
    """Run interaction analysis on a previously crawled page."""
```

---

## Cost Estimates (Per Page)

| Analysis Type | Claude API Calls | Estimated Cost |
|---------------|------------------|----------------|
| Current (static only) | 1 | $0.01-0.03 |
| With hover capture (20 elements) | +10 | +$0.10-0.30 |
| With click feedback (10 elements) | +10 | +$0.10-0.30 |
| With form validation (3 forms) | +3 | +$0.03-0.09 |
| With scroll/responsive | +2 | +$0.02-0.06 |
| **Total per page** | ~25 | **$0.26-0.78** |
| With Gemini video | +1 | +$0.01-0.05 |

**For a 5-page site: ~$1.30-$4.00** (up from $0.05-0.15 currently)

---

## Implementation Checklist

### Week 1-2: Core Interaction Capture
- [ ] Create `interaction_explorer.py` with all capture methods
- [ ] Unit tests for interaction capture
- [ ] Integrate with `web_crawler.py` via flag
- [ ] Test on sample sites

### Week 2-3: Claude Multi-Image Analysis
- [ ] Add interaction prompt to `prompts.py`
- [ ] Add interaction schema to `schema.py`
- [ ] Implement `analyze_interaction_sequence()` in `analyzer.py`
- [ ] Update `site_analyzer.py` to orchestrate interaction analysis
- [ ] Integration tests

### Week 3: Report Updates
- [ ] Add interaction section to `formatters.py`
- [ ] Update `ReportViewer.tsx` frontend component
- [ ] Update estimate preview to show interaction analysis scope

### Week 3-4: Gemini Video (Optional)
- [ ] Create `animation_analyzer.py`
- [ ] Add Playwright video recording to interaction capture
- [ ] Integrate Gemini findings with Claude analysis
- [ ] Add `GOOGLE_AI_API_KEY` to environment config

---

## Configuration

Add to `.env`:

```bash
# Interaction analysis (optional - all default to true)
ENABLE_HOVER_CAPTURE=true
ENABLE_CLICK_CAPTURE=true
ENABLE_FORM_CAPTURE=true
ENABLE_SCROLL_CAPTURE=true
ENABLE_RESPONSIVE_CAPTURE=true

# Limits (to control cost/time)
MAX_HOVER_ELEMENTS=20
MAX_CLICK_ELEMENTS=10
MAX_FORMS=3

# Gemini (optional - for animation analysis)
GOOGLE_AI_API_KEY=your-key-here
ENABLE_ANIMATION_ANALYSIS=false
```

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Analysis time increases significantly | Make interaction capture async, run in parallel where possible |
| Cost per analysis increases 10-20x | Offer as optional "Deep Analysis" tier, or limit to first N elements |
| Click interactions cause navigation | Check URL after click, use `page.go_back()` if navigated |
| Some sites block automated interactions | Add configurable interaction delays, respect rate limits |
| Hover states not visible in headless mode | Use `headless: false` option or force hover via JS injection |

---

## Future: Claude Computer Use (Premium Tier)

When you're ready to offer a premium "AI UX Evaluator" tier:

1. Set up Docker container with virtual desktop
2. Deploy Claude Computer Use to explore autonomously
3. Charge per-analysis ($10-25) or high monthly fee ($199+)
4. This provides the "closest to human" evaluation

---

## Summary

**Start with Phase 1-2.** This gives you 80% of the value at 20% of the cost of a full autonomous agent. Your existing Playwright + Claude infrastructure makes this a natural extension.

**Key insight from the advice:** You don't need an autonomous agent for most cases. Systematic, scripted interaction patterns capture what humans observe during moment-by-moment use.
