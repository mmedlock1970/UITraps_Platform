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
