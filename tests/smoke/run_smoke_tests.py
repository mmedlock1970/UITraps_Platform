#!/usr/bin/env python3
"""
UI Traps Analyzer — Smoke Test Suite

Tests behavioral properties of the live Railway backend.
Does NOT test trap detection quality — tests that specific known behaviors
work correctly (draft suppression, task attribution, task naming, etc.).

Requirements:
    pip install requests Pillow

Usage:
    # Set credentials as env vars:
    ANALYZER_URL=https://your-app.railway.app ANALYZER_TOKEN=<jwt> python tests/smoke/run_smoke_tests.py

    # Or put them in tests/smoke/.env.test (see .env.test.example)
    python tests/smoke/run_smoke_tests.py

    # Skip slow analysis tests (no Claude calls, no API credit cost):
    python tests/smoke/run_smoke_tests.py --fast
"""

import argparse
import io
import json
import os
import re
import sys
import threading
import time
from typing import Callable, Optional

try:
    import requests
except ImportError:
    print("requests not installed — run: pip install requests")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Pillow not installed — run: pip install Pillow")
    sys.exit(1)


# ─── Credentials ─────────────────────────────────────────────────────────────

_env_file = os.path.join(os.path.dirname(__file__), ".env.test")
if os.path.exists(_env_file):
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

ANALYZER_URL = os.environ.get("ANALYZER_URL", "").rstrip("/")
ANALYZER_TOKEN = os.environ.get("ANALYZER_TOKEN", "")


def _check_token_expiry(token: str) -> None:
    """Decode JWT exp claim (no signature check) and abort if expired."""
    if not token:
        return
    try:
        import base64, json as _json
        parts = token.split(".")
        if len(parts) != 3:
            return
        payload_b64 = parts[1] + "=="  # re-pad
        payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
        exp = payload.get("exp")
        if exp and time.time() > exp:
            expired_at = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(exp))
            print(f"\n{R}Error: Token expired at {expired_at}.{X}")
            print("Get a fresh token:")
            print("  1. Open the WordPress staging site")
            print("  2. DevTools → Network → filter 'railway' → clear log (🚫)")
            print("  3. Click Past Analyses → copy Bearer value from /reports request")
            print("  4. Paste new token into tests/smoke/.env.test\n")
            sys.exit(1)
    except Exception:
        pass  # malformed token — let the server reject it


# ─── Terminal colors ──────────────────────────────────────────────────────────

G = "\033[92m"  # green
R = "\033[91m"  # red
Y = "\033[93m"  # yellow
C = "\033[96m"  # cyan
B = "\033[1m"   # bold
X = "\033[0m"   # reset


# ─── Synthetic image fixtures ─────────────────────────────────────────────────

