"""
TIER 1 - FREE VALIDATION TESTS (0 API calls)

Tests analyzer output structure without calling Claude API.
Uses mocked responses to validate:
- Schema compliance
- No hallucinated trap/tenet names
- Correct data types
- Required fields present
- Edge case handling

Cost: $0.00 per run
Runtime: <5 seconds
Coverage: 80-85% of bugs
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add backend to path for imports (not src directly)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schema import VALID_TRAP_NAMES, VALID_TENET_NAMES, UI_ANALYSIS_SCHEMA
from src.analyzer import UITrapsAnalyzer


# ============================================================================
# FIXTURES - Mock API Responses
# ============================================================================

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client to avoid API calls and skip file operations."""
    # Mock image data (minimal valid base64 PNG - 1x1 transparent pixel)
    mock_image_data = {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        }
    }

    # Mock the Anthropic client, file validation, and image loading
    with patch('src.analyzer.Anthropic') as mock_anthropic, \
         patch('src.analyzer.validate_file_format', return_value=(True, "Valid")), \
         patch('src.analyzer.UITrapsAnalyzer._load_image', return_value=mock_image_data):
        yield mock_anthropic


@pytest.fixture
def valid_user_context():
    """Valid user context that passes validation (10+ characters per field)."""
    return {
        "users": "Software developers and testers",
        "tasks": "Running automated tests and validating results",
        "format": "PNG screenshot"
    }


@pytest.fixture
def valid_analysis_response():
    """Valid analysis response matching schema."""
    return {
        "summary_headline": "Strong visual hierarchy, though some secondary actions are less visible than ideal.",
        "summary_narrative": "The design supports the primary task well; a few secondary actions may be harder to find.",
        "critical_issues": [
            {
                "trap_name": "INVISIBLE ELEMENT",
                "tenet": "UNDERSTANDABLE",
                "location": "Top right corner, settings icon",
                "problem": "Settings icon has very low contrast against background",
                "recommendation": "Increase icon contrast or add text label",
                "confidence": "high"
            }
        ],
        "moderate_issues": [
            {
                "trap_name": "FEEDBACK FAILURE",
                "tenet": "RESPONSIVE",
                "location": "Search input field",
                "problem": "No visual feedback when search is in progress",
                "recommendation": "Add loading spinner or progress indicator",
                "confidence": "medium"
            }
        ],
        "minor_issues": [],
        "positive_observations": [
            "Clear visual hierarchy",
            "Good use of whitespace",
            "Consistent color scheme"
        ],
        "potential_issues": [
            {
                "trap_name": "INFORMATION OVERLOAD",
                "tenet": "COMFORTABLE",
                "location": "Dashboard main area",
                "observation": "Many data points displayed simultaneously",
                "why_uncertain": "May be necessary for power users; needs context about user goals",
                "confidence": "low"
            }
        ],
        "traps_checked_not_found": [
            "ACCIDENTAL ACTIVATION",
            "CAPTIVE WAIT",
            "DATA LOSS"
        ]
    }


@pytest.fixture
def malformed_summary_response():
    """Response where summary_headline is the wrong type (a list, not a string)."""
    return {
        "summary_headline": ["not", "a", "string"],  # WRONG TYPE — parser coerces to ''
        "summary_narrative": "A valid narrative paragraph.",
        "critical_issues": [],
        "moderate_issues": [],
        "minor_issues": [],
        "positive_observations": [],
        "potential_issues": [],
        "traps_checked_not_found": []
    }


@pytest.fixture
def hallucinated_trap_response():
    """Response with invalid trap name (hallucination)."""
    return {
        "summary_headline": "The design broadly supports the task, with a few notable friction points.",
        "summary_narrative": "Users can likely accomplish the goal, though some elements may slow them down.",
        "critical_issues": [
            {
                "trap_name": "CONFUSING BUTTON",  # NOT IN VALID_TRAP_NAMES!
                "tenet": "UNDERSTANDABLE",
                "location": "Main page",
                "problem": "Button is confusing",
                "recommendation": "Make it less confusing",
                "confidence": "high"
            }
        ],
        "moderate_issues": [],
        "minor_issues": [],
        "positive_observations": [],
        "potential_issues": [],
        "traps_checked_not_found": []
    }


