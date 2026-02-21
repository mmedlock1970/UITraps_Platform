"""
UI Traps Analyzer - Web Crawler Module

Copyright © 2009-present UI Traps LLC. All Rights Reserved.

CONFIDENTIAL AND PROPRIETARY
This code contains proprietary UI Tenets & Traps framework logic.
Unauthorized use, reproduction, or distribution is strictly prohibited.

This module enables automated analysis of public websites by:
1. Crawling websites and capturing screenshots
2. Following navigation flows
3. Discovering multi-page patterns
4. Analyzing for UI Traps across entire flows
5. Capturing interaction sequences (hover, click, form, scroll, responsive)
"""

import asyncio
import base64
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from urllib.parse import urljoin, urlparse
import json

try:
    from .interaction_explorer import (
        InteractionExplorer,
        InteractionExplorerConfig,
        InteractionCapture
    )
    from .navigation_graph import NavigationGraphBuilder, NavigationGraph
    INTERACTION_EXPLORER_AVAILABLE = True
    NAVIGATION_GRAPH_AVAILABLE = True
except ImportError:
    # Fallback for direct script execution
    try:
        from interaction_explorer import (
            InteractionExplorer,
            InteractionExplorerConfig,
            InteractionCapture
        )
        from navigation_graph import NavigationGraphBuilder, NavigationGraph
        INTERACTION_EXPLORER_AVAILABLE = True
        NAVIGATION_GRAPH_AVAILABLE = True
    except ImportError:
        INTERACTION_EXPLORER_AVAILABLE = False
        NAVIGATION_GRAPH_AVAILABLE = False


