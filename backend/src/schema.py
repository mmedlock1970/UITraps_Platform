"""
JSON Schema for UI Traps Analyzer structured output

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework
"""
import copy

# KB generations that carry all evaluative logic in the KB file itself and use the
# new output vocabulary (Severity & Confidence: High/Medium/Low; G4 coverage labels;
# G8 report sections). The legacy v1/v2 path is unchanged.
NEW_KB_VERSIONS = frozenset({"v1.1", "v2.1"})


def is_new_kb(version: str | None) -> bool:
    """True when the selected KB carries the new (v2.1-lineage) output vocabulary."""
    return version in NEW_KB_VERSIONS


# New-KB output vocabulary (see trap_kb_v2.1.md §SEVERITY & CONFIDENCE and G4/G8)
NEW_KB_CONFIDENCE_LEVELS = ["High", "Medium", "Low"]
NEW_KB_SEVERITY_LABELS = ["High", "Medium", "Low"]
NEW_KB_COVERAGE_STATUSES = [
    "not_present", "not_assessable_artifact", "not_assessable_context",
    # J27 scoped coverage: a trap with a declared artifact-inaccessible sub-domain (e.g.
    # Physical Challenge, Slow or No Response, Invisible Element) — assessed in part, not in
    # full. May co-exist with the trap also appearing as an Issue (mutual-exclusivity relaxed).
    "partially_assessed",
]

# G3 issue-composition — the per-Trap `relationship` marker the model emits (bracketed
# values verbatim from the KB's G3 block). Rendering maps these to three layouts:
# single-trap (none / root_cause / conditional — primary), multi-trap co-occurring, and
# multi-trap conditional — enumerated; a `consequence` trap is folded into prose, not shown.
NEW_KB_RELATIONSHIP_VALUES = [
    "none", "root_cause", "consequence", "co-occurring",
    "conditional — primary", "conditional — enumerated",
]

# Canonical snake_case token per relationship, for tolerant rendering (the model may vary
# hyphen/en-dash/em-dash/spacing on the multi-word values).
_RELATIONSHIP_CANON = {
    "none": "none", "root_cause": "root_cause", "rootcause": "root_cause",
    "consequence": "consequence", "co_occurring": "co_occurring", "cooccurring": "co_occurring",
    "conditional_primary": "conditional_primary", "conditional_enumerated": "conditional_enumerated",
}


def normalize_relationship(value: str | None) -> str:
    """Map a G3 relationship marker (any hyphen/dash/spacing variant) to a canonical token."""
    import re as _re
    key = _re.sub(r"_+", "_", _re.sub(r"[^a-z]+", "_", (value or "").lower())).strip("_")
    return _RELATIONSHIP_CANON.get(key, "none")

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
    "UNNECESSARY STEP(S)",
    "INFORMATION OVERLOAD",
    "SYSTEM AMNESIA",
    "BAD PREDICTION",
    "INCORRECT INFORMATION",
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

# v1 lineage (v1 / v1.1) carries 26 traps: UNNECESSARY STEP (no "(S)"), UNATTRACTIVE
# APPEARANCE (not POOR AESTHETIC), and no INCORRECT INFORMATION. Used to make the new-KB
# schema's trap-name enum version-aware so v1.1 adjudication isn't validated against v2 names.
VALID_TRAP_NAMES_V1 = [
    {"UNNECESSARY STEP(S)": "UNNECESSARY STEP", "POOR AESTHETIC": "UNATTRACTIVE APPEARANCE"}.get(_n, _n)
    for _n in VALID_TRAP_NAMES if _n != "INCORRECT INFORMATION"
]


