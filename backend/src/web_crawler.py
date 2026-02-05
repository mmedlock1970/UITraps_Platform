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
"""

import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
import json


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
        user_agent: Optional[str] = None
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
        """
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.wait_time = wait_time
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.user_agent = user_agent

        self.visited_urls: Set[str] = set()
        self.crawled_pages: List[Dict] = []

        # Check if playwright is installed
        try:
            from playwright.sync_api import sync_playwright
            self.playwright_available = True
        except ImportError:
            self.playwright_available = False
            print("Warning: Playwright not installed. Run: pip install playwright")
            print("Then run: playwright install chromium")

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

    def capture_page(
        self,
        url: str,
        output_dir: str,
        page_number: int,
        playwright,
        browser
    ) -> Optional[Dict]:
        """
        Capture a single page screenshot and metadata.

        Args:
            url: URL to capture
            output_dir: Directory to save screenshot
            page_number: Sequential page number
            playwright: Playwright instance
            browser: Browser instance

        Returns:
            Dictionary with page data or None if failed
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

            return {
                'url': page_url,
                'original_url': url,
                'title': title,
                'screenshot_path': str(screenshot_path),
                'links': links,
                'page_number': page_number
            }

        except Exception as e:
            print(f"    Error: {e}")
            return None

        finally:
            if page:
                page.close()

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
        print()

        # Save crawl metadata
        metadata = {
            'start_url': start_url,
            'pages_crawled': len(self.crawled_pages),
            'pages': self.crawled_pages
        }

        metadata_path = output_path / 'crawl_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return metadata


def main():
    """Example usage of WebCrawler."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python web_crawler.py <url> [output_dir] [max_pages]")
        print("\nExample:")
        print("  python web_crawler.py https://example.com ./crawl 10")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./web_crawl"
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    try:
        crawler = WebCrawler(max_pages=max_pages)
        result = crawler.crawl(url, output_dir)

        print("Crawl Results:")
        for page in result['pages']:
            print(f"  - {page['title']} ({page['url']})")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
