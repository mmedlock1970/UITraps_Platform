"""
Quick test script for interaction analysis with Claude.
Tests that the full pipeline works end-to-end.
"""

import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_interaction_analysis():
    """Test interaction analysis with captured data."""

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set in environment")
        return False
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")

    # Load captured interactions
    interactions_file = "test_output_forms/page_1_interactions.json"
    if not os.path.exists(interactions_file):
        print(f"ERROR: {interactions_file} not found. Run crawler first.")
        return False

    with open(interactions_file, "r") as f:
        interactions = json.load(f)

    print(f"\nLoaded {len(interactions)} interactions:")
    for i, ix in enumerate(interactions):
        print(f"  {i+1}. {ix['interaction_type']}: {ix['element_description']}")

    # Import analyzer
    from src.analyzer import UITrapsAnalyzer

    # Initialize analyzer
    analyzer = UITrapsAnalyzer(api_key=api_key)
    print("\nAnalyzer initialized")

    # Test with first interaction (hover)
    test_interaction = interactions[0]
    print(f"\n{'='*60}")
    print(f"Testing: {test_interaction['interaction_type'].upper()}")
    print(f"Element: {test_interaction['element_description']}")
    print(f"Screenshots: {test_interaction['screenshot_count']}")
    print(f"{'='*60}")

    # Convert to format expected by analyzer (Claude API format)
    images = []
    for img_b64 in test_interaction['screenshots_base64']:
        images.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": img_b64
            }
        })

    print(f"\nSending {len(images)} images to Claude for analysis...")

    # Run analysis
    result = analyzer.analyze_interaction_sequence(
        images=images,
        interaction_type=test_interaction['interaction_type'],
        element_description=test_interaction['element_description'],
        labels=test_interaction['labels'],
        user_context={"product_type": "Test form page"},
        timeout=60
    )

    print("\n" + "="*60)
    print("ANALYSIS RESULT")
    print("="*60)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        return False

    # Get actual analysis data (nested under 'analysis' key)
    analysis = result.get('analysis', result)

    print(f"\nOverall Assessment: {analysis.get('overall_assessment', 'N/A')}")
    print(f"\nFeedback Quality:")
    fq = analysis.get('feedback_quality', {})
    print(f"  - Has visual feedback: {fq.get('has_visual_feedback', 'N/A')}")
    print(f"  - Timing: {fq.get('feedback_timing', 'N/A')}")
    print(f"  - Clarity: {fq.get('feedback_clarity', 'N/A')}")
    print(f"  - Description: {fq.get('feedback_description', 'N/A')[:100]}...")

    print(f"\nState Transition:")
    st = analysis.get('state_transition', {})
    print(f"  - Predictable: {st.get('is_predictable', 'N/A')}")
    print(f"  - Reversible: {st.get('is_reversible', 'N/A')}")
    print(f"  - Maintains context: {st.get('maintains_context', 'N/A')}")

    traps = analysis.get('traps_detected', [])
    print(f"\nTraps Detected: {len(traps)}")
    for trap in traps:
        print(f"  - [{trap.get('severity', '?').upper()}] {trap.get('trap_name', 'Unknown')}")
        print(f"    Tenet: {trap.get('tenet', 'N/A')}")
        print(f"    {trap.get('observation', '')[:100]}...")

    access = analysis.get('accessibility_concerns', [])
    print(f"\nAccessibility Concerns: {len(access)}")
    for ac in access[:2]:
        print(f"  - {ac.get('concern', '')[:80]}...")

    print(f"\nPositive Observations: {len(analysis.get('positive_observations', []))}")
    for obs in analysis.get('positive_observations', [])[:3]:
        print(f"  - {obs[:80]}...")

    print(f"\nSummary: {analysis.get('summary', 'N/A')[:200]}...")

    # Print metadata
    meta = result.get('metadata', {})
    if meta:
        print(f"\n--- Metadata ---")
        print(f"Model: {meta.get('model', 'N/A')}")
        print(f"Duration: {meta.get('duration_seconds', 'N/A')}s")
        print(f"Cost: ${meta.get('estimated_cost', 0):.4f}")

    return True


if __name__ == "__main__":
    print("="*60)
    print("INTERACTION ANALYSIS TEST")
    print("="*60)

    success = test_interaction_analysis()

    print("\n" + "="*60)
    print(f"TEST {'PASSED' if success else 'FAILED'}")
    print("="*60)