def _valid_trap_names(version: str | None) -> list:
    """The canonical trap-name set for a version's lineage (26 for v1/v1.1, 27 for v2/v2.1)."""
    return VALID_TRAP_NAMES_V1 if version in ("v1", "v1.1") else VALID_TRAP_NAMES

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
        "summary_headline": {
            "type": "string",
            "description": "One sentence capturing the most significant finding in relation to the user's stated goals. Tie it to the specific tasks and users provided — not generic. Use measured language: 'appears to', 'may affect', 'could prevent'. Example: 'Several usability issues appear to complicate the path to checkout for first-time buyers, with the most significant concerns clustering around navigation and feedback.' Do NOT write a count."
        },
        "summary_narrative": {
            "type": "string",
            "description": "A single paragraph (3-5 sentences) elaborating on overall findings — patterns observed, tenets most affected, notable context. Written for a reader who has not yet seen the detailed findings. Use measured, hedged language throughout: 'appears to', 'may', 'seems likely', 'could'. Do NOT use absolutist language like 'users cannot' or 'the design fails'."
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
                    "headline": {
                        "type": "string",
                        "description": "One sentence describing how this trap appears to manifest in this specific design and how it may affect the user. Write from the user's perspective, tied to the context and tasks provided. Use measured language: 'appears to', 'may cause', 'could prevent'. Example: 'Dense promotional content between the size selector and checkout button may require users to scroll past irrelevant material to complete their purchase.'"
                    },
                    "location": {
                        "type": "string",
                        "description": "Specific location in the design where trap occurs"
                    },
                    "problem": {
                        "type": "string",
                        "description": "2-3 sentences elaborating on the headline and the reasoning used to conclude this trap appears present. Include what was observed and why it suggests this trap. Write for a reader unfamiliar with UI Traps methodology. Use measured language: 'appears to', 'seems likely', 'may'. Do NOT include gate numbers or internal reasoning labels."
                    },
                    "recommendation": {
                        "type": "string",
                        "description": "2-3 sentences suggesting how this trap might be addressed. Use measured, advisory language: 'one approach would be', 'consider', 'it may help to'. Do NOT use imperative commands like 'you must' or 'fix by'."
                    },
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Confidence level in this finding"
                    },
                    "task": {
                        "type": "string",
                        "description": (
                            "Task this finding most directly relates to. "
                            "Set to the exact task name from the WHAT IS THE TASK BEING EVALUATED section, "
                            "or 'general' if the issue applies across all tasks or is not task-specific. "
                            "Omit when only one task is defined."
                        )
                    },
                    "region": {
                        "type": "object",
                        "description": "Bounding box tightly enclosing the specific element (button, label, icon, text, card) that exhibits this trap — not the section, container, or page area around it. Normalized coordinates 0.0–1.0, origin top-left. The crop must show the problematic element itself. Omit if the crop would not add visual evidence (e.g., finding is about an absence on a screen not provided, or no specific element can be bounded). When including, also provide a caption explaining what the crop shows and how it illustrates this finding.",
                        "properties": {
                            "x": {"type": "number", "description": "Left edge (0.0 = left side, 1.0 = right side)"},
                            "y": {"type": "number", "description": "Top edge (0.0 = top, 1.0 = bottom)"},
                            "width": {"type": "number", "description": "Width as a fraction of image width"},
                            "height": {"type": "number", "description": "Height as a fraction of image height"},
                            "caption": {"type": "string", "description": "Describes (1) what the cropped area shows and (2) how what is shown illustrates this finding. Required when region is provided."}
                        },
                        "required": ["x", "y", "width", "height"]
                    }
                },
                "required": ["trap_name", "tenet", "headline", "location", "problem", "recommendation", "confidence"]
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
                    "headline": {
                        "type": "string",
                        "description": "One sentence describing how this trap appears to manifest in this specific design and how it may affect the user. Use measured language: 'appears to', 'may cause', 'could prevent'."
                    },
                    "location": {"type": "string"},
                    "problem": {"type": "string", "description": "2-3 sentences elaborating on the headline and the reasoning used to conclude this trap appears present. Use measured language. Do NOT include internal reasoning steps or framework terminology."},
                    "recommendation": {"type": "string", "description": "2-3 sentences suggesting how this trap might be addressed. Use advisory language: 'one approach would be', 'consider', 'it may help to'."},
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"]
                    },
                    "task": {
                        "type": "string",
                        "description": (
                            "Task this finding most directly relates to. "
                            "Set to the exact task name from the WHAT IS THE TASK BEING EVALUATED section, "
                            "or 'general' if the issue applies across all tasks or is not task-specific. "
                            "Omit when only one task is defined."
                        )
                    },
                    "region": {
                        "type": "object",
                        "description": "Bounding box tightly enclosing the specific element (button, label, icon, text, card) that exhibits this trap — not the section, container, or page area around it. Normalized coordinates 0.0–1.0, origin top-left. The crop must show the problematic element itself. Omit if the crop would not add visual evidence (e.g., finding is about an absence on a screen not provided, or no specific element can be bounded). When including, also provide a caption explaining what the crop shows and how it illustrates this finding.",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "width": {"type": "number"},
                            "height": {"type": "number"},
                            "caption": {"type": "string", "description": "Describes (1) what the cropped area shows and (2) how what is shown illustrates this finding. Required when region is provided."}
                        },
                        "required": ["x", "y", "width", "height"]
                    }
                },
                "required": ["trap_name", "tenet", "headline", "location", "problem", "recommendation", "confidence"]
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
                    "headline": {
                        "type": "string",
                        "description": "One sentence describing how this trap appears to manifest in this specific design and how it may affect the user. Use measured language: 'appears to', 'may cause', 'could prevent'."
                    },
                    "location": {"type": "string"},
                    "problem": {"type": "string", "description": "2-3 sentences elaborating on the headline and the reasoning used to conclude this trap appears present. Use measured language. Do NOT include internal reasoning steps or framework terminology."},
                    "recommendation": {"type": "string", "description": "2-3 sentences suggesting how this trap might be addressed. Use advisory language: 'one approach would be', 'consider', 'it may help to'."},
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"]
                    },
                    "task": {
                        "type": "string",
                        "description": (
                            "Task this finding most directly relates to. "
                            "Set to the exact task name from the WHAT IS THE TASK BEING EVALUATED section, "
                            "or 'general' if the issue applies across all tasks or is not task-specific. "
                            "Omit when only one task is defined."
                        )
                    },
                    "region": {
                        "type": "object",
                        "description": "Bounding box tightly enclosing the specific element (button, label, icon, text, card) that exhibits this trap — not the section, container, or page area around it. Normalized coordinates 0.0–1.0, origin top-left. The crop must show the problematic element itself. Omit if the crop would not add visual evidence (e.g., finding is about an absence on a screen not provided, or no specific element can be bounded). When including, also provide a caption explaining what the crop shows and how it illustrates this finding.",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "width": {"type": "number"},
                            "height": {"type": "number"},
                            "caption": {"type": "string", "description": "Describes (1) what the cropped area shows and (2) how what is shown illustrates this finding. Required when region is provided."}
                        },
                        "required": ["x", "y", "width", "height"]
                    }
                },
                "required": ["trap_name", "tenet", "headline", "location", "problem", "recommendation", "confidence"]
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
            "description": (
                "Traps you actually evaluated, not flagged as confirmed issues. "
                "Include ONLY: (1) always-evaluable traps not found, with testable:true; "
                "(2) conditional traps where you applied the rule and have a result to report. "
                "Do NOT include SLOW OR NO RESPONSE or POOR AESTHETIC — added automatically. "
                "Do NOT enumerate traps you did not evaluate."
            ),
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {
                        "type": "string",
                        "description": "Name of the trap"
                    },
                    "testable": {
                        "type": "boolean",
                        "description": (
                            "True if you evaluated this trap and confirmed it is NOT present. "
                            "False if you lacked the information needed to make a judgment "
                            "(e.g. requires multiple screens, interaction testing, session data)."
                        )
                    },
                },
                "required": ["trap_name", "testable"]
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
        "summary_headline",
        "summary_narrative",
        "critical_issues",
        "moderate_issues",
        "minor_issues",
        "positive_observations",
        "potential_issues",
        "traps_checked_not_found"
    ],
    "additionalProperties": False
}


