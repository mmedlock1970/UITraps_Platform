"""
Tests for analyze_flow_diagram — conformed to the CURRENT signature/behavior.

`analyze_flow_diagram(frames, flow_map, user_context, timeout, kb_version, verbosity,
pass1_model)` has NO `mode` parameter: it ALWAYS runs both passes and merges them —
  • Screen pass: one `_pass1` per valid frame, injecting "FLOW CONTEXT" into extra_context.
  • Flow pass:   one `_pass1` on the first frame, injecting "FLOW ANALYSIS".
So total `_pass1` calls = len(valid_frames) + 1. We distinguish the two passes by the
context each injects rather than by a mode flag.
"""
from unittest.mock import patch
from src.analyzer import UITrapsAnalyzer

MOCK_REPORT = {
    'summary_headline': 'Test',
    'summary_narrative': 'Test narrative',
    'critical_issues': [],
    'moderate_issues': [],
    'minor_issues': [],
    'positive_observations': [],
    'potential_issues': [],
    'traps_checked_not_found': [],
    'flagged_for_human_review': [],
    'incomplete_flow_findings': [],
    'bugs_detected': [],
}

MOCK_FLOW_MAP = {
    'per_frame': {
        'f1': {'name': 'Cart', 'reached_from': [], 'leads_to': [{'screen': 'Checkout', 'via': 'tap on "Checkout"'}]},
        'f2': {'name': 'Checkout', 'reached_from': [{'screen': 'Cart', 'via': 'tap on "Checkout"'}], 'leads_to': []},
    },
    'summary': 'Complete flow: Cart -> Checkout\nNavigation map:\n  Cart: Checkout -> Checkout',
}

MOCK_FRAMES = [
    {'id': 'f1', 'name': 'Cart', 'image_path': '/tmp/cart.png'},
    {'id': 'f2', 'name': 'Checkout', 'image_path': '/tmp/checkout.png'},
]

USER_CONTEXT = {
    'users': 'users', 'tasks': 'buy product',
    'format': 'app', 'content_type': 'website', 'task_list': []
}

# _enrich_report is patched on the class → called unbound (no self), so the first positional
# arg is the report dict; pass it straight through.
_ENRICH_PASSTHROUGH = dict(side_effect=lambda self_or_r, *args, **kwargs: self_or_r if isinstance(self_or_r, dict) else args[0])


def _extra(call):
    return (call.kwargs.get('user_context', {}) or {}).get('extra_context', '')


@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', **_ENRICH_PASSTHROUGH)
def test_runs_pass1_per_frame_plus_one_flow_pass(mock_enrich, mock_pass1):
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(frames=MOCK_FRAMES, flow_map=MOCK_FLOW_MAP, user_context=USER_CONTEXT)
    assert mock_pass1.call_count == len(MOCK_FRAMES) + 1  # 2 screen + 1 flow


@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', **_ENRICH_PASSTHROUGH)
def test_skips_frames_without_image_path(mock_enrich, mock_pass1):
    frames = MOCK_FRAMES + [{'id': 'f3', 'name': 'Error', 'image_path': None}]
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(frames=frames, flow_map=MOCK_FLOW_MAP, user_context=USER_CONTEXT)
    assert mock_pass1.call_count == 3  # 2 valid-frame screen passes + 1 flow pass (f3 skipped)


@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', **_ENRICH_PASSTHROUGH)
def test_screen_pass_injects_flow_context_per_frame(mock_enrich, mock_pass1):
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(frames=MOCK_FRAMES, flow_map=MOCK_FLOW_MAP, user_context=USER_CONTEXT)
    screen_calls = [c for c in mock_pass1.call_args_list if 'FLOW CONTEXT' in _extra(c)]
    assert len(screen_calls) == len(MOCK_FRAMES)


@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', **_ENRICH_PASSTHROUGH)
def test_flow_pass_injects_flow_analysis_once(mock_enrich, mock_pass1):
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(frames=MOCK_FRAMES, flow_map=MOCK_FLOW_MAP, user_context=USER_CONTEXT)
    flow_calls = [c for c in mock_pass1.call_args_list if 'FLOW ANALYSIS' in _extra(c)]
    assert len(flow_calls) == 1


@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', **_ENRICH_PASSTHROUGH)
def test_screen_and_flow_contexts_are_distinct(mock_enrich, mock_pass1):
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(frames=MOCK_FRAMES, flow_map=MOCK_FLOW_MAP, user_context=USER_CONTEXT)
    extras = [_extra(c) for c in mock_pass1.call_args_list]
    assert sum('FLOW CONTEXT' in e for e in extras) == len(MOCK_FRAMES)
    assert sum('FLOW ANALYSIS' in e for e in extras) == 1
