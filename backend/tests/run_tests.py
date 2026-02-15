#!/usr/bin/env python3
"""
Quick test runner script with cost awareness.

This provides a friendly interface to run different test tiers.
"""

import sys
import subprocess
from pathlib import Path


def print_banner(text, char="="):
    """Print a banner."""
    print(f"\n{char * 70}")
    print(text)
    print(f"{char * 70}\n")


def run_command(cmd, description):
    """Run a command and show output."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)

    if result.returncode != 0:
        print(f"\n❌ {description} failed!")
        return False
    else:
        print(f"\n✅ {description} passed!")
        return True


def main():
    """Main runner."""
    print_banner("UI Traps Analyzer - Test Runner")

    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [tier1|tier2|all|real-api|help]")
        print("\nOptions:")
        print("  tier1     - Run Tier 1 tests (free validation, <5 sec, $0)")
        print("  tier2     - Run Tier 2 tests (cached regression, <10 sec, $0)")
        print("  all       - Run Tier 1 + 2 (everything that's free, <15 sec, $0)")
        print("  real-api  - Run Tier 3 tests (real API calls, ~60 sec, ~$0.25)")
        print("  help      - Show this help")
        print("\nRecommended for development:")
        print("  python run_tests.py all")
        return

    command = sys.argv[1].lower()

    if command == "help":
        print("Test Tiers:")
        print("\nTier 1 - Free Validation")
        print("  - Cost: $0.00")
        print("  - Runtime: <5 seconds")
        print("  - Tests: Schema validation, no hallucinations, data types")
        print("  - Run: python run_tests.py tier1")

        print("\nTier 2 - Cached Regression")
        print("  - Cost: $0.00 (after one-time setup)")
        print("  - Runtime: <10 seconds")
        print("  - Tests: Regression detection, parsing validation")
        print("  - Setup: python tests/generate_fixtures.py")
        print("  - Run: python run_tests.py tier2")

        print("\nTier 3 - Real API Smoke Tests")
        print("  - Cost: ~$0.25 per run")
        print("  - Runtime: 30-60 seconds")
        print("  - Tests: End-to-end validation with real API")
        print("  - Run: python run_tests.py real-api")

    elif command == "tier1":
        print_banner("Running Tier 1: Free Validation Tests", "=")
        print("💰 Cost: $0.00")
        print("⏱️  Expected runtime: <5 seconds\n")

        run_command(
            ["pytest", "tests/test_analyzer_free.py", "-v"],
            "Tier 1 Tests"
        )

    elif command == "tier2":
        print_banner("Running Tier 2: Cached Regression Tests", "=")
        print("💰 Cost: $0.00")
        print("⏱️  Expected runtime: <10 seconds\n")

        # Check if fixtures exist
        fixtures_dir = Path(__file__).parent / "fixtures" / "cached_analyses"
        if not fixtures_dir.exists() or not list(fixtures_dir.glob("*.json")):
            print("❌ ERROR: No cached fixtures found!")
            print("\nYou need to generate fixtures first:")
            print("  python tests/generate_fixtures.py")
            print("\nThis is a one-time setup cost of ~$0.30")
            return

        run_command(
            ["pytest", "tests/test_analyzer_cached.py", "-v"],
            "Tier 2 Tests"
        )

    elif command == "all":
        print_banner("Running All Free Tests (Tier 1 + 2)", "=")
        print("💰 Cost: $0.00")
        print("⏱️  Expected runtime: <15 seconds")
        print("\nThis is the recommended test suite for development.\n")

        # Run Tier 1
        success1 = run_command(
            ["pytest", "tests/test_analyzer_free.py", "-v"],
            "Tier 1 Tests"
        )

        # Run Tier 2
        fixtures_dir = Path(__file__).parent / "fixtures" / "cached_analyses"
        if not fixtures_dir.exists() or not list(fixtures_dir.glob("*.json")):
            print("\n⚠️  WARNING: Skipping Tier 2 (no cached fixtures)")
            print("   Generate fixtures with: python tests/generate_fixtures.py")
            success2 = True  # Don't fail if fixtures missing
        else:
            success2 = run_command(
                ["pytest", "tests/test_analyzer_cached.py", "-v"],
                "Tier 2 Tests"
            )

        if success1 and success2:
            print_banner("✅ All Free Tests Passed!", "=")
            print("💰 Total cost: $0.00")
        else:
            print_banner("❌ Some Tests Failed", "=")
            sys.exit(1)

    elif command == "real-api":
        print_banner("⚠️  WARNING: Running Real API Tests (Tier 3)", "!")
        print("💰 Cost: ~$0.25 per run")
        print("⏱️  Runtime: 30-60 seconds")
        print("\nThese tests make REAL API calls and cost money.")
        print("Only run before major releases or after significant changes.\n")

        response = input("Continue? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("❌ Cancelled by user")
            return

        import os
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("\n❌ ERROR: ANTHROPIC_API_KEY not set!")
            print("Set it in .env file or environment variable")
            return

        run_command(
            ["pytest", "tests/test_analyzer_real_api.py", "-v", "-m", "real_api"],
            "Tier 3 Real API Tests"
        )

    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python run_tests.py help' for usage")


if __name__ == "__main__":
    main()
