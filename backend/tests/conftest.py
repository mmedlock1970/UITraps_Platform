"""
Pytest configuration for UI Traps Analyzer tests.

Defines custom markers and shared fixtures.
"""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "real_api: marks tests that make real API calls (deselect with '-m \"not real_api\"')"
    )


def pytest_collection_modifyitems(config, items):
    """
    Auto-skip real_api tests unless explicitly requested.

    By default, real API tests are skipped to avoid costs.
    To run them, use: pytest -m real_api
    """
    # Check if user is explicitly running real_api tests
    markexpr = config.option.markexpr
    if markexpr and "real_api" in markexpr:
        # User explicitly wants real_api tests - don't skip
        return

    # Otherwise, skip real_api tests by default
    skip_real_api = pytest.mark.skip(reason="Skipping real API tests by default (cost money). Run with: pytest -m real_api")

    for item in items:
        if "real_api" in item.keywords:
            item.add_marker(skip_real_api)


# ============================================================================
# SHARED FIXTURES
# ============================================================================

@pytest.fixture
def sample_user_context():
    """Sample user context for tests."""
    return {
        "users": "Software developers and testers",
        "tasks": "Running tests, viewing results, debugging failures",
        "format": "PNG screenshot"
    }


@pytest.fixture
def mock_image_path(tmp_path):
    """Create a temporary mock image file for testing."""
    import base64
    from pathlib import Path

    # Create a minimal 1x1 PNG (valid PNG header)
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )

    image_file = tmp_path / "test.png"
    image_file.write_bytes(png_data)

    return str(image_file)


# ============================================================================
# PYTEST HOOKS
# ============================================================================

def pytest_report_header(config):
    """Add custom header to test report."""
    return [
        "UI Traps Analyzer - Test Suite",
        "Tier 1: Free validation (always run)",
        "Tier 2: Cached regression tests (run generate_fixtures.py first)",
        "Tier 3: Real API tests (costs money, skip by default)"
    ]


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add cost summary at end of test run."""
    # Count tests by tier
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    skipped = len(terminalreporter.stats.get("skipped", []))

    # Check if real_api tests were run
    real_api_run = any(
        "real_api" in item.keywords
        for item in terminalreporter.stats.get("passed", [])
    )

    terminalreporter.write_sep("=", "Test Run Summary")
    terminalreporter.write_line(f"Passed: {passed}")
    terminalreporter.write_line(f"Failed: {failed}")
    terminalreporter.write_line(f"Skipped: {skipped}")

    if real_api_run:
        terminalreporter.write_sep("=", "Cost Estimate")
        terminalreporter.write_line("⚠️  Real API tests were run")
        terminalreporter.write_line(f"Estimated cost: ~${passed * 0.05:.2f}")
    else:
        terminalreporter.write_sep("=", "Cost")
        terminalreporter.write_line("✅ No API costs (Tier 1+2 tests only)")