def _new_kb_analysis_schema(version: str = "v2.1"):
    """
    Derive the analysis schema for new-KB (v2.1-lineage) versions from the legacy
    schema. Only the vocabulary changes — field names and array structure are
    preserved so the whole downstream pipeline (enrichment, crops, formatter,
    front end) keeps working:

    - confidence enum → High / Medium / Low
    - each issue gains an optional `severity_label` (High/Medium/Low ladder)
    - `traps_checked_not_found` items carry a G4 `coverage_status` label instead of
      the legacy `testable` boolean
    - the tier-specific `flagged_for_human_review` / `incomplete_flow_findings`
      buckets are dropped (they have no G8 home; uncertain findings route to
      `potential_issues` = "Worth a closer look")
    """
    schema = copy.deepcopy(UI_ANALYSIS_SCHEMA)
    props = schema["properties"]
    trap_names = _valid_trap_names(version)

    for sev in ("critical_issues", "moderate_issues", "minor_issues"):
        item = props[sev]["items"]
        item_props = item["properties"]
        # Version-aware trap-name enum — v1.1 must validate against the 26-name v1 set, not v2's 27.
        if "trap_name" in item_props and "enum" in item_props["trap_name"]:
            item_props["trap_name"]["enum"] = trap_names
        # severity_label is required — an omitted label silently miscounts the scorecard
        # (a High finding falls back to Medium). The system prompt already asks for it.
        if "severity_label" not in item.get("required", []):
            item.setdefault("required", []).append("severity_label")
        item_props["confidence"] = {
            "type": "string",
            "enum": NEW_KB_CONFIDENCE_LEVELS,
            "description": (
                "Confidence this issue is real: High (directly evidenced), "
                "Medium (strong evidence; a named check would settle it), or Low "
                "(partial evidence, or leaning on a declared default). "
                "State the promotion path for every non-High finding."
            ),
        }
        item_props["severity_label"] = {
            "type": "string",
            "enum": NEW_KB_SEVERITY_LABELS,
            "description": (
                "Severity ladder level — the worst plausible outcome for the stated goals: "
                "High (task failure or irreversible harm), Medium (recoverable failure or "
                "recurring friction), Low (one-time friction, delay, polish). Populate this "
                "AND place the issue in the array indicated by the system prompt's severity mapping."
            ),
        }

    tcnf = props["traps_checked_not_found"]
    tcnf["description"] = (
        "Coverage notes (G8 section 3): traps assessed and not present (with the condition "
        "that ruled them out), and traps not assessable (with what would settle them). "
        "Never include a trap reported as an issue."
    )
    tcnf["items"]["properties"] = {
        "trap_name": {"type": "string", "description": "Name of the trap"},
        "coverage_status": {
            "type": "string",
            "enum": NEW_KB_COVERAGE_STATUSES,
            "description": (
                "G4 label. not_present: the artifact can show this trap, required context is "
                "available or a declared default covers it, the detection procedure ran, and "
                "nothing survived. not_assessable_artifact: 'Not assessable from this artifact'. "
                "not_assessable_context: 'Not assessable without user context'. partially_assessed: "
                "J27 scoped coverage — assessable in part but not in full (declared artifact-"
                "inaccessible sub-domain); emit even when the trap is also reported as an Issue."
            ),
        },
        "detail": {
            "type": "string",
            "description": (
                "MANDATORY G6 evidence, one line. not_present → either "
                "'procedure run against [scope], no triggering conditions' or "
                "'disconfirmed: [named observation]'. not_assessable_artifact → the artifact "
                "that would settle it. not_assessable_context → which C1–C4 context field "
                "would settle it. partially_assessed → 'assessed within scope: [...]; not "
                "assessable from this artifact: [...] — [what would settle]'. A bare trap name "
                "with no evidence is not a valid entry."
            ),
        },
    }
    tcnf["items"]["required"] = ["trap_name", "coverage_status", "detail"]

    # "Worth a closer look" (G8 §2): pivotal, assessability-blocked unknowns — questions,
    # not findings. Replace the legacy potential_issues shape with the richer entry the KB
    # requested (why-it-matters / the check + cost / both-way implications; no confidence).
    potential = props["potential_issues"]
    potential["description"] = (
        "Worth a closer look (G8 section 2): pivotal unknowns that cannot be settled from this "
        "artifact but would change the picture if real. Entry ticket is a hard AND: pivotal to a "
        "stated goal, the worst branch clears Medium severity, and a specific named check exists. "
        "These are questions, not findings — anything whose evidence clears its Trap's bar is an "
        "Issue instead."
    )
    potential["items"]["properties"] = {
        "trap_name": {"type": "string", "enum": trap_names, "description": "The trap this unknown concerns."},
        "tenet": {"type": "string", "enum": VALID_TENET_NAMES},
        "location": {"type": "string", "description": "The element/screen the unknown concerns."},
        "observation": {"type": "string", "description": "What is factually visible that raises the question."},
        "why_it_matters": {"type": "string", "description": "Why this is pivotal to the stated goal (entry-ticket gate a)."},
        "why_uncertain": {"type": "string", "description": "What specifically cannot be determined from this artifact."},
        "check": {"type": "string", "description": "The specific named check that would settle it (entry-ticket gate c)."},
        "check_cost": {"type": "string", "description": "Cost of that check, e.g. 'one click', 'five-user test', 'code audit'."},
        "implication_if_confirmed": {"type": "string", "description": "What it means for the user if the check confirms the problem."},
        "implication_if_ruled_out": {"type": "string", "description": "What it means if the check rules it out (often itself a live trap)."},
    }
    potential["items"]["required"] = [
        "trap_name", "tenet", "location", "observation", "why_it_matters", "check", "check_cost",
    ]

    # Drop tier-specific buckets that have no place in the G8 report structure.
    for legacy_field in ("flagged_for_human_review", "incomplete_flow_findings"):
        props.pop(legacy_field, None)

    return schema


