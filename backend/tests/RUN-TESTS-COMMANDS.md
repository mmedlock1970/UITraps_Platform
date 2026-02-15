# Quick Command Reference - Run Tests

## Option 1: Copy-Paste All at Once (Windows CMD)

Open Command Prompt and paste this entire block:

```cmd
cd C:\Users\mmed\OneDrive\Desktop\UITraps-Platform\backend
pip install -r tests/requirements.txt
pytest tests/test_analyzer_free.py -v
```

## Option 2: Copy-Paste All at Once (VS Code Terminal)

Open VS Code terminal (Ctrl + `) and paste:

```bash
cd backend
pip install -r tests/requirements.txt
pytest tests/test_analyzer_free.py -v
```

## Option 3: Step-by-Step (if copy-paste doesn't work)

### Step 1: Navigate to backend directory
```bash
cd C:\Users\mmed\OneDrive\Desktop\UITraps-Platform\backend
```

### Step 2: Install dependencies
```bash
pip install -r tests/requirements.txt
```

Wait for installation to complete (20-30 seconds)

### Step 3: Run tests
```bash
pytest tests/test_analyzer_free.py -v
```

---

## Expected Output

### After Step 2 (pip install):
```
Collecting pytest>=7.4.0
  Downloading pytest-7.4.3-py3-none-any.whl (325 kB)
Collecting pytest-cov>=4.1.0
  Downloading pytest_cov-4.1.0-py3-none-any.whl (21 kB)
...
Successfully installed pytest-7.4.3 pytest-cov-4.1.0 pytest-mock-3.11.1
```

### After Step 3 (pytest):
```
================================ test session starts =================================
platform win32 -- Python 3.14.0, pytest-7.4.3, pluggy-1.3.0
cachedir: .pytest_cache
rootdir: C:\Users\mmed\OneDrive\Desktop\UITraps-Platform\backend
configfile: pytest.ini
testpaths: tests
collected 42 items

tests/test_analyzer_free.py::test_valid_response_passes_validation PASSED    [ 2%]
tests/test_analyzer_free.py::test_summary_must_be_array PASSED               [ 4%]
tests/test_analyzer_free.py::test_summary_length_validation PASSED           [ 7%]
tests/test_analyzer_free.py::test_rejects_hallucinated_trap_names PASSED     [ 9%]
tests/test_analyzer_free.py::test_rejects_hallucinated_tenet_names PASSED    [11%]
tests/test_analyzer_free.py::test_all_valid_trap_names_are_accepted PASSED   [14%]
...
tests/test_analyzer_free.py::test_cost_estimation_is_reasonable PASSED       [100%]

================================ 42 passed in 3.21s ==================================
========================== Test Run Summary ==========================
Passed: 42
Failed: 0
Skipped: 0
========================== Cost ==========================
✅ No API costs (Tier 1+2 tests only)
```

---

## Troubleshooting

### Issue: "pip is not recognized"

**Solution**:
```bash
# Use python -m pip instead
python -m pip install -r tests/requirements.txt
```

### Issue: "pytest: command not found"

**Solution**:
```bash
# Use python -m pytest instead
python -m pytest tests/test_analyzer_free.py -v
```

### Issue: "No module named 'src'"

**Solution**: Make sure you're in the `backend` directory:
```bash
# Check where you are
pwd  # Mac/Linux
cd   # Windows

# Should show: .../UITraps-Platform/backend
# If not, navigate there:
cd C:\Users\mmed\OneDrive\Desktop\UITraps-Platform\backend
```

### Issue: Tests fail with import errors

**Solution**: Make sure you're running from backend directory:
```bash
# Always run from here:
cd C:\Users\mmed\OneDrive\Desktop\UITraps-Platform\backend

# Then run tests
pytest tests/test_analyzer_free.py -v
```

---

## Other Useful Commands

### Run all free tests (Tier 1 + Tier 2):
```bash
pytest tests/ -v
```

### Run just one specific test:
```bash
pytest tests/test_analyzer_free.py::test_valid_response_passes_validation -v
```

### Run tests with more detail:
```bash
pytest tests/test_analyzer_free.py -vv -s
```

### Check which tests would run (don't execute):
```bash
pytest tests/test_analyzer_free.py --collect-only
```

---

## Quick Reference Card

| What | Command |
|------|---------|
| Navigate to backend | `cd C:\Users\mmed\OneDrive\Desktop\UITraps-Platform\backend` |
| Install dependencies | `pip install -r tests/requirements.txt` |
| Run Tier 1 tests | `pytest tests/test_analyzer_free.py -v` |
| Run all free tests | `pytest tests/ -v` |
| Run with more details | `pytest tests/test_analyzer_free.py -vv` |

---

## VS Code Shortcut (Easiest Method)

If you have VS Code open with the project:

1. Press **Ctrl + `** to open terminal
2. Paste this:
   ```bash
   cd backend && pip install -r tests/requirements.txt && pytest tests/test_analyzer_free.py -v
   ```
3. Press Enter
4. Done! ✅
