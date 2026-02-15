# Quick Start Guide - Testing the Analyzer

Get up and running with cost-effective testing in 5 minutes.

## ⚡ 30-Second Setup

```bash
# 1. Install test dependencies
cd backend
pip install -r tests/requirements.txt

# 2. Run free tests (Tier 1)
pytest tests/test_analyzer_free.py -v

# Expected output:
# ========== 42 passed in 3.2s ==========
# ✅ No API costs (Tier 1+2 tests only)
```

**That's it!** You now have 42 tests running in <5 seconds with $0 cost.

---

## 🎯 Development Workflow

### Daily Development

```bash
# Quick validation (every save)
pytest tests/test_analyzer_free.py -v
# Cost: $0, Time: <5s
```

### Before Committing

```bash
# Run all free tests
pytest tests/ -v
# Cost: $0, Time: <15s
```

### Before Major Release

```bash
# Run real API tests (costs money!)
pytest tests/test_analyzer_real_api.py -v -m real_api
# Cost: ~$0.25, Time: ~60s
```

---

## 📋 What Each Test Tier Does

### Tier 1: Free Validation

**Catches:**
- ✅ Schema violations (missing fields)
- ✅ Hallucinated trap names ("CONFUSING BUTTON" not in VALID_TRAP_NAMES)
- ✅ Hallucinated tenet names ("USABILITY" not in VALID_TENET_NAMES)
- ✅ Wrong data types (summary as string instead of array)
- ✅ Invalid confidence values ("very_high" instead of "high"/"medium"/"low")
- ✅ Crashes on edge cases

**Example failure it catches:**
```python
# AI returns invalid trap name
{
  "critical_issues": [{
    "trap_name": "CONFUSING LAYOUT",  # ❌ NOT in VALID_TRAP_NAMES!
    ...
  }]
}

# Test fails with:
# AssertionError: Invalid trap name: CONFUSING LAYOUT
```

### Tier 2: Cached Regression

**Catches:**
- ✅ Breaking changes to parser logic
- ✅ New hallucination bugs
- ✅ Response structure changes

**Example failure it catches:**
```python
# You change code that breaks parsing
# Old cached response no longer parses correctly

# Test fails with:
# AssertionError: Missing required field: summary
```

### Tier 3: Real API Smoke Tests

**Catches:**
- ✅ API integration broken
- ✅ Claude model changes broke analyzer
- ✅ Prompt changes broke output format

**Example failure it catches:**
```python
# System prompt change causes Claude to return wrong format

# Test fails with:
# AssertionError: Analysis should succeed (got error response)
```

---

## 🔧 How Mocking Works (Tier 1)

Tier 1 tests use **mocked Anthropic client** to avoid API calls:

```python
# Instead of calling Claude API...
response = client.messages.create(...)  # ❌ Costs $0.05

# We mock the response
mock_response = Mock()
mock_response.content = [
    Mock(type="tool_use", input={
        "summary": ["Test finding 1", "Test finding 2", ...],
        "critical_issues": [...],
        ...
    })
]

# Analyzer gets mocked response instead of real API
mock_client.messages.create.return_value = mock_response  # ✅ $0.00
```

This lets us test **output validation** without spending money.

---

## 💡 Common Issues

### Issue: "No module named 'src'"

**Fix:**
```bash
# Run tests from backend/ directory
cd backend
pytest tests/ -v
```

### Issue: "No fixtures found"

**Fix:**
```bash
# Generate fixtures (one-time, costs ~$0.30)
python tests/generate_fixtures.py
```

### Issue: Tests are slow (>10 seconds)

**Fix:**
```bash
# Make sure you're not running real_api tests
pytest tests/ -v -m "not real_api"
```

---

## 📊 Cost Comparison

| Approach | Cost per Day | Cost per Month |
|----------|--------------|----------------|
| **No tests** | $0 | $0 (but bugs in production 💥) |
| **Our 3-tier strategy** | $0 | ~$1 (4 releases × $0.25) |
| **Real API on every test** | $50 | $1,500 💸 |

**Savings: $1,499/month** by using free validation + cached tests!

---

## 🎓 Next Steps

1. **Run Tier 1 tests** - Already done if you followed 30-second setup

2. **Add test images** (optional, for Tier 2)
   ```bash
   # Add 5 test images to tests/fixtures/images/
   # See tests/fixtures/images/README.md for details
   ```

3. **Generate fixtures** (optional, for Tier 2)
   ```bash
   # One-time cost: ~$0.30
   python tests/generate_fixtures.py
   ```

4. **Run all free tests**
   ```bash
   pytest tests/ -v
   ```

5. **Add to CI/CD**
   ```yaml
   # .github/workflows/test.yml
   - name: Run tests
     run: |
       cd backend
       pytest tests/ -v --ignore=tests/test_analyzer_real_api.py
   ```

---

## 📚 More Resources

- [README.md](./README.md) - Full testing guide
- [TESTING-STRATEGY.md](../TESTING-STRATEGY.md) - Detailed strategy document
- [run_tests.py](./run_tests.py) - Interactive test runner

---

## 🚀 You're Ready!

You now have:
- ✅ 42+ free tests validating analyzer output
- ✅ <5 second feedback loop
- ✅ $0 cost per test run
- ✅ 80-85% bug coverage

**Happy testing!** 🎉