class WebCrawler:
    """
    Crawls public websites and captures screenshots for UI Traps analysis.

    Uses Playwright for reliable browser automation and screenshot capture.
    """

    def __init__(
        self,
        max_pages: int = 10,
        max_depth: int = 2,
        wait_time: int = 2,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        user_agent: Optional[str] = None,
        cookies: Optional[Any] = None,
        storage_state: Optional[str] = None,
        enable_interaction_capture: bool = False,
        interaction_config: Optional[Dict[str, Any]] = None,
        enable_navigation_graph: bool = True,
        verify_ctas: bool = True,
        max_ctas_to_verify: int = 5,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ):
        """
        Initialize web crawler.

        Args:
            max_pages: Maximum number of pages to crawl (default: 10)
            max_depth: Maximum link depth to follow (default: 2)
            wait_time: Seconds to wait after page load (default: 2)
            viewport_width: Browser viewport width (default: 1920)
            viewport_height: Browser viewport height (default: 1080)
            user_agent: Custom user agent string (optional)
            cookies: Browser cookies for authenticated access. Accepts:
                - JSON string: '[{"name":"session","value":"abc123","domain":".site.com"}]'
                - List of dicts: [{"name":"session","value":"abc123"}]
                - Dict by domain: {"site.com": [{"name":"session","value":"abc123"}]}
            storage_state: Path to Playwright storage_state.json file.
                Preferred over cookies as it includes localStorage/sessionStorage.
                Get from: context.storage_state(path="auth.json")
            enable_interaction_capture: Enable moment-by-moment interaction capture (default: False)
            interaction_config: Configuration for interaction explorer (optional)
                - max_hover_elements: int (default: 20)
                - max_click_elements: int (default: 10)
                - max_forms: int (default: 3)
                - capture_hover: bool (default: True)
                - capture_click: bool (default: True)
                - capture_form: bool (default: True)
                - capture_scroll: bool (default: True)
                - capture_responsive: bool (default: True)
            enable_navigation_graph: Build site navigation graph (default: True)
            verify_ctas: Click CTAs to verify destinations (default: True)
            max_ctas_to_verify: Max CTAs to verify per page (default: 5)
            progress_callback: Optional callback(message, current, total) for progress updates
        """
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.wait_time = wait_time
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.user_agent = user_agent
        self.cookies = self._parse_cookies(cookies) if cookies else None
        self.storage_state = storage_state
        self.enable_interaction_capture = enable_interaction_capture
        self.interaction_config = interaction_config or {}
        self.enable_navigation_graph = enable_navigation_graph
        self.verify_ctas = verify_ctas
        self.max_ctas_to_verify = max_ctas_to_verify
        self.progress_callback = progress_callback

        self.visited_urls: Set[str] = set()
        self.crawled_pages: List[Dict] = []
        self.navigation_graph: Optional[NavigationGraph] = None
        self._nav_builder: Optional[NavigationGraphBuilder] = None

        # Check if playwright is installed
        try:
            from playwright.sync_api import sync_playwright
            self.playwright_available = True
        except ImportError:
            self.playwright_available = False
            print("Warning: Playwright not installed. Run: pip install playwright")
            print("Then run: playwright install chromium")

        # Check interaction explorer availability
        if enable_interaction_capture and not INTERACTION_EXPLORER_AVAILABLE:
            print("Warning: Interaction explorer not available. Disabling interaction capture.")
            self.enable_interaction_capture = False

        # Check navigation graph availability
        if enable_navigation_graph and not NAVIGATION_GRAPH_AVAILABLE:
            print("Warning: Navigation graph not available. Disabling navigation analysis.")
            self.enable_navigation_graph = False

    def _parse_cookies(self, cookies: Any) -> Optional[List[Dict]]:
        """
        Parse cookies from various formats into Playwright format with security validation.

        Args:
            cookies: Cookies in string (JSON), list, or dict format

        Returns:
            List of cookie dicts with required fields: name, value, domain
            None if parsing fails
        """
        import json

        # Handle JSON string input
        if isinstance(cookies, str):
            try:
                cookies = json.loads(cookies)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse cookies JSON: {e}")
                return None

        # Handle domain-grouped dict format
        if isinstance(cookies, dict) and not all(k in cookies for k in ['name', 'value']):
            # This is a dict like {"example.com": [{"name": "sid", "value": "..."}]}
            cookie_list = []
            for domain, domain_cookies in cookies.items():
                if not isinstance(domain_cookies, list):
                    continue
                for cookie in domain_cookies:
                    if 'domain' not in cookie:
                        cookie = {**cookie, 'domain': domain if domain.startswith('.') else f'.{domain}'}
                    cookie_list.append(cookie)
            cookies = cookie_list

        # Handle single cookie dict (convert to list)
        if isinstance(cookies, dict) and 'name' in cookies and 'value' in cookies:
            cookies = [cookies]

        # Validate cookie list
        if not isinstance(cookies, list):
            print(f"Warning: Invalid cookies format: {type(cookies)}")
            return None

        # Security validation
        valid_cookies = []
        for cookie in cookies:
            if not isinstance(cookie, dict):
                continue

            if 'name' not in cookie or 'value' not in cookie:
                print(f"Warning: Skipping invalid cookie (missing name or value): {cookie}")
                continue

            # Security: Reject suspicious values (prevent injection)
            cookie_value = str(cookie['value'])
            if any(char in cookie_value for char in ['\n', '\r', ';', '\x00']):
                print(f"Warning: Rejected cookie '{cookie['name']}' with suspicious characters")
                continue

            # Warn about non-secure cookies
            if 'secure' in cookie and not cookie['secure']:
                print(f"Warning: Cookie '{cookie['name']}' not marked secure")

            valid_cookies.append(cookie)

        return valid_cookies if valid_cookies else None

    def normalize_url(self, url: str) -> str:
        """
        Normalize URL for comparison (remove fragments, trailing slashes).

        Args:
            url: URL to normalize

        Returns:
            Normalized URL string
        """
        parsed = urlparse(url)
        # Remove fragment and normalize path
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        # Remove trailing slash unless it's the root
        if normalized.endswith('/') and parsed.path != '/':
            normalized = normalized[:-1]
        return normalized

    def is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs are from the same domain.

        Args:
            url1: First URL
            url2: Second URL

        Returns:
            True if same domain, False otherwise
        """
        domain1 = urlparse(url1).netloc
        domain2 = urlparse(url2).netloc
        return domain1 == domain2

    def should_crawl(self, url: str, base_url: str) -> bool:
        """
        Determine if URL should be crawled.

        Args:
            url: URL to check
            base_url: Original starting URL

        Returns:
            True if should crawl, False otherwise
        """
        # Skip if already visited
        normalized = self.normalize_url(url)
        if normalized in self.visited_urls:
            return False

        # Skip if max pages reached
        if len(self.visited_urls) >= self.max_pages:
            return False

        # Skip if different domain
        if not self.is_same_domain(url, base_url):
            return False

        # Skip common non-page URLs
        skip_extensions = ['.pdf', '.zip', '.exe', '.dmg', '.jpg', '.png', '.gif', '.svg', '.mp4', '.mp3']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False

        # Skip common patterns
        skip_patterns = ['/cdn-cgi/', '/api/', '/_next/', '/assets/', '/static/']
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False

        return True

    def extract_links(self, page) -> List[str]:
        """
        Extract all links from a page.

        Args:
            page: Playwright page object

        Returns:
            List of absolute URLs
        """
        try:
            # Get all anchor tags
            links = page.eval_on_selector_all(
                'a[href]',
                'elements => elements.map(e => e.href)'
            )
            return [link for link in links if link]
        except Exception as e:
            print(f"    Warning: Failed to extract links: {e}")
            return []

    def _extract_navigation_async(self, page_info: Dict, page_role: str) -> None:
        """
        Extract navigation elements from a page asynchronously.

        Args:
            page_info: Dict with url, title
            page_role: Role from page classifier
        """
        if not self.enable_navigation_graph or not NAVIGATION_GRAPH_AVAILABLE:
            return

        if self._nav_builder is None:
            # Get base domain from first page
            parsed = urlparse(page_info.get('url', ''))
            self._nav_builder = NavigationGraphBuilder(base_domain=parsed.netloc)

        async def _async_extract():
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                    ]
                )

                # Build context options with same settings as main crawl (including anti-bot headers)
                context_options = {
                    'viewport': {"width": self.viewport_width, "height": self.viewport_height},
                    'user_agent': self.user_agent or (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
                    ),
                    'extra_http_headers': {
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-User': '?1',
                        'Sec-Fetch-Dest': 'document',
                        'Upgrade-Insecure-Requests': '1'
                    }
                }
                if self.user_agent:
                    context_options['user_agent'] = self.user_agent
                if self.storage_state and os.path.exists(self.storage_state):
                    context_options['storage_state'] = self.storage_state

                context = await browser.new_context(**context_options)

                # Add stealth script
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                """)

                # Add cookies if provided (and not using storage_state)
                if self.cookies and not self.storage_state:
                    try:
                        await context.add_cookies(self.cookies)
                    except Exception as e:
                        print(f"    Warning: Failed to add cookies in async context: {e}")

                page = await context.new_page()

                try:
                    await page.goto(page_info['url'], wait_until='networkidle', timeout=30000)
                    await self._nav_builder.extract_navigation(
                        page_info=page_info,
                        playwright_page=page,
                        page_role=page_role
                    )
                except Exception as e:
                    print(f"    Warning: Navigation extraction failed: {e}")
                finally:
                    await context.close()
                    await browser.close()

        # Run async code from sync context
        try:
            try:
                loop = asyncio.get_running_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _async_extract())
                    future.result()
            except RuntimeError:
                asyncio.run(_async_extract())
        except Exception as e:
            print(f"    Warning: Could not extract navigation: {e}")

    def _verify_ctas_async(self) -> List[Dict]:
        """
        Verify CTA destinations by clicking them.

        Returns:
            List of verified flow dicts
        """
        if not self.enable_navigation_graph or not self.verify_ctas:
            return []

        if self._nav_builder is None:
            return []

        async def _async_verify():
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                    ]
                )

                # Build context options with same settings as main crawl (including anti-bot headers)
                context_options = {
                    'viewport': {"width": self.viewport_width, "height": self.viewport_height},
                    'user_agent': self.user_agent or (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
                    ),
                    'extra_http_headers': {
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-User': '?1',
                        'Sec-Fetch-Dest': 'document',
                        'Upgrade-Insecure-Requests': '1'
                    }
                }
                if self.user_agent:
                    context_options['user_agent'] = self.user_agent
                if self.storage_state and os.path.exists(self.storage_state):
                    context_options['storage_state'] = self.storage_state

                context = await browser.new_context(**context_options)

                # Add stealth script
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                """)

                # Add cookies if provided (and not using storage_state)
                if self.cookies and not self.storage_state:
                    try:
                        await context.add_cookies(self.cookies)
                    except Exception as e:
                        print(f"    Warning: Failed to add cookies in async context: {e}")

                page = await context.new_page()

                try:
                    verified = await self._nav_builder.verify_cta_destinations(
                        page=page,
                        max_ctas=self.max_ctas_to_verify,
                        progress_callback=self.progress_callback
                    )
                    return verified
                except Exception as e:
                    print(f"    Warning: CTA verification failed: {e}")
                    return []
                finally:
                    await context.close()
                    await browser.close()

        # Run async code from sync context
        try:
            try:
                loop = asyncio.get_running_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _async_verify())
                    return future.result()
            except RuntimeError:
                return asyncio.run(_async_verify())
        except Exception as e:
            print(f"    Warning: Could not verify CTAs: {e}")
            return []

    def _run_interaction_capture(self, url: str) -> List[Dict]:
        """
        Run async interaction exploration and return captures.

        Uses a separate async Playwright context to capture interactions.

        Args:
            url: URL to explore

        Returns:
            List of serialized InteractionCapture dicts
        """
        if not self.enable_interaction_capture or not INTERACTION_EXPLORER_AVAILABLE:
            return []

        async def _async_explore():
            from playwright.async_api import async_playwright

            config = InteractionExplorerConfig(
                max_hover_elements=self.interaction_config.get('max_hover_elements', 20),
                max_click_elements=self.interaction_config.get('max_click_elements', 10),
                max_forms=self.interaction_config.get('max_forms', 3),
                capture_hover=self.interaction_config.get('capture_hover', True),
                capture_click=self.interaction_config.get('capture_click', True),
                capture_form=self.interaction_config.get('capture_form', True),
                capture_scroll=self.interaction_config.get('capture_scroll', True),
                capture_responsive=self.interaction_config.get('capture_responsive', True),
            )

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                    ]
                )

                # Build context options with same settings as main crawl (including anti-bot headers)
                context_options = {
                    'viewport': {"width": self.viewport_width, "height": self.viewport_height},
                    'user_agent': self.user_agent or (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
                    ),
                    'extra_http_headers': {
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-User': '?1',
                        'Sec-Fetch-Dest': 'document',
                        'Upgrade-Insecure-Requests': '1'
                    }
                }
                if self.user_agent:
                    context_options['user_agent'] = self.user_agent
                if self.storage_state and os.path.exists(self.storage_state):
                    context_options['storage_state'] = self.storage_state

                context = await browser.new_context(**context_options)

                # Add stealth script
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                """)

                # Add cookies if provided (and not using storage_state)
                if self.cookies and not self.storage_state:
                    try:
                        await context.add_cookies(self.cookies)
                    except Exception as e:
                        print(f"    Warning: Failed to add cookies in async context: {e}")

                page = await context.new_page()

                try:
                    await page.goto(url, wait_until='networkidle', timeout=30000)

                    explorer = InteractionExplorer(
                        page=page,
                        config=config,
                        progress_callback=self.progress_callback
                    )
                    captures = await explorer.run_full_exploration()

                    # Serialize captures for JSON storage
                    serialized = []
                    for capture in captures:
                        serialized.append({
                            'element_description': capture.element_description,
                            'interaction_type': capture.interaction_type,
                            'labels': capture.labels,
                            'screenshot_count': len(capture.screenshots),
                            'screenshots_base64': [
                                capture.to_base64_images()[i]['source']['data']
                                for i in range(len(capture.screenshots))
                            ],
                            'timestamp': capture.timestamp
                        })

                    return serialized

                except Exception as e:
                    print(f"    Warning: Interaction capture failed: {e}")
                    return []

                finally:
                    await context.close()
                    await browser.close()

        # Run async code from sync context
        try:
            # Check if there's already an event loop running
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, need to use nest_asyncio or similar
                # For simplicity, we'll create a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _async_explore())
                    return future.result()
            except RuntimeError:
                # No event loop running, we can use asyncio.run directly
                return asyncio.run(_async_explore())
        except Exception as e:
            print(f"    Warning: Could not run interaction capture: {e}")
            return []

    def capture_page(
        self,
        url: str,
        output_dir: str,
        page_number: int,
        playwright,
        context
    ) -> Optional[Dict]:
        """
        Capture a single page screenshot, metadata, and optionally interaction sequences.

        Args:
            url: URL to capture
            output_dir: Directory to save screenshot
            page_number: Sequential page number
            playwright: Playwright instance
            context: Browser context instance (with cookies/auth if provided)

        Returns:
            Dictionary with page data including:
                - url: Final URL after redirects
                - original_url: Requested URL
                - title: Page title
                - screenshot_path: Path to static screenshot
                - links: Extracted links for crawling
                - page_number: Sequential page number
                - interactions: List of interaction captures (if enabled)
            Returns None if failed
        """
        page = None
        try:
            page = context.new_page()

            print(f"  [{page_number}/{self.max_pages}] Loading: {url}")

            # Navigate to page with fallback wait strategies for bot-protected sites
            response = None
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    # Try networkidle first (best for most sites)
                    response = page.goto(url, wait_until='networkidle', timeout=30000)
                    break  # Success, exit retry loop
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"    Attempt {attempt + 1} failed, retrying in 2 seconds...")
                        time.sleep(2)
                        continue
                    print(f"    Warning: networkidle failed ({str(e)[:100]}), trying domcontentloaded...")
                    try:
                        # Fallback: wait for DOM only (works with bot-protected sites)
                        response = page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    except Exception as e2:
                        print(f"    Error: Failed to load page after {max_retries} attempts: {e2}")
                        return None

            # Log status but continue to screenshot (even error pages can be useful)
            if response:
                status = response.status
                if status >= 400:
                    print(f"    Warning: Got HTTP {status}")
                    if status == 403:
                        print(f"    >> Site may be blocking automated access (403 Forbidden)")
                        print(f"    >> Attempting to screenshot whatever loaded...")
                    elif status == 429:
                        print(f"    >> Rate limited (429 Too Many Requests)")
                        print(f"    >> Attempting to screenshot whatever loaded...")
                    # Don't return None - continue to screenshot whatever we got
            else:
                print(f"    Warning: No response received, but page may have loaded")
                # Continue anyway - page might have loaded despite missing response

            # Wait for any dynamic content
            time.sleep(self.wait_time)

            # Get page metadata
            title = page.title()
            page_url = page.url  # Actual URL after redirects

            # Take screenshot
            screenshot_name = f"page_{page_number}_{self._sanitize_filename(title)}.png"
            screenshot_path = Path(output_dir) / screenshot_name
            page.screenshot(path=str(screenshot_path), full_page=True)

            # Convert screenshot to base64 for embedding in reports
            screenshot_base64 = None
            try:
                from PIL import Image
                import io

                # Load the PNG screenshot
                with Image.open(screenshot_path) as img:
                    # Compress: resize if too large, reduce quality
                    max_width = 1200  # Reasonable for reports
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), Image.LANCZOS)

                    # Convert to RGB (required for JPEG)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = rgb_img

                    # Save as compressed JPEG
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=75, optimize=True)
                    screenshot_base64 = base64.standard_b64encode(output.getvalue()).decode('utf-8')

            except Exception as e:
                print(f"    Warning: Failed to encode screenshot to base64: {e}")
                screenshot_base64 = None

            # Extract links for further crawling
            links = self.extract_links(page)

            print(f"    >> Captured: {title}")
            print(f"    Found {len(links)} links")

            # Mark as visited
            self.visited_urls.add(self.normalize_url(page_url))

            # Build result
            result = {
                'url': page_url,
                'original_url': url,
                'title': title,
                'screenshot_path': str(screenshot_path),
                'screenshot_base64': screenshot_base64,  # ADD: Base64 for embedding in reports
                'links': links,
                'page_number': page_number,
                'interactions': [],
                'http_status': response.status if response else None,  # Track HTTP status
                'had_errors': response.status >= 400 if response else False  # Flag error pages
            }

            # Close sync page before async operations
            page.close()
            page = None

            # Extract navigation for flow analysis (uses separate async context)
            if self.enable_navigation_graph:
                # Simple page role detection (will be refined by page_classifier)
                page_role = self._detect_page_role(page_url, title)
                self._extract_navigation_async(
                    page_info={'url': page_url, 'title': title},
                    page_role=page_role
                )

            # Run interaction capture if enabled (uses separate async context)
            if self.enable_interaction_capture:
                print(f"    >> Capturing interactions...")
                interactions = self._run_interaction_capture(page_url)
                result['interactions'] = interactions

                if interactions:
                    total_screenshots = sum(i['screenshot_count'] for i in interactions)
                    print(f"    >> Captured {len(interactions)} interactions ({total_screenshots} screenshots)")

                    # Save interaction data to JSON
                    interaction_file = Path(output_dir) / f"page_{page_number}_interactions.json"
                    with open(interaction_file, 'w') as f:
                        json.dump(interactions, f, indent=2)
                    result['interactions_file'] = str(interaction_file)

            return result

        except Exception as e:
            print(f"    Error during page capture: {e}")

            # Even on error, try to capture SOMETHING if the page loaded at all
            try:
                if page and not page.is_closed():
                    print(f"    >> Attempting emergency screenshot despite error...")
                    title = page.title() or "Error Page"
                    page_url = page.url or url

                    screenshot_name = f"page_{page_number}_ERROR_{self._sanitize_filename(title)}.png"
                    screenshot_path = Path(output_dir) / screenshot_name
                    page.screenshot(path=str(screenshot_path), full_page=True, timeout=10000)

                    print(f"    >> Emergency screenshot captured: {title}")

                    # Return minimal result
                    return {
                        'url': page_url,
                        'original_url': url,
                        'title': title,
                        'screenshot_path': str(screenshot_path),
                        'screenshot_base64': None,  # Skip base64 encoding on errors
                        'links': [],
                        'page_number': page_number,
                        'interactions': [],
                        'http_status': None,
                        'had_errors': True,
                        'error_message': str(e)[:200]  # Include truncated error
                    }
            except Exception as e2:
                print(f"    >> Emergency screenshot also failed: {e2}")

            return None

        finally:
            if page and not page.is_closed():
                page.close()

    def _detect_page_role(self, url: str, title: str) -> str:
        """
        Simple page role detection based on URL and title.

        This is a lightweight version used during crawl. Full classification
        happens in page_classifier.py during analysis.

        Args:
            url: Page URL
            title: Page title

        Returns:
            Simple role string
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        title_lower = title.lower() if title else ""

        # Check for homepage
        if path in ['/', '', '/index.html', '/index.php']:
            return 'homepage'

        # Check common patterns
        patterns = {
            'about': ['/about', '/team', '/our-story', '/company'],
            'contact': ['/contact', '/reach-us', '/get-in-touch'],
            'product': ['/product', '/item', '/shop/'],
            'cart': ['/cart', '/basket', '/bag'],
            'checkout': ['/checkout', '/payment', '/order'],
            'help': ['/help', '/faq', '/support'],
        }

        for role, url_patterns in patterns.items():
            if any(p in path for p in url_patterns):
                return role

        return 'unknown'

    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Convert text to safe filename.

        Args:
            text: Text to sanitize
            max_length: Maximum filename length

        Returns:
            Safe filename string
        """
        # Remove invalid characters
        safe = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces with underscores
        safe = re.sub(r'[\s]+', '_', safe)
        # Truncate
        return safe[:max_length]

    def crawl(
        self,
        start_url: str,
        output_dir: str = "./web_crawl"
    ) -> Dict:
        """
        Crawl website starting from given URL.

        Args:
            start_url: Starting URL to crawl
            output_dir: Directory to save screenshots and data

        Returns:
            Dictionary with crawl results
        """
        if not self.playwright_available:
            raise RuntimeError(
                "Playwright not installed. Install with:\n"
                "  pip install playwright\n"
                "  playwright install chromium"
            )

        from playwright.sync_api import sync_playwright

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print("="*60)
        print("WEB CRAWLER - UI TRAPS ANALYZER")
        print("="*60)
        print()
        print(f"Starting URL: {start_url}")
        print(f"Max pages: {self.max_pages}")
        print(f"Max depth: {self.max_depth}")
        print(f"Output: {output_dir}")
        print(f"Interaction capture: {'ENABLED' if self.enable_interaction_capture else 'disabled'}")
        print()
        print("-"*60)
        print()

        with sync_playwright() as playwright:
            # Launch browser ONCE with args to bypass some bot detection
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',  # Hide automation
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )

            # Build browser context options with enhanced anti-bot detection
            context_options = {
                'viewport': {
                    'width': self.viewport_width,
                    'height': self.viewport_height
                },
                # Use realistic user agent if not provided
                'user_agent': self.user_agent or (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
                ),
                # Add realistic browser headers to avoid bot detection
                'extra_http_headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Upgrade-Insecure-Requests': '1'
                }
            }
            # Override user_agent if explicitly provided
            if self.user_agent:
                context_options['user_agent'] = self.user_agent

            # Add storage state if provided (includes cookies + localStorage)
            if self.storage_state and os.path.exists(self.storage_state):
                context_options['storage_state'] = self.storage_state

            # Create browser context with options
            context = browser.new_context(**context_options)

            # Add stealth script to hide automation markers
            context.add_init_script("""
                // Override navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Override Chrome runtime
                window.chrome = {
                    runtime: {}
                };

                // Override plugins to appear normal
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            """)

            # Add cookies if provided (and not using storage_state)
            if self.cookies and not self.storage_state:
                # Add default domain if cookies missing it
                parsed_url = urlparse(start_url)
                base_domain = f'.{parsed_url.netloc}'

                cookies_with_domain = []
                for cookie in self.cookies:
                    if 'domain' not in cookie:
                        cookie = {**cookie, 'domain': base_domain}
                    if 'url' not in cookie:
                        cookie = {**cookie, 'url': start_url}
                    cookies_with_domain.append(cookie)

                try:
                    context.add_cookies(cookies_with_domain)
                    print(f">> Added {len(cookies_with_domain)} cookies")
                except Exception as e:
                    print(f"Warning: Failed to add cookies: {e}")

            # Track URLs to crawl at each depth level
            urls_to_crawl = [(start_url, 0)]  # (url, depth)
            page_number = 0

            while urls_to_crawl and page_number < self.max_pages:
                current_url, depth = urls_to_crawl.pop(0)

                # Check if should crawl
                if not self.should_crawl(current_url, start_url):
                    continue

                # Skip if depth exceeded
                if depth > self.max_depth:
                    continue

                page_number += 1

                # Capture page
                page_data = self.capture_page(
                    current_url,
                    output_dir,
                    page_number,
                    playwright,
                    context  # CHANGED from browser
                )

                if page_data:
                    self.crawled_pages.append(page_data)

                    # Add links for next depth level
                    if depth < self.max_depth:
                        for link in page_data['links']:
                            if self.should_crawl(link, start_url):
                                urls_to_crawl.append((link, depth + 1))

            context.close()
            browser.close()

        print()
        print("-"*60)
        print()
        print(f">> Crawl complete!")
        print(f"  Pages captured: {len(self.crawled_pages)}")

        if len(self.crawled_pages) == 0:
            print()
            print("  ⚠️  WARNING: No pages were successfully crawled!")
            print("  Possible reasons:")
            print("    - Site is blocking automated access (bot detection)")
            print("    - Site requires authentication/cookies")
            print("    - Network timeout or connection issues")
            print("    - Site requires JavaScript that didn't load in time")
            print()
            print("  Troubleshooting:")
            print("    1. Check if site is accessible in a regular browser")
            print("    2. Try with authentication cookies if available")
            print("    3. Reduce max_pages or increase wait_time")
            print("    4. Check console output above for specific errors")
            print()
        else:
            print(f"  Screenshots saved to: {output_dir}")

            # Show which pages had errors
            error_pages = [p for p in self.crawled_pages if p.get('had_errors')]
            if error_pages:
                print()
                print(f"  ⚠️  {len(error_pages)} page(s) returned HTTP errors but were captured anyway:")
                for p in error_pages[:5]:  # Show first 5
                    status = p.get('http_status', 'unknown')
                    print(f"    - {p.get('title', 'Unknown')} (HTTP {status})")
                if len(error_pages) > 5:
                    print(f"    ... and {len(error_pages) - 5} more")
                print(f"  Note: These screenshots may show error pages rather than actual content")

        # Calculate interaction statistics
        total_interactions = 0
        total_interaction_screenshots = 0
        if self.enable_interaction_capture:
            for page_data in self.crawled_pages:
                interactions = page_data.get('interactions', [])
                total_interactions += len(interactions)
                total_interaction_screenshots += sum(i.get('screenshot_count', 0) for i in interactions)
            print(f"  Interactions captured: {total_interactions}")
            print(f"  Interaction screenshots: {total_interaction_screenshots}")

        # Build and verify navigation graph
        verified_ctas = []
        nav_graph_data = None
        if self.enable_navigation_graph and self._nav_builder:
            print()
            print(">> Building navigation graph...")

            # Verify CTAs by clicking them
            if self.verify_ctas:
                print(">> Verifying CTA destinations...")
                verified_ctas = self._verify_ctas_async()
                print(f"  CTAs verified: {len(verified_ctas)}")

            # Build final graph
            self.navigation_graph = self._nav_builder.build_graph()
            nav_summary = self.navigation_graph.get_summary()

            print(f"  Navigation graph built:")
            print(f"    - Pages mapped: {nav_summary['total_pages']}")
            print(f"    - Entry points: {len(nav_summary['entry_points'])}")
            print(f"    - Max depth: {nav_summary['max_depth']}")
            if nav_summary['orphan_pages']:
                print(f"    - Orphan pages: {len(nav_summary['orphan_pages'])}")

            # Serialize navigation graph
            nav_graph_data = self.navigation_graph.to_dict()

            # Save navigation graph to file
            nav_path = output_path / 'navigation_graph.json'
            with open(nav_path, 'w') as f:
                json.dump(nav_graph_data, f, indent=2)
            print(f"  Navigation graph saved to: {nav_path}")

        print()

        # Save crawl metadata
        metadata = {
            'start_url': start_url,
            'pages_crawled': len(self.crawled_pages),
            'interaction_capture_enabled': self.enable_interaction_capture,
            'navigation_graph_enabled': self.enable_navigation_graph,
            'total_interactions': total_interactions,
            'total_interaction_screenshots': total_interaction_screenshots,
            'verified_ctas': verified_ctas,
            'pages': self.crawled_pages
        }

        # Include navigation graph in metadata if built
        if nav_graph_data:
            metadata['navigation_graph'] = nav_graph_data

        metadata_path = output_path / 'crawl_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return metadata

    def get_navigation_graph(self) -> Optional[NavigationGraph]:
        """
        Get the navigation graph built during crawl.

        Returns:
            NavigationGraph object, or None if not built
        """
        return self.navigation_graph


