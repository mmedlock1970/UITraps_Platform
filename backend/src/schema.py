"""
JSON Schema for UI Traps Analyzer structured output

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework
"""

# The 27 valid UI Trap names - ONLY these are allowed
VALID_TRAP_NAMES = [
    "INVISIBLE ELEMENT",
    "EFFECTIVELY INVISIBLE ELEMENT",
    "DISTRACTION",
    "UNCOMPREHENDED ELEMENT",
    "INVITING DEAD END",
    "POOR GROUPING",
    "FORCED SYNTAX",
    "MEMORY CHALLENGE",
    "FEEDBACK FAILURE",
    "PHYSICAL CHALLENGE",
    "ACCIDENTAL ACTIVATION",
    "SLOW OR NO RESPONSE",
    "CAPTIVE WAIT",
    "UNNECESSARY STEP",
    "INFORMATION OVERLOAD",
    "SYSTEM AMNESIA",
    "BAD PREDICTION",
    "INCORRECT INFO",
    "IRREVERSIBLE ACTION",
    "UNWANTED DISCLOSURE",
    "DATA LOSS",
    "GRATUITOUS REDUNDANCY",
    "VARIABLE OUTCOME",
    "WANDERING ELEMENT",
    "INCONSISTENT APPEARANCE",
    "AMBIGUOUS HOME",
    "POOR AESTHETIC",
]

# The 9 valid UI Tenet names
VALID_TENET_NAMES = [
    "UNDERSTANDABLE",
    "COMFORTABLE",
    "RESPONSIVE",
    "EFFICIENT",
    "ACCURATE",
    "FORGIVING",
    "PROTECTIVE",
    "HABITUATING",
    "BEAUTIFUL",
]

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
                        "enum": VALID_TRAP_NAMES,
                        "description": "Name of the trap - MUST be one of the 27 valid trap names"
                    },
                    "tenet": {
                        "type": "string",
                        "enum": VALID_TENET_NAMES,
                        "description": "Parent tenet violated - MUST be one of the 9 valid tenets"
                    },
                    "location": {
                        "type": "string",
                        "description": "Specific location in the design where trap occurs"
                    },
                    "problem": {
                        "type": "string",
                        "description": "Human-readable explanation for end users. Describe the specific UI element causing the issue and how it impacts the user experience. Do NOT include internal reasoning steps, gate numbers, or analytical framework terminology. Write as if explaining to a client who has never heard of UI Traps methodology."
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
                    "trap_name": {"type": "string", "enum": VALID_TRAP_NAMES},
                    "tenet": {"type": "string", "enum": VALID_TENET_NAMES},
                    "location": {"type": "string"},
                    "problem": {"type": "string", "description": "Human-readable explanation for end users. Describe the issue and its impact without internal reasoning steps or framework terminology."},
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
                    "trap_name": {"type": "string", "enum": VALID_TRAP_NAMES},
                    "tenet": {"type": "string", "enum": VALID_TENET_NAMES},
                    "location": {"type": "string"},
                    "problem": {"type": "string", "description": "Human-readable explanation for end users. Describe the issue and its impact without internal reasoning steps or framework terminology."},
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
                    "trap_name": {"type": "string", "enum": VALID_TRAP_NAMES, "description": "Potential trap name - MUST be one of the 27 valid trap names"},
                    "tenet": {"type": "string", "enum": VALID_TENET_NAMES, "description": "Tenet that might be violated - MUST be one of the 9 valid tenets"},
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
        },
        "flagged_for_human_review": {
            "type": "array",
            "description": "Tier 3 traps that require human judgment to confirm. These traps depend on understanding user conventions, expectations, or taste that AI cannot reliably assess. A human reviewer must verify whether these are actual issues for the target users.",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {
                        "type": "string",
                        "enum": ["UNCOMPREHENDED ELEMENT", "INVITING DEAD END", "DISTRACTION", "EFFECTIVELY INVISIBLE ELEMENT", "POOR AESTHETIC"],
                        "description": "The trap being flagged - limited to Tier 3 traps requiring human judgment"
                    },
                    "tenet": {
                        "type": "string",
                        "enum": VALID_TENET_NAMES,
                        "description": "Parent tenet that might be violated"
                    },
                    "location": {
                        "type": "string",
                        "description": "Where in the design this was observed"
                    },
                    "observation": {
                        "type": "string",
                        "description": "Factual description of what the AI observes - no assumptions about user confusion"
                    },
                    "why_human_review_needed": {
                        "type": "string",
                        "description": "Why AI cannot determine if this is a real issue - what human knowledge is needed"
                    },
                    "question_for_reviewer": {
                        "type": "string",
                        "description": "Specific question the human reviewer should answer to confirm/reject this finding"
                    }
                },
                "required": ["trap_name", "tenet", "location", "observation", "why_human_review_needed", "question_for_reviewer"]
            }
        },
        "incomplete_flow_findings": {
            "type": "array",
            "description": "Tier 2 traps that AI can assess but require complete task flows. These findings are flagged with caveats because screenshots may be missing intermediate steps. AI can detect these traps but confidence is limited without seeing the full user journey.",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {
                        "type": "string",
                        "enum": ["UNNECESSARY STEP", "FORCED SYNTAX", "GRATUITOUS REDUNDANCY", "MEMORY CHALLENGE", "SYSTEM AMNESIA", "VARIABLE OUTCOME"],
                        "description": "The trap being flagged - limited to Tier 2 traps requiring complete flows"
                    },
                    "tenet": {
                        "type": "string",
                        "enum": VALID_TENET_NAMES,
                        "description": "Parent tenet that might be violated"
                    },
                    "location": {
                        "type": "string",
                        "description": "Where in the design this was observed"
                    },
                    "observation": {
                        "type": "string",
                        "description": "What was observed in the provided screenshots"
                    },
                    "caveat": {
                        "type": "string",
                        "description": "Why this finding may be incomplete - what additional context might change the assessment"
                    },
                    "additional_screenshots_needed": {
                        "type": "string",
                        "description": "What additional screenshots would help confirm this finding"
                    },
                    "confidence": {
                        "type": "string",
                        "enum": ["medium", "low"],
                        "description": "Confidence level - typically medium or low for incomplete flow findings"
                    }
                },
                "required": ["trap_name", "tenet", "location", "observation", "caveat", "confidence"]
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


