from src.prompts import build_flow_context_section, build_user_message


def test_screen_mode_includes_reached_from():
    ctx = {
        'name': 'Checkout',
        'reached_from': [{'screen': 'Cart', 'via': 'tap on "Checkout button"'}],
        'leads_to': [{'screen': 'Order Confirmation', 'via': 'tap on "Place Order"'}],
    }
    result = build_flow_context_section(flow_context=ctx, mode='screen')
    assert 'Reached from: Cart' in result
    assert 'Leads to: Order Confirmation' in result
    assert 'FLOW CONTEXT' in result


def test_flow_mode_includes_summary():
    summary = "Complete flow: Cart -> Checkout\nNavigation map:\n  Cart: Checkout button -> Checkout"
    result = build_flow_context_section(flow_summary=summary, mode='flow')
    assert 'Cart -> Checkout' in result
    assert 'FLOW ANALYSIS' in result
    assert 'UNNECESSARY STEPS' in result


def test_returns_empty_string_for_missing_data():
    assert build_flow_context_section() == ''
    assert build_flow_context_section(mode='screen') == ''
    assert build_flow_context_section(mode='flow') == ''


def test_build_user_message_accepts_image_list():
    ctx = {
        'users': 'users', 'tasks': 'task', 'format': 'app',
        'content_type': 'website', 'task_list': []
    }
    img1 = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "abc"}}
    img2 = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "def"}}
    content = build_user_message(ctx, image_data_list=[img1, img2])
    image_blocks = [c for c in content if c.get('type') == 'image']
    assert len(image_blocks) == 2
    text_blocks = [c for c in content if c.get('type') == 'text']
    assert len(text_blocks) == 1
