"""
FIXTURE GENERATION SCRIPT

Generates cached API responses for Tier 2 regression tests.

IMPORTANT: This script costs money (~$0.25-0.40) and should only be run:
1. Initially to create fixtures
2. When you change the system prompt (prompts.py)
3. When you change the schema (schema.py)
4. When you upgrade Claude model version

DO NOT run this on every test run - that's the whole point of caching!

Usage:
    python tests/generate_fixtures.py

Cost: $0.25-0.40 (one-time)
Runtime: ~60-90 seconds
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Add backend to path (not src directly)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer import UITrapsAnalyzer


# ============================================================================
# TEST IMAGES CONFIGURATION
# ============================================================================

# Define test images to generate fixtures for
# These should cover diverse scenarios to catch regressions
TEST_IMAGES = [
    {
        "name": "simple_form",
        "description": "Basic form with inputs and submit button",
        "path": "tests/fixtures/images/simple_form.png",
        "user_context": {
            "users": "General users filling out contact information",
            "tasks": "Submit contact form with name, email, and message",
            "format": "PNG screenshot"
        }
    },
    {
        "name": "complex_dashboard",
        "description": "Dense dashboard with multiple widgets",
        "path": "tests/fixtures/images/complex_dashboard.png",
        "user_context": {
            "users": "Data analysts and managers",
            "tasks": "Monitor metrics, view reports, analyze trends",
            "format": "PNG screenshot"
        }
    },
    {
        "name": "mobile_screen",
        "description": "Mobile app interface",
        "path": "tests/fixtures/images/mobile_screen.png",
        "user_context": {
            "users": "Mobile app users",
            "tasks": "Browse products, add to cart, checkout",
            "format": "PNG screenshot"
        }
    },
    {
        "name": "error_state",
        "description": "Error screen or validation failure",
        "path": "tests/fixtures/images/error_state.png",
        "user_context": {
            "users": "Users encountering errors",
            "tasks": "Understand error and recover",
            "format": "PNG screenshot"
        }
    },
    {
        "name": "minimal_ui",
        "description": "Very simple UI with few elements",
        "path": "tests/fixtures/images/minimal_ui.png",
        "user_context": {
            "users": "All users",
            "tasks": "Complete simple action",
            "format": "PNG screenshot"
        }
    }
]


# ============================================================================
# MAIN GENERATION LOGIC
# ============================================================================

def generate_fixtures():
    """Generate cached analysis fixtures from test images."""

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not set in environment")
        print("   Set it in .env file or environment variable")
        return False

    print("=" * 70)
    print("FIXTURE GENERATION - TIER 2 CACHED TESTS")
    print("=" * 70)
    print(f"\n⚠️  WARNING: This will cost ~$0.05 per image × {len(TEST_IMAGES)} images")
    print(f"   Estimated total cost: ${0.05 * len(TEST_IMAGES):.2f}")
    print("\nThis is a ONE-TIME cost. Generated fixtures can be reused forever.")
    print("=" * 70)

    # Confirm before proceeding
    response = input("\nProceed with fixture generation? (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("❌ Cancelled by user")
        return False

    # Create output directory
    output_dir = Path(__file__).parent / "fixtures" / "cached_analyses"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize analyzer
    try:
        analyzer = UITrapsAnalyzer(api_key=api_key, use_caching=True)
        print("\n✅ Analyzer initialized")
    except Exception as e:
        print(f"\n❌ Failed to initialize analyzer: {e}")
        return False

    # Track results
    successful = 0
    failed = 0
    total_cost = 0.0
    total_duration = 0.0

    # Process each test image
    for i, test_config in enumerate(TEST_IMAGES):
        print(f"\n{'-' * 70}")
        print(f"[{i+1}/{len(TEST_IMAGES)}] Processing: {test_config['name']}")
        print(f"Description: {test_config['description']}")
        print(f"{'-' * 70}")

        image_path = Path(__file__).parent.parent / test_config["path"]

        # Check if image exists
        if not image_path.exists():
            print(f"⚠️  WARNING: Image not found at {image_path}")
            print(f"   Skipping this fixture (you can add the image later)")
            failed += 1
            continue

        try:
            # Run analysis
            print(f"Analyzing {image_path.name}...")
            start_time = time.time()

            result = analyzer.analyze_design(
                design_file=str(image_path),
                user_context=test_config["user_context"],
                timeout=120
            )

            duration = time.time() - start_time

            # Check if successful
            if result.get("status") != "success":
                print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                failed += 1
                continue

            # Extract key info
            metadata = result.get("metadata", {})
            report = result.get("report", {})

            cost = metadata.get("estimated_cost", 0)
            total_cost += cost
            total_duration += duration

            # Print summary
            print(f"✅ Analysis complete:")
            print(f"   - Duration: {duration:.1f}s")
            print(f"   - Cost: ${cost:.4f}")
            print(f"   - Tokens: {metadata.get('total_tokens', 0)}")

            # Count findings
            critical = len(report.get("critical_issues", []))
            moderate = len(report.get("moderate_issues", []))
            minor = len(report.get("minor_issues", []))
            print(f"   - Findings: {critical} critical, {moderate} moderate, {minor} minor")

            # Save fixture
            fixture_data = {
                "test_config": test_config,
                "result": result,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "model": metadata.get("model"),
                "note": "This is a cached fixture. Do not edit manually."
            }

            fixture_file = output_dir / f"{test_config['name']}_analysis.json"
            with open(fixture_file, "w") as f:
                json.dump(fixture_data, f, indent=2)

            print(f"   - Saved to: {fixture_file.name}")

            successful += 1

            # Rate limiting - wait 1 second between requests
            if i < len(TEST_IMAGES) - 1:
                print("   - Waiting 1s before next request...")
                time.time.sleep(1)

        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1

    # Final summary
    print("\n" + "=" * 70)
    print("FIXTURE GENERATION COMPLETE")
    print("=" * 70)
    print(f"\n✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"💰 Total cost: ${total_cost:.4f}")
    print(f"⏱️  Total time: {total_duration:.1f}s")

    if successful > 0:
        print(f"\n📁 Fixtures saved to: {output_dir}")
        print(f"   Run tests with: pytest tests/test_analyzer_cached.py -v")

    return successful > 0


def list_fixtures():
    """List existing fixtures."""
    fixture_dir = Path(__file__).parent / "fixtures" / "cached_analyses"

    if not fixture_dir.exists():
        print("No fixtures directory found")
        return

    fixtures = list(fixture_dir.glob("*.json"))

    if not fixtures:
        print("No fixtures found")
        return

    print(f"\nExisting fixtures ({len(fixtures)}):")
    for fixture_file in sorted(fixtures):
        try:
            with open(fixture_file) as f:
                data = json.load(f)
                test_name = data.get("test_config", {}).get("name", "Unknown")
                generated_at = data.get("generated_at", "Unknown")
                model = data.get("model", "Unknown")
                print(f"  - {fixture_file.name}")
                print(f"      Test: {test_name}")
                print(f"      Generated: {generated_at}")
                print(f"      Model: {model}")
        except Exception as e:
            print(f"  - {fixture_file.name} (error reading: {e})")


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate test fixtures for Tier 2 cached tests")
    parser.add_argument("--list", action="store_true", help="List existing fixtures")

    args = parser.parse_args()

    if args.list:
        list_fixtures()
    else:
        success = generate_fixtures()
        sys.exit(0 if success else 1)
