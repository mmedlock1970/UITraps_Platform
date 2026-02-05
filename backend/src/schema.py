"""
JSON Schema for UI Traps Analyzer structured output

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework
"""

# JSON Schema for Claude's structured output
# This ensures Claude always returns data in the exact format we expect
UI_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "array",
            "description": "5-9 bullet points summarizing overall findings. MUST be an array where each item is a complete sentence/bullet point.",
            "items": {
                "type": "string",
                "description": "A single complete bullet point (complete sentence)"
            },
            "minItems": 5,
            "maxItems": 9
        },
        "critical_issues": {
            "type": "array",
            "description": "Critical severity issues that block core user tasks",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {
                        "type": "string",
                        "description": "Name of the trap in ALL CAPS (e.g., INVISIBLE ELEMENT)"
                    },
                    "tenet": {
                        "type": "string",
                        "description": "Parent tenet violated (e.g., UNDERSTANDABLE, COMFORTABLE)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Specific location in the design where trap occurs"
                    },
                    "problem": {
                        "type": "string",
                        "description": "Detailed explanation of why the trap is present"
                    },
                    "recommendation": {
                        "type": "string",
                        "description": "How to fix the issue"
                    },
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Confidence level in this finding"
                    }
                },
                "required": ["trap_name", "tenet", "location", "problem", "recommendation", "confidence"]
            }
        },
        "moderate_issues": {
            "type": "array",
            "description": "Moderate severity issues that slow tasks or cause frustration",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {"type": "string"},
                    "tenet": {"type": "string"},
                    "location": {"type": "string"},
                    "problem": {"type": "string"},
                    "recommendation": {"type": "string"},
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"]
                    }
                },
                "required": ["trap_name", "tenet", "location", "problem", "recommendation", "confidence"]
            }
        },
        "minor_issues": {
            "type": "array",
            "description": "Minor severity issues like aesthetic problems or small inefficiencies",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {"type": "string"},
                    "tenet": {"type": "string"},
                    "location": {"type": "string"},
                    "problem": {"type": "string"},
                    "recommendation": {"type": "string"},
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"]
                    }
                },
                "required": ["trap_name", "tenet", "location", "problem", "recommendation", "confidence"]
            }
        },
        "positive_observations": {
            "type": "array",
            "description": "What the design does well",
            "items": {
                "type": "string"
            }
        },
        "potential_issues": {
            "type": "array",
            "description": "Borderline issues that might be traps but require human judgment. Use for cases where you observe something potentially problematic but lack context to definitively classify it. Examples: INFORMATION OVERLOAD where content might be necessary, GRATUITOUS REDUNDANCY that might be intentional flexibility.",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {"type": "string", "description": "Potential trap name in ALL CAPS"},
                    "tenet": {"type": "string", "description": "Tenet that might be violated"},
                    "location": {"type": "string", "description": "Where the potential issue appears"},
                    "observation": {"type": "string", "description": "What you observe that might be problematic"},
                    "why_uncertain": {"type": "string", "description": "Why this needs human review - what context is missing"},
                    "confidence": {"type": "string", "enum": ["low"], "description": "Always 'low'"}
                },
                "required": ["trap_name", "tenet", "location", "observation", "why_uncertain", "confidence"]
            }
        },
        "traps_checked_not_found": {
            "type": "array",
            "description": "List of trap names that were checked but not found",
            "items": {
                "type": "string"
            }
        },
        "bugs_detected": {
            "type": "array",
            "description": "Technical bugs or broken states observed (not UI Traps, but system failures). Use for: blank screens that shouldn't be blank, broken layouts, missing content that should exist, partially loaded states, error states, or technical failures distinct from usability issues.",
            "items": {
                "type": "object",
                "properties": {
                    "bug_type": {
                        "type": "string",
                        "enum": ["blank_screen", "broken_layout", "missing_content", "partial_load", "error_state", "technical_failure"],
                        "description": "Type of bug detected"
                    },
                    "location": {
                        "type": "string",
                        "description": "Where the bug appears"
                    },
                    "description": {
                        "type": "string",
                        "description": "What appears to be wrong or broken"
                    },
                    "possible_cause": {
                        "type": "string",
                        "description": "Best guess at what might be causing this (loading state, error, missing data, etc.)"
                    },
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Confidence this is actually a bug vs intentional state"
                    }
                },
                "required": ["bug_type", "location", "description", "confidence"]
            }
        },
        "frame_quality_notes": {
            "type": "array",
            "description": "Notes about frame quality issues that may affect analysis accuracy (for video/multi-image). Examples: mid-transition frames, partial scrolls, loading states, duplicate frames.",
            "items": {
                "type": "object",
                "properties": {
                    "frame_index": {
                        "type": "integer",
                        "description": "Which frame this note applies to (1-indexed)"
                    },
                    "issue": {
                        "type": "string",
                        "enum": ["mid_transition", "partial_scroll", "loading_state", "blank_screen", "duplicate", "low_quality", "incomplete_ui"],
                        "description": "Type of frame quality issue"
                    },
                    "description": {
                        "type": "string",
                        "description": "Details about the issue"
                    },
                    "should_skip": {
                        "type": "boolean",
                        "description": "Whether this frame should be excluded from analysis"
                    }
                },
                "required": ["frame_index", "issue", "description", "should_skip"]
            }
        }
    },
    "required": [
        "summary",
        "critical_issues",
        "moderate_issues",
        "minor_issues",
        "positive_observations",
        "potential_issues",
        "traps_checked_not_found"
    ],
    "additionalProperties": False
}


def get_ui_analysis_schema():
    """
    Get the JSON schema for UI analysis structured output.

    Returns:
        Dictionary containing the JSON schema
    """
    return UI_ANALYSIS_SCHEMA