def _to_png(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def fixture_simple_ui() -> bytes:
    """Generic e-commerce UI: nav bar, hero, three product cards with prices and Add to Cart buttons."""
    img = Image.new("RGB", (900, 600), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # Nav
    d.rectangle([0, 0, 900, 60], fill=(25, 25, 25))
    d.text((20, 18), "ShopNow", fill=(255, 255, 255))
    for label, x in [("Products", 600), ("About", 700), ("Contact", 800)]:
        d.text((x, 18), label, fill=(180, 180, 180))
    # Hero
    d.text((40, 90), "Discover our latest collection", fill=(25, 25, 25))
    d.text((40, 120), "High-quality goods at fair prices. Free shipping over $50.", fill=(80, 80, 80))
    d.rectangle([40, 155, 210, 192], fill=(0, 120, 200))
    d.text((70, 165), "Shop Now", fill=(255, 255, 255))
    # Product cards
    d.text((40, 230), "Featured Products", fill=(25, 25, 25))
    for i, name in enumerate(["Trail Runner X", "Summit Pack Pro", "Polar Fleece Vest"]):
        x = 40 + i * 285
        d.rectangle([x, 260, x + 255, 460], outline=(210, 210, 210))
        d.text((x + 10, 270), name, fill=(25, 25, 25))
        d.text((x + 10, 300), "$79.99", fill=(60, 60, 60))
        d.text((x + 10, 325), "In stock", fill=(0, 140, 70))
        d.rectangle([x + 10, 400, x + 160, 435], fill=(0, 120, 200))
        d.text((x + 30, 410), "Add to Cart", fill=(255, 255, 255))
    return _to_png(img)


def fixture_lorem_product_page() -> bytes:
    """Product detail page where the description copy is lorem ipsum placeholder text."""
    img = Image.new("RGB", (900, 600), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 900, 60], fill=(25, 25, 25))
    d.text((20, 18), "ShopNow", fill=(255, 255, 255))
    d.text((40, 80), "Premium Widget Pro", fill=(25, 25, 25))
    d.text((40, 110), "$49.99", fill=(60, 60, 60))
    d.text((40, 145), "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", fill=(80, 80, 80))
    d.text((40, 170), "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", fill=(80, 80, 80))
    d.text((40, 195), "Ut enim ad minim veniam, quis nostrud exercitation ullamco.", fill=(80, 80, 80))
    d.rectangle([40, 235, 210, 272], fill=(0, 150, 80))
    d.text((72, 246), "Add to Cart", fill=(255, 255, 255))
    d.text((40, 310), "Product Details", fill=(25, 25, 25))
    d.text((40, 340), "Lorem ipsum dolor sit amet, consectetur adipiscing.", fill=(80, 80, 80))
    d.text((40, 365), "Pellentesque habitant morbi tristique senectus et netus.", fill=(80, 80, 80))
    return _to_png(img)


def fixture_login_only() -> bytes:
    """Full-screen login wall: only Log In and Sign Up controls, no browse path."""
    img = Image.new("RGB", (900, 600), (235, 238, 242))
    d = ImageDraw.Draw(img)
    d.rectangle([300, 110, 600, 470], fill=(255, 255, 255), outline=(215, 215, 215))
    d.text((355, 140), "Welcome Back", fill=(25, 25, 25))
    d.text((320, 195), "Email address", fill=(80, 80, 80))
    d.rectangle([315, 215, 585, 248], outline=(180, 180, 180), fill=(250, 250, 250))
    d.text((320, 265), "Password", fill=(80, 80, 80))
    d.rectangle([315, 285, 585, 318], outline=(180, 180, 180), fill=(250, 250, 250))
    d.rectangle([315, 345, 585, 382], fill=(0, 100, 200))
    d.text((398, 355), "Log In", fill=(255, 255, 255))
    d.text((330, 415), "Don't have an account?", fill=(80, 80, 80))
    d.text((390, 440), "Sign Up", fill=(0, 100, 200))
    return _to_png(img)


# ─── API helpers ──────────────────────────────────────────────────────────────

def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {ANALYZER_TOKEN}"}


def post_analysis(
    png_bytes: bytes,
    users: str,
    tasks_str: str,
    task_list: Optional[list] = None,
    extra_context: str = "",
    design_name: str = "smoke-test",
) -> dict:
    """Submit a single-image analysis via /api/ask. Returns parsed JSON response."""
    files = [("files", ("test.png", png_bytes, "image/png"))]
    data = {
        "users": users,
        "tasks": tasks_str,
        "format": "website",
        "content_type": "website",
        "design_name": design_name,
        "extra_context": extra_context,
        "kb_version": "v2",
    }
    if task_list and len(task_list) > 1:
        data["task_list"] = json.dumps(task_list)

    resp = requests.post(
        f"{ANALYZER_URL}/api/ask",
        files=files,
        data=data,
        headers=_auth_headers(),
        timeout=180,
    )
    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise AssertionError(f"HTTP {resp.status_code} from /api/ask: {detail}")
    return resp.json()


# ─── Test runner ──────────────────────────────────────────────────────────────

class _Result:
    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0.0):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration


def _run(name: str, fn: Callable) -> _Result:
    print(f"  {B}{name}{X}")
    t0 = time.time()
    stop = threading.Event()

    def _ticker():
        while not stop.wait(1.0):
            elapsed = time.time() - t0
            sys.stdout.write(f"\r    ⏱  {elapsed:.0f}s")
            sys.stdout.flush()

    ticker = threading.Thread(target=_ticker, daemon=True)
    ticker.start()

    try:
        fn()
        stop.set()
        ticker.join()
        dur = time.time() - t0
        sys.stdout.write(f"\r    {G}✓  passed{X} ({dur:.1f}s)\n\n")
        sys.stdout.flush()
        return _Result(name, True, duration=dur)
    except AssertionError as e:
        stop.set()
        ticker.join()
        dur = time.time() - t0
        sys.stdout.write(f"\r    {R}✗  FAILED:{X} {e} ({dur:.1f}s)\n\n")
        sys.stdout.flush()
        return _Result(name, False, str(e), dur)
    except Exception as e:
        stop.set()
        ticker.join()
        dur = time.time() - t0
        sys.stdout.write(f"\r    {R}✗  ERROR:{X} {type(e).__name__}: {e} ({dur:.1f}s)\n\n")
        sys.stdout.flush()
        return _Result(name, False, f"{type(e).__name__}: {e}", dur)