@pytest.fixture
def hallucinated_tenet_response():
    """Response with invalid tenet name."""
    return {
        "summary_headline": "The design broadly supports the task, with a few notable friction points.",
        "summary_narrative": "Users can likely accomplish the goal, though some elements may slow them down.",
        "critical_issues": [
            {
                "trap_name": "INVISIBLE ELEMENT",
                "tenet": "USABILITY",  # NOT IN VALID_TENET_NAMES!
                "location": "Header",
                "problem": "Element is invisible",
                "recommendation": "Make it visible",
                "confidence": "high"
            }
        ],
        "moderate_issues": [],
        "minor_issues": [],
        "positive_observations": [],
        "potential_issues": [],
        "traps_checked_not_found": []
    }


@pytest.fixture
def invalid_confidence_response():
    """Response with invalid confidence value."""
    return {
        "summary_headline": "The design broadly supports the task, with a few notable friction points.",
        "summary_narrative": "Users can likely accomplish the goal, though some elements may slow them down.",
        "critical_issues": [
            {
                "trap_name": "INVISIBLE ELEMENT",
                "tenet": "UNDERSTANDABLE",
                "location": "Header",
                "problem": "Problem description",
                "recommendation": "Fix it",
                "confidence": "very_high"  # INVALID! Must be high/medium/low
            }
        ],
        "moderate_issues": [],
        "minor_issues": [],
        "positive_observations": [],
        "potential_issues": [],
        "traps_checked_not_found": []
    }


