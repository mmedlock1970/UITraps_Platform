# UI Traps Analyzer - Cost-Effective Testing Strategy

## Overview
3-tier testing pyramid prioritizing FREE validation to catch bugs early without burning API credits.

**Goal**: Catch 80%+ of bugs with $0 in API costs, reserve expensive tests for critical validation.

---

## TIER 1: FREE TESTS (0 API calls, <5 sec runtime)

### What It Tests
Validates **output structure** without calling Claude API:
- ✅ Schema compliance (all required fields present)
- ✅ No hallucinated trap names (only 27 valid trap names allowed)
- ✅ No hallucinated tenet names (only 9 valid tenet names allowed)
- ✅ Data types correct (summary is array, not string)
- ✅ Confidence values valid ("high"/"medium"/"low" only)
- ✅ Issue objects have all required fields
- ✅ Summary has 5-9 bullet points (per schema)
- ✅ No crashes on edge cases (empty input, malformed responses)

### How It Works
Uses **mocked Anthropic client** to return controlled responses:
```python
# Mock the API response
mock_response = Mock()
mock_response.content = [
    Mock(type="tool_use", input={
        "summary": ["Test finding 1", "Test finding 2"],
        "critical_issues": [{"trap_name": "INVISIBLE ELEMENT", ...}],
        # ... rest of schema
    })
]
mock_client.messages.create.return_value = mock_response
```

Then run analyzer and validate the output structure.

### Cost
**$0.00 per run** ✅

### Coverage
**80-85%** of bugs (structural issues, hallucinations, type errors)

### Run Command
```bash
cd backend
pytest tests/test_analyzer_free.py -v
```

---

## TIER 2: CACHED REGRESSION TESTS (one-time $0.40 setup)

### What It Tests
Validates that **code changes don't break existing behavior**:
- ✅ Output structure matches baseline (field names, nesting)
- ✅ Severity distribution reasonable (not all critical)
- ✅ No new hallucinations introduced
- ✅ Response parsing still works

### How It Works
**One-time setup** (run once, cache forever):
1. Run analyzer on 5-8 diverse test images
2. Save raw API responses as JSON fixtures
3. Store in `tests/fixtures/cached_analyses/`

**Every test run** (free):
1. Load cached responses from disk
2. Feed to analyzer's parsing logic
3. Validate structure matches expectations
4. Compare against baseline stats

### Fixture Types Needed
```
tests/fixtures/
├── images/                    # Test images for fixture generation
│   ├── simple_form.png       # Basic form (few traps)
│   ├── complex_dashboard.png # Dense UI (many traps)
│   ├── mobile_screen.png     # Mobile design
│   ├── error_state.png       # Edge case: error screen
│   └── minimal_ui.png        # Edge case: very simple UI
└── cached_analyses/          # Generated fixtures (JSON)
    ├── simple_form_analysis.json
    ├── complex_dashboard_analysis.json
    └── ...
```

### One-Time Setup Cost
- 5-8 images × $0.05/analysis = **$0.25-0.40**
- Run once, use forever ♻️

### Ongoing Cost
**$0.00 per run** (uses cached fixtures) ✅

### Coverage
**10-15%** (regression detection, parsing validation)

### Run Command
```bash
# One-time fixture generation (costs money)
python tests/generate_fixtures.py

# Every test run (free)
pytest tests/test_analyzer_cached.py -v
```

### When to Regenerate Fixtures
Only regenerate if you change:
- System prompt (prompts.py)
- Schema structure (schema.py)
- Claude model version

---

## TIER 3: MINIMAL REAL API TESTS (<$0.25 per cycle)

### What It Tests
**Smoke tests** to verify analyzer still works end-to-end:
- ✅ Can analyze a real screenshot
- ✅ Returns valid JSON structure
- ✅ API credentials work
- ✅ Doesn't crash

### How It Works
Run analyzer on 3-5 critical test cases with **real API calls**:
```python
@pytest.mark.real_api  # Mark as expensive
def test_real_api_simple_form():
    result = analyzer.analyze_design("tests/fixtures/images/simple_form.png", ...)
    assert result["status"] == "success"
    # ... validate output
```

### Cost
- 3-5 images × $0.05/analysis = **$0.15-0.25 per validation cycle**

### Coverage
**5-10%** (end-to-end validation, API integration)

### When to Run
- Before major releases
- After prompt/schema changes
- After Claude model upgrades
- **NOT on every commit** (too expensive)

### Run Command
```bash
# Skip by default (marked with @pytest.mark.real_api)
pytest tests/ -v

# Explicitly run expensive tests when needed
pytest tests/test_analyzer_real_api.py -v -m real_api
```

---

## Cost Summary

| Tier | Setup Cost | Per-Run Cost | Runtime | Coverage | When to Run |
|------|------------|--------------|---------|----------|-------------|
| **Tier 1 (Free)** | $0.00 | $0.00 | <5 sec | 80-85% | Every commit, PR, local dev |
| **Tier 2 (Cached)** | $0.25-0.40 | $0.00 | <10 sec | 10-15% | Every commit, PR, local dev |
| **Tier 3 (Real API)** | N/A | $0.15-0.25 | 30-60 sec | 5-10% | Before releases, major changes |

**Total initial setup**: $0.25-0.40 (one-time)
**Typical dev workflow cost**: $0.00 per test run ✅
**Pre-release validation**: $0.15-0.25 per cycle

---

## Testing Workflow

### Local Development (every save)
```bash
pytest tests/test_analyzer_free.py -v  # <5 sec, $0
```

### Before Committing
```bash
pytest tests/ -v  # Runs Tier 1 + Tier 2, ~10 sec, $0
```

### Before Release / Major Changes
```bash
pytest tests/ -v -m real_api  # Runs all tiers, ~60 sec, ~$0.20
```

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
on: [push, pull_request]
jobs:
  test:
    - name: Run free tests (Tier 1 + 2)
      run: pytest tests/ -v --ignore=tests/test_analyzer_real_api.py

  # Optional: Run real API tests on main branch only
  test_real_api:
    if: github.ref == 'refs/heads/main'
    - name: Run real API tests (Tier 3)
      run: pytest tests/test_analyzer_real_api.py -v -m real_api
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Anti-Patterns We're Avoiding

❌ **DON'T**: Build "accuracy evaluation" (requires human ground truth, too expensive)
❌ **DON'T**: Compare exact AI outputs (non-deterministic, flaky tests)
❌ **DON'T**: Test "did it find the RIGHT traps" (subjective, requires expert review)
❌ **DON'T**: Call API on every test (expensive, slow, rate limits)

✅ **DO**: Test output structure validity
✅ **DO**: Test no hallucinated trap/tenet names
✅ **DO**: Test parsing and error handling
✅ **DO**: Use mocks and cached fixtures

---

## Success Metrics

**Good test suite should**:
1. Catch bugs in <5 seconds locally (Tier 1)
2. Cost $0 for 95%+ of test runs (Tier 1 + 2)
3. Prevent deployment of broken analyzers (all tiers)
4. Run in CI/CD without burning budget (Tier 1 + 2 only)

**We're optimizing for**:
- ⚡ Speed (fast feedback loop)
- 💰 Cost (minimize API spend)
- 🎯 Signal (catch real bugs, not flaky failures)