# Interaction Analysis Schema
# Used for analyzing individual interaction sequences (hover, click, form, scroll, responsive)
INTERACTION_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "interaction_type": {
            "type": "string",
            "enum": ["hover", "click", "form", "scroll", "responsive"],
            "description": "Type of interaction analyzed"
        },
        "element_analyzed": {
            "type": "string",
            "description": "Description of the element or area analyzed"
        },
        "feedback_quality": {
            "type": "object",
            "description": "Assessment of visual feedback quality",
            "properties": {
                "has_visual_feedback": {
                    "type": "boolean",
                    "description": "Whether any visual feedback is provided"
                },
                "feedback_timing": {
                    "type": "string",
                    "enum": ["immediate", "delayed", "none"],
                    "description": "How quickly feedback appears"
                },
                "feedback_clarity": {
                    "type": "string",
                    "enum": ["clear", "subtle", "confusing", "none"],
                    "description": "How clear/noticeable the feedback is"
                },
                "feedback_description": {
                    "type": "string",
                    "description": "Description of what feedback is provided (or missing)"
                }
            },
            "required": ["has_visual_feedback", "feedback_timing", "feedback_clarity"]
        },
        "state_transition": {
            "type": "object",
            "description": "Assessment of state changes during interaction",
            "properties": {
                "is_predictable": {
                    "type": "boolean",
                    "description": "Whether the resulting state is what a user would expect"
                },
                "is_reversible": {
                    "type": "boolean",
                    "description": "Whether the user can undo or go back"
                },
                "maintains_context": {
                    "type": "boolean",
                    "description": "Whether the user's mental model/context is preserved"
                },
                "transition_description": {
                    "type": "string",
                    "description": "Description of the state transition observed"
                }
            },
            "required": ["is_predictable", "is_reversible", "maintains_context"]
        },
        "traps_detected": {
            "type": "array",
            "description": "UI Traps identified in this interaction",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {
                        "type": "string",
                        "enum": VALID_TRAP_NAMES,
                        "description": "Name of the trap - MUST be one of the 27 valid trap names"
                    },
                    "tenet": {
                        "type": "string",
                        "enum": VALID_TENET_NAMES,
                        "description": "Parent tenet violated - MUST be one of the 9 valid tenets"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "moderate", "minor"],
                        "description": "Severity of this issue"
                    },
                    "observation": {
                        "type": "string",
                        "description": "What was observed in the interaction sequence"
                    },
                    "screenshot_evidence": {
                        "type": "string",
                        "description": "Which screenshots show the issue (e.g., 'visible in before_click vs after_click')"
                    },
                    "recommendation": {
                        "type": "string",
                        "description": "How to fix this issue"
                    },
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Confidence level in this finding"
                    }
                },
                "required": ["trap_name", "severity", "observation", "recommendation", "confidence"]
            }
        },
        "accessibility_concerns": {
            "type": "array",
            "description": "Accessibility issues related to this interaction",
            "items": {
                "type": "object",
                "properties": {
                    "concern": {
                        "type": "string",
                        "description": "Description of the accessibility concern"
                    },
                    "affected_users": {
                        "type": "string",
                        "description": "Who would be affected (e.g., 'keyboard users', 'screen reader users', 'users with motor impairments')"
                    },
                    "recommendation": {
                        "type": "string",
                        "description": "How to address this concern"
                    }
                },
                "required": ["concern", "affected_users", "recommendation"]
            }
        },
        "positive_observations": {
            "type": "array",
            "description": "What works well in this interaction",
            "items": {
                "type": "string"
            }
        },
        "overall_assessment": {
            "type": "string",
            "enum": ["good", "acceptable", "needs_improvement", "poor"],
            "description": "Overall quality rating for this interaction"
        },
        "summary": {
            "type": "string",
            "description": "Brief summary of findings for this interaction (1-2 sentences)"
        }
    },
    "required": [
        "interaction_type",
        "element_analyzed",
        "feedback_quality",
        "state_transition",
        "traps_detected",
        "accessibility_concerns",
        "positive_observations",
        "overall_assessment",
        "summary"
    ],
    "additionalProperties": False
}