# Cache the derived new-KB schema PER LINEAGE — v1.1 (26 traps) and v2.1 (27 traps) differ.
_NEW_KB_ANALYSIS_SCHEMA_CACHE: dict = {}


def get_ui_analysis_schema(version: str = "v2"):
    """
    Get the JSON schema for UI analysis structured output.

    Args:
        version: KB version. New-KB versions (v1.1/v2.1) get the remapped
            vocabulary with a version-aware trap-name enum; others get the legacy schema.

    Returns:
        Dictionary containing the JSON schema
    """
    if not is_new_kb(version):
        return UI_ANALYSIS_SCHEMA
    lineage = "v1" if version in ("v1", "v1.1") else "v2"
    cached = _NEW_KB_ANALYSIS_SCHEMA_CACHE.get(lineage)
    if cached is None:
        cached = _NEW_KB_ANALYSIS_SCHEMA_CACHE[lineage] = _new_kb_analysis_schema(version)
    return cached


# Schema for Pass 3 user-issues synthesis output
USER_ISSUES_SCHEMA = {
    "type": "object",
    "properties": {
        "summary_headline": {
            "type": "string",
            "description": "One sentence capturing the most significant user-facing issue. Use measured language: 'appears to', 'may affect'. Do NOT write a count."
        },
        "summary_narrative": {
            "type": "string",
            "description": "A single paragraph (3-5 sentences) summarising the overall picture for a reader who has not yet seen the findings. Use hedged language throughout."
        },
        "issues": {
            "type": "array",
            "description": "User-facing problems, each grouping one or more related Traps that share a common design element or underlying problem.",
            "items": {
                "type": "object",
                "properties": {
                    "headline": {
                        "type": "string",
                        "description": "One sentence describing the problem in user-relatable terms, tied to the specific design and context. Avoid Trap jargon. Use measured language."
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "moderate", "minor"],
                        "description": "Severity of the issue — take the highest severity among the grouped Traps."
                    },
                    "confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Confidence in this issue — take the lowest confidence among the grouped Traps."
                    },
                    "root_cause_trap": {
                        "type": "object",
                        "description": "The Trap that best represents the root cause of this issue. Required even for single-Trap issues.",
                        "properties": {
                            "trap_name": {
                                "type": "string",
                                "enum": VALID_TRAP_NAMES,
                                "description": "Trap name — MUST be one of the 27 valid trap names"
                            },
                            "tenet": {
                                "type": "string",
                                "enum": VALID_TENET_NAMES
                            },
                            "definition": {
                                "type": "string",
                                "description": "The canonical one-sentence definition of this Trap from the UI Tenets & Traps framework — what the Trap IS in general. Do NOT describe how it manifests in this specific design."
                            }
                        },
                        "required": ["trap_name", "tenet", "definition"]
                    },
                    "contributing_traps": {
                        "type": "array",
                        "description": "Additional Traps whose definitions are also satisfied by this same design problem. Empty array if none.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "trap_name": {
                                    "type": "string",
                                    "enum": VALID_TRAP_NAMES
                                },
                                "tenet": {
                                    "type": "string",
                                    "enum": VALID_TENET_NAMES
                                },
                                "definition": {
                                    "type": "string",
                                    "description": "The canonical one-sentence definition of this Trap from the UI Tenets & Traps framework — what the Trap IS in general. Do NOT describe how it manifests in this specific design."
                                }
                            },
                            "required": ["trap_name", "tenet", "definition"]
                        }
                    },
                    "description": {
                        "type": "string",
                        "description": "2-4 sentences describing the issue from the user's perspective. Use measured language."
                    },
                    "recommendation": {
                        "type": "string",
                        "description": "2-3 sentences suggesting how the issue might be addressed. Use advisory language."
                    },
                    "region": {
                        "type": "object",
                        "description": "Bounding box of the design element. Normalized 0.0-1.0, origin top-left. Omit if no single element can be bounded.",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "width": {"type": "number"},
                            "height": {"type": "number"},
                            "caption": {"type": "string"}
                        },
                        "required": ["x", "y", "width", "height"]
                    }
                },
                "required": ["headline", "severity", "confidence", "root_cause_trap", "contributing_traps", "description", "recommendation"]
            }
        },
        "positive_observations": {
            "type": "array",
            "items": {"type": "string"}
        },
        "traps_checked_not_found": {
            "type": "array",
            "description": "Pass-through from the underlying Trap analysis — traps evaluated and not found.",
            "items": {
                "type": "object",
                "properties": {
                    "trap_name": {"type": "string"},
                    "testable": {"type": "boolean"}
                },
                "required": ["trap_name", "testable"]
            }
        }
    },
    "required": [
        "summary_headline",
        "summary_narrative",
        "issues",
        "positive_observations",
        "traps_checked_not_found"
    ],
    "additionalProperties": False
}


