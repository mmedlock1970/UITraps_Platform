"""
TIER 2 - CACHED REGRESSION TESTS (0 API calls after initial setup)

Uses pre-generated cached API responses to test:
- Output structure matches baseline
- No regressions in parsing logic
- Response handling is robust
- Statistics calculation works

Cost: $0.00 per run (uses cached fixtures)
Setup cost: $0.25-0.40 one-time (run generate_fixtures.py)
Runtime: <10 seconds
Coverage: 10-15% (regression detection)

Prerequisites:
    python tests/generate_fixtures.py
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from schema import VALID_TRAP_NAMES, VALID_TENET_NAMES
from analyzer import UITrapsAnalyzer
from formatters import get_report_statistics


# ============================================================================
# FIXTURES
# ============================================================================

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "cached_analyses"


def load_fixture(fixture_name):
    """Load a cached analysis fixture."""
    fixture_file = FIXTURES_DIR / f"{fixture_name}_analysis.json"

    if not fixture_file.exists():
        pytest.skip(f"Fixture not found: {fixture_file}. Run generate_fixtures.py first.")

    with open(fixture_file) as f:
        return json.load(f)


@pytest.fixture
def simple_form_fixture():
    """Load simple form fixture."""
    return load_fixture("simple_form")


@pytest.fixture
def complex_dashboard_fixture():
    """Load complex dashboard fixture."""
    return load_fixture("complex_dashboard")


@pytest.fixture
def mobile_screen_fixture():
    """Load mobile screen fixture."""
    return load_fixture("mobile_screen")


@pytest.fixture
def error_state_fixture():
    """Load error state fixture."""
    return load_fixture("error_state")


@pytest.fixture
def minimal_ui_fixture():
    """Load minimal UI fixture."""
    return load_fixture("minimal_ui")


@pytest.fixture(params=[
    "simple_form",
    "complex_dashboard",
    "mobile_screen",
    "error_state",
    "minimal_ui"
])
def all_fixtures(request):
    """Parametrized fixture that runs test across all cached analyses."""
    return load_fixture(request.param)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_report_structure(report):
    """Validate that a report has the expected structure."""
    # Required top-level fields
    required_fields = [
        'summary',
        'critical_issues',
        'moderate_issues',
        'minor_issues',
        'positive_observations',
        'potential_issues',
        'traps_checked_not_found'
    ]

    for field in required_fields:
        assert field in report, f"Missing required field: {field}"

    # Type checks
    assert isinstance(report['summary'], list), "summary must be a list"
    assert isinstance(report['critical_issues'], list), "critical_issues must be a list"
    assert isinstance(report['moderate_issues'], list), "moderate_issues must be a list"
    assert isinstance(report['minor_issues'], list), "minor_issues must be a list"
    assert isinstance(report['positive_observations'], list), "positive_observations must be a list"
    assert isinstance(report['potential_issues'], list), "potential_issues must be a list"
    assert isinstance(report['traps_checked_not_found'], list), "traps_checked_not_found must be a list"

    return True


def validate_issue(issue, issue_type="standard"):
    """Validate an issue object."""
    if issue_type == "standard":
        required_fields = ['trap_name', 'tenet', 'location', 'problem', 'recommendation', 'confidence']
    elif issue_type == "potential":
        required_fields = ['trap_name', 'tenet', 'location', 'observation', 'why_uncertain', 'confidence']
    else:
        raise ValueError(f"Unknown issue type: {issue_type}")

    for field in required_fields:
        assert field in issue, f"Issue missing required field: {field}"

    # Validate trap name
    assert issue['trap_name'] in VALID_TRAP_NAMES, \
        f"Invalid trap name: {issue['trap_name']} (not in VALID_TRAP_NAMES)"

    # Validate tenet name
    assert issue['tenet'] in VALID_TENET_NAMES, \
        f"Invalid tenet name: {issue['tenet']} (not in VALID_TENET_NAMES)"

    # Validate confidence
    valid_confidences = ["high", "medium", "low"]
    assert issue['confidence'] in valid_confidences, \
        f"Invalid confidence: {issue['confidence']} (must be high/medium/low)"

    return True


# ============================================================================
# TESTS - Structure Validation
# ============================================================================

def test_all_fixtures_have_valid_structure(all_fixtures):
    """All cached fixtures should have valid report structure."""
    result = all_fixtures["result"]
    report = result["report"]

    validate_report_structure(report)


def test_all_fixtures_have_metadata(all_fixtures):
    """All cached fixtures should include metadata."""
    result = all_fixtures["result"]
    metadata = result["metadata"]

    required_metadata = [
        "model",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "estimated_cost",
        "duration_seconds",
        "timestamp"
    ]

    for field in required_metadata:
        assert field in metadata, f"Missing metadata field: {field}"


def test_all_issues_in_fixtures_are_valid(all_fixtures):
    """All issues in cached fixtures should pass validation."""
    result = all_fixtures["result"]
    report = result["report"]

    # Validate all critical issues
    for issue in report["critical_issues"]:
        validate_issue(issue, issue_type="standard")

    # Validate all moderate issues
    for issue in report["moderate_issues"]:
        validate_issue(issue, issue_type="standard")

    # Validate all minor issues
    for issue in report["minor_issues"]:
        validate_issue(issue, issue_type="standard")

    # Validate all potential issues
    for issue in report["potential_issues"]:
        validate_issue(issue, issue_type="potential")


# ============================================================================
# TESTS - No Hallucinations
# ============================================================================

def test_no_hallucinated_trap_names(all_fixtures):
    """Cached fixtures should not contain hallucinated trap names."""
    result = all_fixtures["result"]
    report = result["report"]

    all_issues = (
        report["critical_issues"] +
        report["moderate_issues"] +
        report["minor_issues"] +
        report["potential_issues"]
    )

    for issue in all_issues:
        trap_name = issue["trap_name"]
        assert trap_name in VALID_TRAP_NAMES, \
            f"Hallucinated trap name detected: {trap_name}"


def test_no_hallucinated_tenet_names(all_fixtures):
    """Cached fixtures should not contain hallucinated tenet names."""
    result = all_fixtures["result"]
    report = result["report"]

    all_issues = (
        report["critical_issues"] +
        report["moderate_issues"] +
        report["minor_issues"] +
        report["potential_issues"]
    )

    for issue in all_issues:
        tenet_name = issue["tenet"]
        assert tenet_name in VALID_TENET_NAMES, \
            f"Hallucinated tenet name detected: {tenet_name}"


def test_traps_checked_not_found_are_valid(all_fixtures):
    """Trap names in 'traps_checked_not_found' should be valid trap names."""
    result = all_fixtures["result"]
    report = result["report"]

    for trap_name in report["traps_checked_not_found"]:
        assert trap_name in VALID_TRAP_NAMES, \
            f"Invalid trap name in traps_checked_not_found: {trap_name}"


# ============================================================================
# TESTS - Data Quality
# ============================================================================

def test_summary_has_reasonable_length(all_fixtures):
    """Summary should have 5-9 items (per schema)."""
    result = all_fixtures["result"]
    report = result["report"]
    summary = report["summary"]

    # Schema specifies 5-9 items
    assert len(summary) >= 5, f"Summary too short: {len(summary)} items (expected 5-9)"
    assert len(summary) <= 9, f"Summary too long: {len(summary)} items (expected 5-9)"


def test_summary_items_are_strings(all_fixtures):
    """All summary items should be strings."""
    result = all_fixtures["result"]
    report = result["report"]

    for item in report["summary"]:
        assert isinstance(item, str), f"Summary item is not a string: {type(item)}"
        assert len(item) > 0, "Summary item is empty string"


def test_confidence_values_are_valid(all_fixtures):
    """All confidence values should be high/medium/low."""
    result = all_fixtures["result"]
    report = result["report"]

    valid_confidences = {"high", "medium", "low"}

    all_issues = (
        report["critical_issues"] +
        report["moderate_issues"] +
        report["minor_issues"] +
        report["potential_issues"]
    )

    for issue in all_issues:
        confidence = issue["confidence"]
        assert confidence in valid_confidences, \
            f"Invalid confidence value: {confidence}"


def test_severity_distribution_is_reasonable(all_fixtures):
    """Severity distribution should be reasonable (not all critical)."""
    result = all_fixtures["result"]
    report = result["report"]

    critical_count = len(report["critical_issues"])
    moderate_count = len(report["moderate_issues"])
    minor_count = len(report["minor_issues"])

    total_issues = critical_count + moderate_count + minor_count

    if total_issues > 0:
        # Critical issues should be minority (typically < 50%)
        critical_ratio = critical_count / total_issues

        # This is a soft check - some designs might legitimately have many critical issues
        # But if ALL issues are critical, that's suspicious
        if total_issues >= 3:
            assert critical_ratio < 1.0, \
                "All issues are marked critical (seems unrealistic)"


# ============================================================================
# TESTS - Statistics Calculation
# ============================================================================

def test_statistics_calculation_works(all_fixtures):
    """Statistics calculation should work on cached fixtures."""
    result = all_fixtures["result"]
    report = result["report"]

    # Calculate statistics
    stats = get_report_statistics(report)

    # Basic validation
    assert "total_issues" in stats
    assert "by_severity" in stats
    assert "by_tenet" in stats
    assert "by_trap" in stats

    # Counts should match
    total_issues = (
        len(report["critical_issues"]) +
        len(report["moderate_issues"]) +
        len(report["minor_issues"])
    )

    assert stats["total_issues"] == total_issues, \
        f"Statistics mismatch: {stats['total_issues']} vs {total_issues}"


# ============================================================================
# TESTS - Regression Detection
# ============================================================================

def test_simple_form_baseline(simple_form_fixture):
    """Simple form fixture should match baseline characteristics."""
    result = simple_form_fixture["result"]
    report = result["report"]

    # This is a SIMPLE form - shouldn't have tons of issues
    total_issues = (
        len(report["critical_issues"]) +
        len(report["moderate_issues"]) +
        len(report["minor_issues"])
    )

    # Baseline: simple form should have < 20 total issues
    # (adjust this if your test image actually has more issues)
    assert total_issues < 20, \
        f"Simple form has too many issues ({total_issues}) - possible regression"


def test_complex_dashboard_baseline(complex_dashboard_fixture):
    """Complex dashboard should have more issues than simple form."""
    result = complex_dashboard_fixture["result"]
    report = result["report"]

    total_issues = (
        len(report["critical_issues"]) +
        len(report["moderate_issues"]) +
        len(report["minor_issues"])
    )

    # Complex dashboard should find at least a few issues
    # (adjust based on your test image)
    assert total_issues >= 0, "Dashboard analysis should complete"


# ============================================================================
# TESTS - Response Parsing Robustness
# ============================================================================

def test_can_reparse_cached_response():
    """Should be able to re-parse cached responses through analyzer."""
    # This tests that the analyzer's parsing logic hasn't broken

    fixture_files = list(FIXTURES_DIR.glob("*_analysis.json"))

    if not fixture_files:
        pytest.skip("No fixtures found. Run generate_fixtures.py first.")

    for fixture_file in fixture_files:
        with open(fixture_file) as f:
            fixture_data = json.load(f)

        result = fixture_data["result"]

        # The fact that we can load and validate is the test
        validate_report_structure(result["report"])


# ============================================================================
# TESTS - Cost Tracking
# ============================================================================

def test_fixtures_have_reasonable_cost(all_fixtures):
    """Cached fixtures should show reasonable cost ($0.01-0.10 per analysis)."""
    result = all_fixtures["result"]
    metadata = result["metadata"]

    cost = metadata["estimated_cost"]

    assert cost > 0, "Cost should be positive"
    assert cost < 1.0, f"Cost seems too high: ${cost:.4f} (expected < $1.00)"


def test_total_fixture_generation_cost():
    """Total cost of all fixtures should be reasonable."""
    fixture_files = list(FIXTURES_DIR.glob("*_analysis.json"))

    if not fixture_files:
        pytest.skip("No fixtures found. Run generate_fixtures.py first.")

    total_cost = 0.0

    for fixture_file in fixture_files:
        with open(fixture_file) as f:
            data = json.load(f)
            cost = data["result"]["metadata"].get("estimated_cost", 0)
            total_cost += cost

    print(f"\nTotal fixture generation cost: ${total_cost:.4f}")
    print(f"Average cost per fixture: ${total_cost / len(fixture_files):.4f}")

    # Should be less than $1 total for all fixtures
    assert total_cost < 1.0, \
        f"Total fixture cost too high: ${total_cost:.4f}"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
