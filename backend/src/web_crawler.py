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
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": self.viewport_width, "height": self.viewport_height}
                )
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
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": self.viewport_width, "height": self.viewport_height}
                )
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
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": self.viewport_width, "height": self.viewport_height}
                )
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
        browser
    ) -> Optional[Dict]:
        """
        Capture a single page screenshot, metadata, and optionally interaction sequences.

        Args:
            url: URL to capture
            output_dir: Directory to save screenshot
            page_number: Sequential page number
            playwright: Playwright instance
            browser: Browser instance

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
            page = browser.new_page()

            print(f"  [{page_number}/{self.max_pages}] Loading: {url}")

            # Navigate to page
            response = page.goto(url, wait_until='networkidle', timeout=30000)

            if not response or response.status >= 400:
                print(f"    Warning: Failed to load (status {response.status if response else 'unknown'})")
                return None

            # Wait for any dynamic content
            time.sleep(self.wait_time)

            # Get page metadata
            title = page.title()
            page_url = page.url  # Actual URL after redirects

            # Take screenshot
            screenshot_name = f"page_{page_number}_{self._sanitize_filename(title)}.png"
            screenshot_path = Path(output_dir) / screenshot_name
            page.screenshot(path=str(screenshot_path), full_page=True)

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
                'links': links,
                'page_number': page_number,
                'interactions': []
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
            print(f"    Error: {e}")
            return None

        finally:
            if page:
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
            # Launch browser
            browser = playwright.chromium.launch(headless=True)

            # Set up browser context
            context_options = {
                'viewport': {
                    'width': self.viewport_width,
                    'height': self.viewport_height
                }
            }
            if self.user_agent:
                context_options['user_agent'] = self.user_agent

            browser = playwright.chromium.launch(headless=True)

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
                    browser
                )

                if page_data:
                    self.crawled_pages.append(page_data)

                    # Add links for next depth level
                    if depth < self.max_depth:
                        for link in page_data['links']:
                            if self.should_crawl(link, start_url):
                                urls_to_crawl.append((link, depth + 1))

            browser.close()

        print()
        print("-"*60)
        print()
        print(f">> Crawl complete!")
        print(f"  Pages captured: {len(self.crawled_pages)}")
        print(f"  Screenshots saved to: {output_dir}")

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
