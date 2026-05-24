import pytest
from src.figma_analyzer import FigmaAnalyzer


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