def get_user_issues_schema():
    """Get the JSON schema for Pass 3 user-issues synthesis output (legacy v1/v2)."""
    return USER_ISSUES_SCHEMA


def _new_kb_coverage_items():
    """The coverage-note item shape shared by the new-KB analysis and issues schemas."""
    return {
        "type": "object",
        "properties": {
            "trap_name": {"type": "string", "description": "Name of the trap"},
            "coverage_status": {"type": "string", "enum": NEW_KB_COVERAGE_STATUSES},
            "detail": {"type": "string", "description": "MANDATORY G6 one-line evidence."},
        },
        "required": ["trap_name", "coverage_status", "detail"],
    }


def _new_kb_issues_schema(version: str = "v2.1", self_serve: bool = False):
    """
    By-Issue output schema for the new (v2.1-lineage) KBs — the adjudication pass emits this
    directly when report_style='issues' (Option A). Issue-centric per G8 §1, with each
    aligned Trap carrying its G3 `relationship` marker. The tool injects each trap's verbatim
    `definition` post-hoc from the manifest, so the model does not transcribe it here.

    self_serve=True relaxes the contract for the raw-KB profile: trap names come from the
    injected material (no enum), tenet/relationship are optional (no relationship semantics
    are given to the model), coverage/positives are optional, and every issue field except a
    headline may be omitted. The model may drop any field it cannot ground.
    """
    trap_names = _valid_trap_names(version)
    _trap_name = {"type": "string"} if self_serve else {"type": "string", "enum": trap_names}
    _tenet = {"type": "string"} if self_serve else {"type": "string", "enum": VALID_TENET_NAMES}
    _relationship = ({"type": "string", "description": "Optional relationship marker; omit if not defined by the material."}
                     if self_serve else
                     {"type": "string", "enum": NEW_KB_RELATIONSHIP_VALUES, "description": "G3 designation for this trap within the issue (bracketed G3 value)."})
    _trap_required = ["trap_name"] if self_serve else ["trap_name", "tenet", "relationship"]
    _issue_required = ["headline"] if self_serve else ["headline", "severity_label", "confidence", "traps", "description", "recommendation"]
    _top_required = (["summary_headline", "summary_narrative", "issues"] if self_serve
                     else ["summary_headline", "summary_narrative", "issues", "positive_observations", "traps_checked_not_found"])
    return {
        "type": "object",
        "properties": {
            "summary_headline": {"type": "string", "description": "A punchy verdict (16–24 words) on how well the design supports the stated goal. No counts."},
            "summary_narrative": {"type": "string", "description": "One paragraph on the user-experience implications. Hedged language; no counts, no enumerations."},
            "issues": {
                "type": "array",
                "description": "User-facing issues (G8 §1). Each groups the Trap(s) that align to it per G3 composition.",
                "items": {
                    "type": "object",
                    "properties": {
                        "headline": {"type": "string", "description": "Plain-language, user-facing statement of the problem (8–14 words). No trap jargon."},
                        "severity_label": {"type": "string", "enum": NEW_KB_SEVERITY_LABELS, "description": "Highest severity among this issue's traps. Severity ≠ likelihood."},
                        "confidence": {"type": "string", "enum": NEW_KB_CONFIDENCE_LEVELS, "description": "Lowest confidence among this issue's traps."},
                        "traps": {
                            "type": "array",
                            "description": "The Trap(s) aligned to this issue per G3. A `consequence` trap is included here (it renders in prose, not as a separate entry). One entry per trap.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "trap_name": _trap_name,
                                    "tenet": _tenet,
                                    "relationship": _relationship,
                                },
                                "required": _trap_required,
                            },
                        },
                        "description": {"type": "string", "description": "Problem-first prose: what the user experiences and why. Reference traps only to aid understanding/fixing; state any cascade or conditional-branch condition here, not as jargon. Hedged language."},
                        "recommendation": {"type": "string", "description": "The fix direction, advisory language."},
                        "region": {
                            "type": "object",
                            "description": "Optional bounding box of the element. Normalized 0.0–1.0, origin top-left. Omit if no single element bounds it.",
                            "properties": {
                                "x": {"type": "number"}, "y": {"type": "number"},
                                "width": {"type": "number"}, "height": {"type": "number"},
                                "caption": {"type": "string"},
                            },
                            "required": ["x", "y", "width", "height"],
                        },
                    },
                    "required": _issue_required,
                },
            },
            "positive_observations": {"type": "array", "items": {"type": "string"}},
            "traps_checked_not_found": {
                "type": "array",
                "description": "Coverage notes (G8 §3), same shape as the by-trap report. Includes partially_assessed (J27 scoped) entries even when the trap is also an Issue.",
                "items": _new_kb_coverage_items(),
            },
        },
        "required": _top_required,
        "additionalProperties": bool(self_serve),
    }


