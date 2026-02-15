"""
TIER 3 - REAL API SMOKE TESTS (costs money - use sparingly!)

Real end-to-end tests with actual Claude API calls.

⚠️  WARNING: These tests cost $0.05-0.10 per run!

Only run these:
- Before major releases
- After prompt/schema changes
- After Claude model upgrades
- When Tier 1+2 tests pass but you want extra confidence

Cost: $0.15-0.25 per full run (3-5 test cases)
Runtime: 30-60 seconds
Coverage: 5-10% (end-to-end validation)

Usage:
    # Skip by default (marked with @pytest.mark.real_api)
    pytest tests/ -v

    # Explicitly run expensive tests
    pytest tests/test_analyzer_real_api.py -v -m real_api

Prerequisites:
    - ANTHROPIC_API_KEY environment variable set
    - Test images in tests/fixtures/images/
"""

import pytest
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyzer import UITrapsAnalyzer
from schema import VALID_TRAP_NAMES, VALID_TENET_NAMES


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

# Mark all tests in this file as "real_api" so they can be skipped by default
pytestmark = pytest.mark.real_api


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def api_key():
    """Get API key from environment."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY not set. Cannot run real API tests.")
    return key


@pytest.fixture(scope="module")
def analyzer(api_key):
    """Create analyzer instance (reuse across tests in this module)."""
    return UITrapsAnalyzer(api_key=api_key, use_caching=True)


@pytest.fixture
def test_images_dir():
    """Get test images directory."""
    return Path(__file__).parent / "fixtures" / "images"


# ============================================================================
# SMOKE TESTS - Core Functionality
# ============================================================================

@pytest.mark.real_api
def test_can_analyze_simple_form(analyzer, test_images_dir):
    """
    SMOKE TEST: Can analyze a simple form.

    Cost: ~$0.05
    """
    image_path = test_images_dir / "simple_form.png"

    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")

    result = analyzer.analyze_design(
        design_file=str(image_path),
        user_context={
            "users": "General users",
            "tasks": "Fill out contact form",
            "format": "PNG screenshot"
        },
        timeout=120
    )

    # Basic validation
    assert result["status"] == "success", "Analysis should succeed"
    assert "report" in result, "Should have report"
    assert "metadata" in result, "Should have metadata"

    # Validate report structure
    report = result["report"]
    required_fields = [
        'summary', 'critical_issues', 'moderate_issues',
        'minor_issues', 'positive_observations', 'potential_issues',
        'traps_checked_not_found'
    ]

    for field in required_fields:
        assert field in report, f"Missing field: {field}"

    # No hallucinations
    all_issues = (
        report["critical_issues"] +
        report["moderate_issues"] +
        report["minor_issues"] +
        report["potential_issues"]
    )

    for issue in all_issues:
        assert issue["trap_name"] in VALID_TRAP_NAMES, \
            f"Hallucinated trap name: {issue['trap_name']}"
        assert issue["tenet"] in VALID_TENET_NAMES, \
            f"Hallucinated tenet name: {issue['tenet']}"

    # Print summary
    print(f"\n✅ Analysis successful:")
    print(f"   Cost: ${result['metadata']['estimated_cost']:.4f}")
    print(f"   Duration: {result['metadata']['duration_seconds']:.1f}s")
    print(f"   Findings: {len(report['critical_issues'])} critical, "
          f"{len(report['moderate_issues'])} moderate, "
          f"{len(report['minor_issues'])} minor")


@pytest.mark.real_api
def test_can_analyze_complex_dashboard(analyzer, test_images_dir):
    """
    SMOKE TEST: Can analyze a complex dashboard.

    Cost: ~$0.05
    """
    image_path = test_images_dir / "complex_dashboard.png"

    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")

    result = analyzer.analyze_design(
        design_file=str(image_path),
        user_context={
            "users": "Data analysts",
            "tasks": "Monitor metrics and view reports",
            "format": "PNG screenshot"
        },
        timeout=120
    )

    assert result["status"] == "success"
    assert len(result["report"]["summary"]) >= 5, "Summary should have at least 5 points"


@pytest.mark.real_api
def test_can_analyze_mobile_screen(analyzer, test_images_dir):
    """
    SMOKE TEST: Can analyze a mobile interface.

    Cost: ~$0.05
    """
    image_path = test_images_dir / "mobile_screen.png"

    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")

    result = analyzer.analyze_design(
        design_file=str(image_path),
        user_context={
            "users": "Mobile app users",
            "tasks": "Browse and purchase products",
            "format": "PNG screenshot"
        },
        timeout=120
    )

    assert result["status"] == "success"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

@pytest.mark.real_api
def test_can_analyze_error_state(analyzer, test_images_dir):
    """
    EDGE CASE: Can analyze an error screen.

    Cost: ~$0.05
    """
    image_path = test_images_dir / "error_state.png"

    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")

    result = analyzer.analyze_design(
        design_file=str(image_path),
        user_context={
            "users": "Users encountering errors",
            "tasks": "Understand error and recover",
            "format": "PNG screenshot"
        },
        timeout=120
    )

    assert result["status"] == "success"

    # Error screens often have specific trap patterns
    report = result["report"]
    print(f"\nError state analysis:")
    print(f"   Total issues: {len(report['critical_issues']) + len(report['moderate_issues'])}")


@pytest.mark.real_api
def test_can_analyze_minimal_ui(analyzer, test_images_dir):
    """
    EDGE CASE: Can analyze very simple UI.

    Cost: ~$0.05
    """
    image_path = test_images_dir / "minimal_ui.png"

    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")

    result = analyzer.analyze_design(
        design_file=str(image_path),
        user_context={
            "users": "All users",
            "tasks": "Complete simple action",
            "format": "PNG screenshot"
        },
        timeout=120
    )

    assert result["status"] == "success"

    # Minimal UI should have fewer issues
    report = result["report"]
    total_issues = (
        len(report["critical_issues"]) +
        len(report["moderate_issues"]) +
        len(report["minor_issues"])
    )

    print(f"\nMinimal UI analysis:")
    print(f"   Total issues: {total_issues}")


# ============================================================================
# VALIDATION TESTS
# ============================================================================

@pytest.mark.real_api
def test_metadata_is_accurate(analyzer, test_images_dir):
    """
    Validate that metadata (cost, tokens, etc.) is accurate.

    Cost: ~$0.05
    """
    image_path = test_images_dir / "simple_form.png"

    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")

    result = analyzer.analyze_design(
        design_file=str(image_path),
        user_context={"users": "Test", "tasks": "Test", "format": "PNG"},
        timeout=120
    )

    metadata = result["metadata"]

    # Validate metadata fields
    assert metadata["model"] == "claude-sonnet-4-5-20250929"
    assert metadata["input_tokens"] > 0, "Should have input tokens"
    assert metadata["output_tokens"] > 0, "Should have output tokens"
    assert metadata["total_tokens"] == metadata["input_tokens"] + metadata["output_tokens"]
    assert metadata["estimated_cost"] > 0, "Should have positive cost"
    assert metadata["duration_seconds"] > 0, "Should have positive duration"

    print(f"\nMetadata validation:")
    print(f"   Input tokens: {metadata['input_tokens']}")
    print(f"   Output tokens: {metadata['output_tokens']}")
    print(f"   Cost: ${metadata['estimated_cost']:.4f}")


# ============================================================================
# TOTAL COST CALCULATION
# ============================================================================

def test_print_total_run_cost(api_key):
    """
    Not a real test - just prints expected cost of running all real API tests.

    This helps track budget.
    """
    # Count number of @pytest.mark.real_api tests in this file
    # Each test costs ~$0.05

    import inspect

    test_count = 0
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj) and name.startswith("test_"):
            if hasattr(obj, "pytestmark") or "pytestmark" in globals():
                # Check if marked as real_api
                marks = getattr(obj, "pytestmark", [])
                if marks or pytestmark:
                    test_count += 1

    # Subtract this test itself
    test_count -= 1

    estimated_cost = test_count * 0.05

    print(f"\n" + "=" * 70)
    print(f"TIER 3 - REAL API TESTS COST ESTIMATE")
    print(f"=" * 70)
    print(f"Tests marked @real_api: {test_count}")
    print(f"Estimated cost per test: $0.05")
    print(f"Total estimated cost: ${estimated_cost:.2f}")
    print(f"=" * 70)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    # When run directly, show cost warning
    print("\n⚠️  WARNING: Running real API tests will cost money (~$0.25)")
    print("These tests make actual API calls to Claude.")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()

    pytest.main([__file__, "-v", "-s"])