def main():
    """Example usage of WebCrawler."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python web_crawler.py <url> [output_dir] [max_pages] [flags]")
        print("\nExample:")
        print("  python web_crawler.py https://example.com ./crawl 10")
        print("  python web_crawler.py https://example.com ./crawl 5 --interactions")
        print("  python web_crawler.py https://example.com ./crawl 5 --no-nav-graph")
        print("\nFlags:")
        print("  --interactions   Enable moment-by-moment interaction capture")
        print("  --no-nav-graph   Disable navigation graph building")
        print("  --no-verify-cta  Disable CTA destination verification")
        sys.exit(1)

    # Parse arguments
    url = sys.argv[1]
    enable_interactions = '--interactions' in sys.argv
    enable_nav_graph = '--no-nav-graph' not in sys.argv
    verify_ctas = '--no-verify-cta' not in sys.argv

    # Remove flags from args for positional parsing
    args = [a for a in sys.argv[2:] if not a.startswith('--')]
    output_dir = args[0] if len(args) > 0 else "./web_crawl"
    max_pages = int(args[1]) if len(args) > 1 else 10

    try:
        crawler = WebCrawler(
            max_pages=max_pages,
            enable_interaction_capture=enable_interactions,
            enable_navigation_graph=enable_nav_graph,
            verify_ctas=verify_ctas,
            interaction_config={
                'max_hover_elements': 10,  # Reduced for CLI testing
                'max_click_elements': 5,
                'max_forms': 2
            }
        )
        result = crawler.crawl(url, output_dir)

        print("Crawl Results:")
        for page in result['pages']:
            interactions_info = ""
            if page.get('interactions'):
                interactions_info = f" [{len(page['interactions'])} interactions]"
            print(f"  - {page['title']} ({page['url']}){interactions_info}")

        # Show navigation graph summary if built
        if result.get('navigation_graph'):
            nav = result['navigation_graph']
            print("\nNavigation Graph:")
            print(f"  Homepage: {nav.get('homepage_url', 'Unknown')}")
            print(f"  Verified CTAs: {len(result.get('verified_ctas', []))}")
            for cta in result.get('verified_ctas', [])[:5]:
                print(f"    - \"{cta['element_text']}\" → {cta['destination_url']}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
