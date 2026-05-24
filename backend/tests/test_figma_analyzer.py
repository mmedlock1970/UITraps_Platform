import pytest
from src.figma_analyzer import FigmaAnalyzer, build_flow_map


def _mock_document():
    return {
        "document": {
            "children": [{
                "type": "PAGE",
                "name": "Page 1",
                "children": [
                    {
                        "type": "FRAME",
                        "id": "frame-1",
                        "name": "Cart",
                        "children": [
                            {
                                "type": "COMPONENT",
                                "id": "btn-checkout",
                                "name": "Checkout button",
                                "interactions": [{
                                    "trigger": {"type": "ON_CLICK"},
                                    "actions": [{"destinationId": "frame-2"}]
                                }],
                                "children": []
                            }
                        ]
                    },
                    {
                        "type": "FRAME",
                        "id": "frame-2",
                        "name": "Checkout",
                        "children": []
                    }
                ]
            }]
        }
    }


def test_get_prototype_flows_includes_from_frame():
    fa = FigmaAnalyzer.__new__(FigmaAnalyzer)
    flows = fa.get_prototype_flows(_mock_document())

    assert len(flows) == 1
    flow = flows[0]
    assert flow['from_node'] == 'btn-checkout'
    assert flow['from_name'] == 'Checkout button'
    assert flow['to_node'] == 'frame-2'
    assert flow['from_frame'] == 'frame-1'
    assert flow['from_frame_name'] == 'Cart'


def _mock_frames():
    return [
        {'id': 'frame-1', 'name': 'Cart'},
        {'id': 'frame-2', 'name': 'Checkout'},
        {'id': 'frame-3', 'name': 'Order Confirmation'},
    ]


def _mock_flows():
    return [
        {
            'from_node': 'btn-1', 'from_name': 'Checkout button',
            'from_frame': 'frame-1', 'from_frame_name': 'Cart',
            'to_node': 'frame-2', 'trigger': 'ON_CLICK'
        },
        {
            'from_node': 'btn-2', 'from_name': 'Place Order',
            'from_frame': 'frame-2', 'from_frame_name': 'Checkout',
            'to_node': 'frame-3', 'trigger': 'ON_CLICK'
        },
    ]


def test_build_flow_map_per_frame_context():
    result = build_flow_map(_mock_frames(), _mock_flows())
    per = result['per_frame']

    assert any(e['screen'] == 'Checkout' for e in per['frame-1']['leads_to'])
    assert any(e['screen'] == 'Cart' for e in per['frame-2']['reached_from'])
    assert any(e['screen'] == 'Order Confirmation' for e in per['frame-2']['leads_to'])
    assert any(e['screen'] == 'Checkout' for e in per['frame-3']['reached_from'])


def test_build_flow_map_summary_contains_frames():
    result = build_flow_map(_mock_frames(), _mock_flows())
    summary = result['summary']
    assert 'Cart' in summary
    assert 'Checkout' in summary
    assert 'Order Confirmation' in summary


def test_build_flow_map_ignores_unknown_destinations():
    flows = _mock_flows() + [{
        'from_node': 'btn-x', 'from_name': 'External link',
        'from_frame': 'frame-1', 'from_frame_name': 'Cart',
        'to_node': 'unknown-node-id', 'trigger': 'ON_CLICK'
    }]
    result = build_flow_map(_mock_frames(), flows)
    assert len(result['per_frame']['frame-1']['leads_to']) == 1