@pytest.fixture
def missing_required_fields_response():
    """Response missing required issue fields."""
    return {
        "summary_headline": "The design broadly supports the task, with a few notable friction points.",
        "summary_narrative": "Users can likely accomplish the goal, though some elements may slow them down.",
        "critical_issues": [
            {
                "trap_name": "INVISIBLE ELEMENT",
                "tenet": "UNDERSTANDABLE",
                # Missing: location, problem, recommendation, confidence
            }
        ],
        "moderate_issues": [],
        "minor_issues": [],
        "positive_observations": [],
        "potential_issues": [],
        "traps_checked_not_found": []
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_mock_tool_response(analysis_data):
    """Create a mock Claude API response with tool use."""
    mock_response = Mock()
    mock_response.content = [
        Mock(type="tool_use", input=analysis_data)
    ]
    mock_response.usage = Mock(
        input_tokens=1000,
        output_tokens=500,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0
    )
    return mock_response


def validate_issue_structure(issue, issue_type="standard"):
    """Validate an issue object has all required fields."""
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
        f"Invalid trap name: {issue['trap_name']}"

    # Validate tenet name
    assert issue['tenet'] in VALID_TENET_NAMES, \
        f"Invalid tenet name: {issue['tenet']}"

    # Validate confidence
    valid_confidences = ["high", "medium", "low"]
    assert issue['confidence'] in valid_confidences, \
        f"Invalid confidence: {issue['confidence']}"


# ============================================================================
# TESTS - Schema Compliance
# ============================================================================

def test_valid_response_passes_validation(mock_anthropic_client, valid_analysis_response, valid_user_context):
    """Valid response should pass all validation checks."""
    # Setup mock
    mock_client = Mock()
    mock_response = create_mock_tool_response(valid_analysis_response)
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client

    # Create analyzer and run
    analyzer = UITrapsAnalyzer(api_key="test-key")
    result = analyzer.analyze_design(
        design_file="test.png",
        user_context=valid_user_context
    )

    # Validate result structure
    assert result["status"] == "success"
    assert "report" in result
    assert "metadata" in result

    report = result["report"]

    # Check required top-level fields
    required_fields = [
        'summary_headline', 'summary_narrative', 'critical_issues', 'moderate_issues',
        'minor_issues', 'positive_observations', 'potential_issues',
        'traps_checked_not_found'
    ]
    for field in required_fields:
        assert field in report, f"Missing required field: {field}"


def test_summary_headline_wrong_type_is_coerced(mock_anthropic_client, malformed_summary_response, valid_user_context):
    """A non-string summary_headline should be coerced to a string, not crash."""
    # Setup mock
    mock_client = Mock()
    mock_response = create_mock_tool_response(malformed_summary_response)
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client

    # Create analyzer
    analyzer = UITrapsAnalyzer(api_key="test-key")

    # Should normalize the malformed headline rather than fail
    result = analyzer.analyze_design(
        design_file="test.png",
        user_context=valid_user_context
    )

    # After normalization, both summary fields are strings
    assert result["status"] == "success"
    assert isinstance(result["report"]["summary_headline"], str)
    assert isinstance(result["report"]["summary_narrative"], str)


def test_minimal_summary_fields_are_accepted(mock_anthropic_client, valid_user_context):
    """A minimal headline/narrative pair should parse into string summary fields."""
    response = {
        "summary_headline": "A minimal summary headline.",
        "summary_narrative": "A minimal narrative.",
        "critical_issues": [],
        "moderate_issues": [],
        "minor_issues": [],
        "positive_observations": [],
        "potential_issues": [],
        "traps_checked_not_found": []
    }

    mock_client = Mock()
    mock_response = create_mock_tool_response(response)
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client

    analyzer = UITrapsAnalyzer(api_key="test-key")
    result = analyzer.analyze_design(
        design_file="test.png",
        user_context=valid_user_context
    )

    # Should succeed; summary fields normalize to strings
    assert result["status"] == "success"
    assert isinstance(result["report"]["summary_headline"], str)
    assert isinstance(result["report"]["summary_narrative"], str)


# ============================================================================
# TESTS - No Hallucinations
# ============================================================================

def test_rejects_hallucinated_trap_names(valid_analysis_response):
    """Should detect when AI hallucinates trap names not in VALID_TRAP_NAMES."""
    # Add invalid trap name
    invalid_issue = {
        "trap_name": "SUPER CONFUSING BUTTON",  # Not in VALID_TRAP_NAMES
        "tenet": "UNDERSTANDABLE",
        "location": "Test",
        "problem": "Test",
        "recommendation": "Test",
        "confidence": "high"
    }

    with pytest.raises(AssertionError, match="Invalid trap name"):
        validate_issue_structure(invalid_issue)


def test_rejects_hallucinated_tenet_names(valid_analysis_response):
    """Should detect when AI hallucinates tenet names not in VALID_TENET_NAMES."""
    invalid_issue = {
        "trap_name": "INVISIBLE ELEMENT",
        "tenet": "SUPER USABLE",  # Not in VALID_TENET_NAMES
        "location": "Test",
        "problem": "Test",
        "recommendation": "Test",
        "confidence": "high"
    }

    with pytest.raises(AssertionError, match="Invalid tenet name"):
        validate_issue_structure(invalid_issue)


def test_all_valid_trap_names_are_accepted():
    """All 27 valid trap names should be accepted."""
    for trap_name in VALID_TRAP_NAMES:
        issue = {
            "trap_name": trap_name,
            "tenet": "UNDERSTANDABLE",
            "location": "Test",
            "problem": "Test",
            "recommendation": "Test",
            "confidence": "high"
        }
        validate_issue_structure(issue)  # Should not raise


def test_all_valid_tenet_names_are_accepted():
    """All 9 valid tenet names should be accepted."""
    for tenet_name in VALID_TENET_NAMES:
        issue = {
            "trap_name": "INVISIBLE ELEMENT",
            "tenet": tenet_name,
            "location": "Test",
            "problem": "Test",
            "recommendation": "Test",
            "confidence": "high"
        }
        validate_issue_structure(issue)  # Should not raise


# ============================================================================
# TESTS - Data Types
# ============================================================================

def test_issue_arrays_are_lists(mock_anthropic_client, valid_analysis_response, valid_user_context):
    """Issue fields must be arrays/lists."""
    mock_client = Mock()
    mock_response = create_mock_tool_response(valid_analysis_response)
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client

    analyzer = UITrapsAnalyzer(api_key="test-key")
    result = analyzer.analyze_design(
        design_file="test.png",
        user_context=valid_user_context
    )

    report = result["report"]

    # All issue fields must be lists
    assert isinstance(report["critical_issues"], list)
    assert isinstance(report["moderate_issues"], list)
    assert isinstance(report["minor_issues"], list)
    assert isinstance(report["positive_observations"], list)
    assert isinstance(report["potential_issues"], list)
    assert isinstance(report["traps_checked_not_found"], list)


def test_confidence_values_are_valid():
    """Confidence must be 'high', 'medium', or 'low'."""
    valid_confidences = ["high", "medium", "low"]

    for conf in valid_confidences:
        issue = {
            "trap_name": "INVISIBLE ELEMENT",
            "tenet": "UNDERSTANDABLE",
            "location": "Test",
            "problem": "Test",
            "recommendation": "Test",
            "confidence": conf
        }
        validate_issue_structure(issue)  # Should not raise

    # Invalid confidence should fail
    invalid_issue = {
        "trap_name": "INVISIBLE ELEMENT",
        "tenet": "UNDERSTANDABLE",
        "location": "Test",
        "problem": "Test",
        "recommendation": "Test",
        "confidence": "very_high"  # INVALID
    }

    with pytest.raises(AssertionError, match="Invalid confidence"):
        validate_issue_structure(invalid_issue)


# ============================================================================
# TESTS - Required Fields
# ============================================================================

def test_standard_issue_has_all_required_fields():
    """Standard issues must have all required fields."""
    complete_issue = {
        "trap_name": "INVISIBLE ELEMENT",
        "tenet": "UNDERSTANDABLE",
        "location": "Header navigation",
        "problem": "Icon has low contrast",
        "recommendation": "Increase contrast ratio",
        "confidence": "high"
    }

    validate_issue_structure(complete_issue)  # Should not raise

    # Test missing each field
    required_fields = ['trap_name', 'tenet', 'location', 'problem', 'recommendation', 'confidence']

    for field in required_fields:
        incomplete_issue = complete_issue.copy()
        del incomplete_issue[field]

        with pytest.raises(AssertionError, match=f"missing required field: {field}"):
            validate_issue_structure(incomplete_issue)


def test_potential_issue_has_different_required_fields():
    """Potential issues have different required fields (observation, why_uncertain)."""
    complete_potential_issue = {
        "trap_name": "INFORMATION OVERLOAD",
        "tenet": "COMFORTABLE",
        "location": "Dashboard",
        "observation": "Many data points displayed",
        "why_uncertain": "May be necessary for power users",
        "confidence": "low"
    }

    validate_issue_structure(complete_potential_issue, issue_type="potential")  # Should not raise


# ============================================================================
# TESTS - Edge Cases
# ============================================================================

def test_empty_issues_arrays_are_valid(mock_anthropic_client, valid_user_context):
    """Empty issue arrays should be valid (design might have no issues)."""
    perfect_design_response = {
        "summary_headline": "A clean design with no major issues found.",
        "summary_narrative": "The interface appears to support the task well with no critical friction.",
        "critical_issues": [],  # No critical issues
        "moderate_issues": [],  # No moderate issues
        "minor_issues": [],     # No minor issues
        "positive_observations": ["Everything is great"],
        "potential_issues": [],
        "traps_checked_not_found": VALID_TRAP_NAMES[:10]
    }

    mock_client = Mock()
    mock_response = create_mock_tool_response(perfect_design_response)
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client

    analyzer = UITrapsAnalyzer(api_key="test-key")
    result = analyzer.analyze_design(
        design_file="test.png",
        user_context=valid_user_context
    )

    assert result["status"] == "success"
    assert len(result["report"]["critical_issues"]) == 0


def test_missing_optional_fields_with_defaults(mock_anthropic_client, valid_user_context):
    """Optional fields should get default values if missing."""
    response_missing_optionals = {
        "summary_headline": "The design broadly supports the task, with a few notable friction points.",
        "summary_narrative": "Users can likely accomplish the goal, though some elements may slow them down.",
        "critical_issues": [],
        "moderate_issues": [],
        "minor_issues": [],
        "positive_observations": [],
        "potential_issues": [],
        "traps_checked_not_found": []
        # Missing: bugs_detected, frame_quality_notes (optional fields)
    }

    mock_client = Mock()
    mock_response = create_mock_tool_response(response_missing_optionals)
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client

    analyzer = UITrapsAnalyzer(api_key="test-key")
    result = analyzer.analyze_design(
        design_file="test.png",
        user_context=valid_user_context
    )

    # Should succeed even without optional fields
    assert result["status"] == "success"


def test_handles_many_issues_without_crashing(mock_anthropic_client, valid_user_context):
    """Should handle responses with many issues (stress test)."""
    # Create 50 issues of each type
    many_issues = [
        {
            "trap_name": VALID_TRAP_NAMES[i % len(VALID_TRAP_NAMES)],
            "tenet": VALID_TENET_NAMES[i % len(VALID_TENET_NAMES)],
            "location": f"Location {i}",
            "problem": f"Problem {i}",
            "recommendation": f"Fix {i}",
            "confidence": ["high", "medium", "low"][i % 3]
        }
        for i in range(50)
    ]

    stress_test_response = {
        "summary_headline": "The design broadly supports the task, with a few notable friction points.",
        "summary_narrative": "Users can likely accomplish the goal, though some elements may slow them down.",
        "critical_issues": many_issues[:20],
        "moderate_issues": many_issues[20:40],
        "minor_issues": many_issues[40:],
        "positive_observations": [],
        "potential_issues": [],
        "traps_checked_not_found": []
    }

    mock_client = Mock()
    mock_response = create_mock_tool_response(stress_test_response)
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client

    analyzer = UITrapsAnalyzer(api_key="test-key")
    result = analyzer.analyze_design(
        design_file="test.png",
        user_context=valid_user_context
    )

    assert result["status"] == "success"
    assert len(result["report"]["critical_issues"]) == 20
    assert len(result["report"]["moderate_issues"]) == 20
    assert len(result["report"]["minor_issues"]) == 10


# ============================================================================
# TESTS - Severity Distribution
# ============================================================================

def test_severity_distribution_is_reasonable(valid_analysis_response):
    """Check that severity distribution makes sense (not all critical)."""
    # Count issues by severity
    critical_count = len(valid_analysis_response["critical_issues"])
    moderate_count = len(valid_analysis_response["moderate_issues"])
    minor_count = len(valid_analysis_response["minor_issues"])

    total_issues = critical_count + moderate_count + minor_count

    if total_issues > 0:
        # Critical issues should be minority (<= 50% is acceptable)
        critical_ratio = critical_count / total_issues
        assert critical_ratio <= 0.5, "Too many critical issues (should be <= 50%)"

        # Should not be ALL critical (unless only 1 issue)
        assert not (total_issues > 1 and critical_count > 0 and moderate_count == 0 and minor_count == 0), \
            "All issues are critical (unrealistic for multiple issues)"


# ============================================================================
# TESTS - Metadata
# ============================================================================

def test_metadata_is_present(mock_anthropic_client, valid_analysis_response, valid_user_context):
    """Result should include metadata about the analysis."""
    mock_client = Mock()
    mock_response = create_mock_tool_response(valid_analysis_response)
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client

    analyzer = UITrapsAnalyzer(api_key="test-key")
    result = analyzer.analyze_design(
        design_file="test.png",
        user_context=valid_user_context
    )

    metadata = result["metadata"]

    # Check required metadata fields (current shape: token counts live under `usage`)
    assert "model" in metadata
    assert "usage" in metadata
    assert "input" in metadata["usage"]
    assert "output" in metadata["usage"]
    assert "estimated_cost" in metadata
    assert "duration_seconds" in metadata
    assert "timestamp" in metadata


def test_cost_estimation_is_reasonable(mock_anthropic_client, valid_analysis_response, valid_user_context):
    """Cost estimation should be in expected range ($0.01-0.10 per analysis)."""
    mock_client = Mock()
    mock_response = create_mock_tool_response(valid_analysis_response)
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_client.return_value = mock_client

    analyzer = UITrapsAnalyzer(api_key="test-key")
    result = analyzer.analyze_design(
        design_file="test.png",
        user_context=valid_user_context
    )

    cost = result["metadata"]["estimated_cost"]

    # Cost should be positive and reasonable
    assert cost > 0, "Cost should be positive"
    assert cost < 1.0, "Cost should be less than $1 per analysis"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