def get_interaction_analysis_schema():
    """
    Get the JSON schema for interaction analysis structured output.

    Returns:
        Dictionary containing the JSON schema
    """
    return INTERACTION_ANALYSIS_SCHEMA


# Interaction Summary Schema
# Used for aggregating multiple interaction analyses into a summary
INTERACTION_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_interaction_quality": {
            "type": "string",
            "enum": ["excellent", "good", "acceptable", "needs_improvement", "poor"],
            "description": "Overall assessment of interaction quality across all tested interactions"
        },
        "total_interactions_analyzed": {
            "type": "integer",
            "description": "Number of interactions analyzed"
        },
        "summary_by_type": {
            "type": "object",
            "description": "Summary for each interaction type",
            "properties": {
                "hover": {
                    "type": "object",
                    "properties": {
                        "analyzed_count": {"type": "integer"},
                        "issues_found": {"type": "integer"},
                        "assessment": {"type": "string", "enum": ["good", "acceptable", "needs_improvement", "poor", "not_tested"]}
                    }
                },
                "click": {
                    "type": "object",
                    "properties": {
                        "analyzed_count": {"type": "integer"},
                        "issues_found": {"type": "integer"},
                        "assessment": {"type": "string", "enum": ["good", "acceptable", "needs_improvement", "poor", "not_tested"]}
                    }
                },
                "form": {
                    "type": "object",
                    "properties": {
                        "analyzed_count": {"type": "integer"},
                        "issues_found": {"type": "integer"},
                        "assessment": {"type": "string", "enum": ["good", "acceptable", "needs_improvement", "poor", "not_tested"]}
                    }
                },
                "scroll": {
                    "type": "object",
                    "properties": {
                        "analyzed_count": {"type": "integer"},
                        "issues_found": {"type": "integer"},
                        "assessment": {"type": "string", "enum": ["good", "acceptable", "needs_improvement", "poor", "not_tested"]}
                    }
                },
                "responsive": {
                    "type": "object",
                    "properties": {
                        "analyzed_count": {"type": "integer"},
                        "issues_found": {"type": "integer"},
                        "assessment": {"type": "string", "enum": ["good", "acceptable", "needs_improvement", "poor", "not_tested"]}
                    }
                }
            }
        },
        "critical_findings": {
            "type": "array",
            "description": "Most important issues found across all interactions",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {"type": "string", "enum": VALID_TRAP_NAMES},
                    "severity": {"type": "string", "enum": ["critical", "moderate", "minor"]},
                    "interaction_type": {"type": "string"},
                    "element": {"type": "string"},
                    "summary": {"type": "string"},
                    "recommendation": {"type": "string"}
                },
                "required": ["trap_name", "severity", "summary", "recommendation"]
            }
        },
        "patterns_observed": {
            "type": "array",
            "description": "Patterns seen across multiple interactions (good or bad)",
            "items": {
                "type": "string"
            }
        },
        "prioritized_recommendations": {
            "type": "array",
            "description": "Recommendations ordered by impact",
            "items": {
                "type": "object",
                "properties": {
                    "priority": {"type": "integer", "minimum": 1},
                    "recommendation": {"type": "string"},
                    "impact": {"type": "string", "description": "Expected impact if fixed"},
                    "effort": {"type": "string", "enum": ["low", "medium", "high"], "description": "Estimated effort to implement"}
                },
                "required": ["priority", "recommendation", "impact", "effort"]
            }
        },
        "executive_summary": {
            "type": "string",
            "description": "2-3 sentence summary of interaction quality for stakeholders"
        }
    },
    "required": [
        "overall_interaction_quality",
        "total_interactions_analyzed",
        "summary_by_type",
        "critical_findings",
        "patterns_observed",
        "prioritized_recommendations",
        "executive_summary"
    ],
    "additionalProperties": False
}


def get_interaction_summary_schema():
    """
    Get the JSON schema for interaction summary structured output.

    Returns:
        Dictionary containing the JSON schema
    """
    return INTERACTION_SUMMARY_SCHEMA