def _self_serve_issues_schema(version: str = "v1"):
    """BARE output schema for the KB-only (self-serve) profile. It defines ONLY the report
    shape — no field-level guidance, no G3 relationship semantics, no G4 coverage taxonomy.
    The KB (injected verbatim) and the screenshot are the only inputs; the harness supplies
    just the labels (High/Medium/Low) and the container. Coverage notes are derived by the
    tool afterward (the complement of the reported traps), so the model is never shown the
    coverage vocabulary. Fields are omittable (headline is the only requirement)."""
    return {
        "type": "object",
        "properties": {
            "summary_headline": {"type": "string"},
            "summary_narrative": {"type": "string"},
            "issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "headline": {"type": "string"},
                        "severity_label": {"type": "string", "enum": NEW_KB_SEVERITY_LABELS},
                        "confidence": {"type": "string", "enum": NEW_KB_CONFIDENCE_LEVELS},
                        "traps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"trap_name": {"type": "string"}},
                                "required": ["trap_name"],
                            },
                        },
                        "description": {"type": "string"},
                        "recommendation": {"type": "string"},
                    },
                    "required": ["headline"],
                },
            },
            "positive_observations": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["summary_headline", "summary_narrative", "issues"],
        "additionalProperties": True,
    }


_NEW_KB_ISSUES_SCHEMA_CACHE: dict = {}


def get_ui_issues_schema(version: str = "v2", self_serve: bool = False):
    """By-Issue schema. New KBs get the issue-centric relationship schema (per lineage);
    legacy v1/v2 get the existing USER_ISSUES_SCHEMA (Pass-3 synthesis). The self-serve
    (raw-KB) profile uses the RELAXED issue schema for ANY version — it renders through the
    rev6 template regardless of lineage, and lets the model omit fields it cannot ground."""
    lineage = "v1" if version in ("v1", "v1.1") else "v2"
    if self_serve:
        key = ("self_serve", lineage)
        cached = _NEW_KB_ISSUES_SCHEMA_CACHE.get(key)
        if cached is None:
            cached = _NEW_KB_ISSUES_SCHEMA_CACHE[key] = _self_serve_issues_schema(version)
        return cached
    if not is_new_kb(version):
        return USER_ISSUES_SCHEMA
    cached = _NEW_KB_ISSUES_SCHEMA_CACHE.get(lineage)
    if cached is None:
        cached = _NEW_KB_ISSUES_SCHEMA_CACHE[lineage] = _new_kb_issues_schema(version)
    return cached


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