# ─── Fast tests (no Claude calls, instant) ───────────────────────────────────

def test_health():
    """Backend is reachable and reports healthy status."""
    r = requests.get(f"{ANALYZER_URL}/health", timeout=10)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data.get("status") == "healthy", f"Unexpected health response: {data}"


def test_auth_required_on_reports():
    """GET /reports without a token must be rejected (401/403 or success:false)."""
    r = requests.get(f"{ANALYZER_URL}/reports", timeout=10)
    if r.status_code in (401, 403):
        return  # correct
    try:
        data = r.json()
        assert not data.get("success", True), \
            f"Expected auth rejection, got HTTP {r.status_code} with success:true"
    except Exception:
        assert False, f"Expected auth rejection, got HTTP {r.status_code}"


def test_past_analyses_with_auth():
    """GET /reports with a valid token returns success:true with a reports list."""
    r = requests.get(f"{ANALYZER_URL}/reports", headers=_auth_headers(), timeout=10)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data.get("success") is True, f"Expected success:true, got: {data}"
    assert "reports" in data, f"Missing 'reports' key: {data}"
    assert "count" in data, f"Missing 'count' key: {data}"


# ─── Analysis tests (Claude calls — 30–90s each, costs API credits) ──────────

def test_analysis_response_shape():
    """Analysis returns the expected top-level fields with HTML content."""
    data = post_analysis(
        fixture_simple_ui(),
        users="General online shopper",
        tasks_str="Browse and purchase a product",
        design_name="smoke-shape",
    )
    assert data.get("success") is True, f"success != true — error: {data.get('error')}"
    assert data.get("mode") == "analysis", f"Unexpected mode: {data.get('mode')!r}"
    html = data.get("report_html", "")
    assert html, "report_html is empty or missing"
    assert "<" in html, "report_html does not appear to contain HTML markup"


def test_draft_context_suppresses_lorem():
    """
    When context explicitly declares a design is a draft with placeholder copy,
    lorem ipsum text must not appear in an INCORRECT INFORMATION finding.
    """
    data = post_analysis(
        fixture_lorem_product_page(),
        users="Online shopper evaluating products",
        tasks_str="Browse and add a product to the cart",
        extra_context=(
            "NOTE: This is an early draft. All lorem ipsum copy is placeholder text "
            "that will be replaced with real product descriptions before launch."
        ),
        design_name="smoke-draft",
    )
    assert data.get("success") is True, f"Analysis failed: {data.get('error')}"
    html = data.get("report_html", "")

    # If lorem ipsum content surfaced in a finding, it must not be inside an
    # INCORRECT INFORMATION finding block. We locate any INCORRECT INFORMATION
    # badges and check the surrounding text.
    ii_pattern = re.compile(
        r'INCORRECT INFORMATION.{0,600}',
        re.DOTALL | re.IGNORECASE,
    )
    for block in ii_pattern.findall(html):
        assert "lorem ipsum" not in block.lower(), (
            "An INCORRECT INFORMATION finding references lorem ipsum "
            "despite draft context being provided — draft suppression not working"
        )


def test_single_task_no_task_sections():
    """Single-task analysis must not produce per-task section divs in the HTML."""
    data = post_analysis(
        fixture_simple_ui(),
        users="Online shopper",
        tasks_str="Browse the product catalog and find an item to buy",
        design_name="smoke-single-task",
    )
    assert data.get("success") is True, f"Analysis failed: {data.get('error')}"
    html = data.get("report_html", "")
    assert "<h3 class='task-section-header'" not in html, (
        "Single-task report contains task-section divs — "
        "per-task sections should only appear in multi-task reports"
    )


def test_multi_task_uses_description_as_header():
    """
    When tasks have descriptions but no names, the report section headers
    must use the description text rather than falling back to 'Task 1', 'Task 2', etc.
    """
    desc_a = "Find a pair of running shoes and add them to the cart"
    desc_b = "Check the stores return policy before completing the purchase"
    data = post_analysis(
        fixture_simple_ui(),
        users="Cautious online shopper",
        tasks_str=f"{desc_a}. {desc_b}",
        task_list=[
            {"name": "", "description": desc_a},
            {"name": "", "description": desc_b},
        ],
        design_name="smoke-task-naming",
    )
    assert data.get("success") is True, f"Analysis failed: {data.get('error')}"
    html = data.get("report_html", "")
    assert "<h3 class='task-section-header'" in html, "Multi-task report is missing task-section divs entirely"
    assert "running shoes" in html.lower(), (
        "First task description not found in HTML — "
        "task naming may be falling back to 'Task 1' instead of using description"
    )
    assert "return policy" in html.lower(), (
        "Second task description not found in HTML — "
        "check task_list fallback logic in formatters.py"
    )


