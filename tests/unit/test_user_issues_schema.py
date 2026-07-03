import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend/src'))

from schema import get_user_issues_schema, VALID_TRAP_NAMES, VALID_TENET_NAMES

def test_schema_exists():
    schema = get_user_issues_schema()
    assert schema is not None

def test_schema_required_fields():
    schema = get_user_issues_schema()
    required = schema["required"]
    assert "summary_headline" in required
    assert "summary_narrative" in required
    assert "issues" in required
    assert "positive_observations" in required
    assert "traps_checked_not_found" in required

def test_issue_item_required_fields():
    schema = get_user_issues_schema()
    issue_schema = schema["properties"]["issues"]["items"]
    required = issue_schema["required"]
    assert "headline" in required
    assert "severity" in required
    assert "confidence" in required
    assert "root_cause_trap" in required
    assert "description" in required
    assert "recommendation" in required

def test_root_cause_trap_structure():
    schema = get_user_issues_schema()
    rct = schema["properties"]["issues"]["items"]["properties"]["root_cause_trap"]
    assert "trap_name" in rct["properties"]
    assert "tenet" in rct["properties"]
    assert "definition" in rct["properties"]
    assert rct["properties"]["trap_name"]["enum"] == VALID_TRAP_NAMES


import importlib, types

def _get_prompts_module():
    """Import prompts as part of backend.src package to handle relative imports."""
    project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '../..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    import backend.src.prompts as _prompts
    return _prompts

def test_synthesis_system_prompt_exists():
    mod = _get_prompts_module()
    prompt = mod.build_synthesis_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 100
    assert "Trap" in prompt

def test_synthesis_user_message_contains_findings():
    mod = _get_prompts_module()
    mock_report = {
        "critical_issues": [],
        "moderate_issues": [
            {
                "trap_name": "GRATUITOUS REDUNDANCY",
                "tenet": "HABITUATING",
                "headline": "Two nav bars duplicate site navigation.",
                "location": "Top of page",
                "problem": "Two horizontal navigation bars appear simultaneously.",
                "recommendation": "Consolidate into one.",
                "confidence": "medium"
            }
        ],
        "minor_issues": [],
        "positive_observations": ["Clean typography"],
        "traps_checked_not_found": [{"trap_name": "DISTRACTION", "testable": True}]
    }
    msg = mod.build_synthesis_user_message(mock_report)
    assert isinstance(msg, str)
    assert "GRATUITOUS REDUNDANCY" in msg
    assert "HABITUATING" in msg
    assert "DISTRACTION" in msg

def test_synthesis_user_message_empty_report():
    mod = _get_prompts_module()
    mock_report = {
        "critical_issues": [],
        "moderate_issues": [],
        "minor_issues": [],
        "positive_observations": [],
        "traps_checked_not_found": []
    }
    msg = mod.build_synthesis_user_message(mock_report)
    assert isinstance(msg, str)
    assert len(msg) > 0

from formatters import format_issues_report_as_html

def test_format_issues_report_basic():
    mock_issues_report = {
        "summary_headline": "Navigation structure creates competing paths.",
        "summary_narrative": "Two navigation systems appear to present users with duplicate routes.",
        "issues": [
            {
                "headline": "Two separate navigation bars appear to duplicate site-level navigation.",
                "severity": "moderate",
                "confidence": "medium",
                "root_cause_trap": {
                    "trap_name": "GRATUITOUS REDUNDANCY",
                    "tenet": "HABITUATING",
                    "definition": "Multiple instances of interface elements that complete the same action are presented at the same time."
                },
                "contributing_traps": [
                    {
                        "trap_name": "AMBIGUOUS HOME",
                        "tenet": "HABITUATING",
                        "definition": "The interface presents competing locations for getting oriented."
                    }
                ],
                "description": "The page presents two horizontal navigation bars simultaneously.",
                "recommendation": "Consider consolidating into a single navigation system."
            }
        ],
        "positive_observations": ["Clean typography"],
        "traps_checked_not_found": [{"trap_name": "DISTRACTION", "testable": True}]
    }
    mock_context = {"users": "Test users", "tasks": "Test tasks", "format": "Website screenshot"}
    html = format_issues_report_as_html(mock_issues_report, mock_context)
    assert "<html" in html
    assert "GRATUITOUS REDUNDANCY" in html
    assert "AMBIGUOUS HOME" in html
    assert "root cause" in html
    assert "Two separate navigation bars" in html
    assert "Traps Not Found" in html
