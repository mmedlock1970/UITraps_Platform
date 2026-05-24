import pytest
from unittest.mock import patch, MagicMock
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
        'f1': {
            'name': 'Cart',
            'reached_from': [],
            'leads_to': [{'screen': 'Checkout', 'via': 'tap on "Checkout"'}]
        },
        'f2': {
            'name': 'Checkout',
            'reached_from': [{'screen': 'Cart', 'via': 'tap on "Checkout"'}],
            'leads_to': []
        },
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


@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', side_effect=lambda self_or_r, *args, **kwargs: self_or_r if isinstance(self_or_r, dict) else args[0])
def test_screen_mode_calls_pass1_per_frame(mock_enrich, mock_pass1):
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(
        frames=MOCK_FRAMES,
        flow_map=MOCK_FLOW_MAP,
        user_context=USER_CONTEXT,
        mode='screen',
    )
    assert mock_pass1.call_count == 2


@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', side_effect=lambda self_or_r, *args, **kwargs: self_or_r if isinstance(self_or_r, dict) else args[0])
def test_flow_mode_calls_pass1_once(mock_enrich, mock_pass1):
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(
        frames=MOCK_FRAMES,
        flow_map=MOCK_FLOW_MAP,
        user_context=USER_CONTEXT,
        mode='flow',
    )
    assert mock_pass1.call_count == 1


@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', side_effect=lambda self_or_r, *args, **kwargs: self_or_r if isinstance(self_or_r, dict) else args[0])
def test_skips_frames_without_image_path(mock_enrich, mock_pass1):
    frames = MOCK_FRAMES + [{'id': 'f3', 'name': 'Error', 'image_path': None}]
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(
        frames=frames,
        flow_map=MOCK_FLOW_MAP,
        user_context=USER_CONTEXT,
        mode='screen',
    )
    assert mock_pass1.call_count == 2  # f3 skipped


@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', side_effect=lambda self_or_r, *args, **kwargs: self_or_r if isinstance(self_or_r, dict) else args[0])
def test_screen_mode_injects_flow_context(mock_enrich, mock_pass1):
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(
        frames=MOCK_FRAMES,
        flow_map=MOCK_FLOW_MAP,
        user_context=USER_CONTEXT,
        mode='screen',
    )
    # Each _pass1 call should have FLOW CONTEXT in the user_context extra_context
    for call in mock_pass1.call_args_list:
        ctx = call.kwargs.get('user_context', {})
        assert 'FLOW CONTEXT' in ctx.get('extra_context', '')


@patch.object(UITrapsAnalyzer, '_pass1', return_value=MOCK_REPORT)
@patch.object(UITrapsAnalyzer, '_enrich_report', side_effect=lambda self_or_r, *args, **kwargs: self_or_r if isinstance(self_or_r, dict) else args[0])
def test_flow_mode_injects_flow_analysis(mock_enrich, mock_pass1):
    analyzer = UITrapsAnalyzer.__new__(UITrapsAnalyzer)
    analyzer.analyze_flow_diagram(
        frames=MOCK_FRAMES,
        flow_map=MOCK_FLOW_MAP,
        user_context=USER_CONTEXT,
        mode='flow',
    )
    ctx = mock_pass1.call_args.kwargs.get('user_context', {})
    assert 'FLOW ANALYSIS' in ctx.get('extra_context', '')