def test_multi_task_findings_have_task_sections():
    """Multi-task analysis produces task-section divs in the HTML report."""
    data = post_analysis(
        fixture_simple_ui(),
        users="Online shopper",
        tasks_str="Browse products. Add an item to the cart and check out.",
        task_list=[
            {"name": "Browse", "description": "Browse the product catalog"},
            {"name": "Purchase", "description": "Add an item to the cart and check out"},
        ],
        design_name="smoke-task-attr",
    )
    assert data.get("success") is True, f"Analysis failed: {data.get('error')}"
    html = data.get("report_html", "")
    assert "<h3 class='task-section-header'" in html, (
        "Multi-task report is missing task-section divs — "
        "findings are not being attributed to tasks"
    )


def test_prerequisite_gate_not_invisible_element():
    """
    A login wall that blocks the core task should not be classified solely as
    INVISIBLE ELEMENT. The correct classification is UNNECESSARY STEP(S).
    INVISIBLE ELEMENT applies when a path exists but lacks a visible cue —
    a blocked/gated path is a step-count problem, not a visibility problem.
    """
    data = post_analysis(
        fixture_login_only(),
        users="New visitor who wants to browse products without registering",
        tasks_str="Browse the product catalog without creating an account",
        design_name="smoke-gate",
    )
    assert data.get("success") is True, f"Analysis failed: {data.get('error')}"
    html = data.get("report_html", "")
    html_lower = html.lower()

    has_invisible_element = "invisible element" in html_lower
    has_unnecessary_steps = "unnecessary step" in html_lower

    if has_invisible_element and not has_unnecessary_steps:
        assert False, (
            "Login gate flagged as INVISIBLE ELEMENT without UNNECESSARY STEPS — "
            "a gated path is a step-count problem, not a visibility problem. "
            "See KB disambiguation rule added 2026-06-11."
        )


# ─── Main ─────────────────────────────────────────────────────────────────────

FAST_TESTS = [
    ("Health check", test_health),
    ("Auth required on /reports (no token)", test_auth_required_on_reports),
    ("Past analyses endpoint (with auth)", test_past_analyses_with_auth),
]

ANALYSIS_TESTS = [
    ("Analysis response shape", test_analysis_response_shape),
    ("Draft context: lorem ipsum suppressed from INCORRECT INFORMATION", test_draft_context_suppresses_lorem),
    ("Single task: no task-section divs", test_single_task_no_task_sections),
    ("Multi-task: description used as section header (not 'Task 1')", test_multi_task_uses_description_as_header),
    ("Multi-task: task-section divs present", test_multi_task_findings_have_task_sections),
    ("Login gate: not classified as INVISIBLE ELEMENT", test_prerequisite_gate_not_invisible_element),
]


def main():
    parser = argparse.ArgumentParser(description="UI Traps Analyzer smoke tests")
    parser.add_argument(
        "--fast", action="store_true",
        help="Run only fast tests — no Claude calls, no API credit cost"
    )
    args = parser.parse_args()

    print(f"\n{B}UI Traps Analyzer — Smoke Tests{X}")
    print(f"Backend : {ANALYZER_URL or f'{R}not set{X}'}")
    print(f"Token   : {'set' if ANALYZER_TOKEN else f'{Y}not set — auth tests will fail{X}'}")
    print()

    _check_token_expiry(ANALYZER_TOKEN)

    if not ANALYZER_URL:
        print(f"{R}Error: ANALYZER_URL is not set.{X}")
        print("Add it to tests/smoke/.env.test or export it as an environment variable.")
        sys.exit(1)

    results: list[_Result] = []

    print(f"{C}── Fast tests (no Claude calls) ──────────────────────{X}\n")
    for name, fn in FAST_TESTS:
        results.append(_run(name, fn))

    if args.fast:
        print(f"{Y}Skipping analysis tests (--fast).{X}\n")
    else:
        est = len(ANALYSIS_TESTS) * 60
        print(f"{C}── Analysis tests (~{est // 60}–{est * 2 // 60} min total, uses API credits) ──{X}\n")
        for name, fn in ANALYSIS_TESTS:
            results.append(_run(name, fn))

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    color = G if failed == 0 else R

    print(f"{B}──────────────────────────────────────────────────────{X}")
    print(f"{B}Results: {color}{passed}/{len(results)} passed{X}", end="")
    print(f"  {R}({failed} failed){X}" if failed else "")
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
