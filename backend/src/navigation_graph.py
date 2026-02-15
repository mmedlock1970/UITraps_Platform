"""
Navigation Graph Builder - Site Flow Understanding

Builds a directed graph of page connections by extracting links, buttons,
and navigation elements. Enables flow-aware analysis by understanding:
- Which pages link to which
- Entry points vs. secondary pages
- CTA destinations (verified by clicking)
- User journey paths

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

import asyncio
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from urllib.parse import urljoin, urlparse
import time


@dataclass
class NavigationElement:
    """Represents a clickable navigation element on a page."""
    element_type: str  # "link", "button", "cta"
    text: str  # Visible text
    href: Optional[str]  # Target URL if available
    aria_label: Optional[str] = None
    is_primary_cta: bool = False  # Looks like a main action button
    selector: Optional[str] = None  # CSS selector to find this element
    verified_destination: Optional[str] = None  # Actual URL after clicking

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_type": self.element_type,
            "text": self.text,
            "href": self.href,
            "aria_label": self.aria_label,
            "is_primary_cta": self.is_primary_cta,
            "verified_destination": self.verified_destination
        }


@dataclass
class PageNode:
    """Represents a page in the navigation graph."""
    url: str
    title: str
    role: str  # From page_classifier
    outgoing_links: List[NavigationElement] = field(default_factory=list)
    incoming_from: Set[str] = field(default_factory=set)  # URLs that link TO this page
    is_entry_point: bool = False  # Can users land here directly?
    depth_from_home: int = -1  # -1 = not connected to home

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "role": self.role,
            "outgoing_links": [link.to_dict() for link in self.outgoing_links],
            "incoming_from": list(self.incoming_from),
            "is_entry_point": self.is_entry_point,
            "depth_from_home": self.depth_from_home
        }


@dataclass
class NavigationGraph:
    """
    Directed graph representing site navigation structure.

    Enables answering questions like:
    - "What pages can I reach from the homepage?"
    - "Where does the 'Order Now' button lead?"
    - "Is the About page reachable without seeing the buy button first?"
    """
    pages: Dict[str, PageNode] = field(default_factory=dict)
    homepage_url: Optional[str] = None
    verified_flows: List[Dict[str, Any]] = field(default_factory=list)

    def add_page(self, url: str, title: str, role: str) -> PageNode:
        """Add a page to the graph."""
        if url not in self.pages:
            self.pages[url] = PageNode(url=url, title=title, role=role)
        return self.pages[url]

    def add_link(self, from_url: str, to_url: str, element: NavigationElement):
        """Add a navigation link between pages."""
        if from_url in self.pages:
            self.pages[from_url].outgoing_links.append(element)
        if to_url in self.pages:
            self.pages[to_url].incoming_from.add(from_url)

    def get_pages_linking_to(self, url: str) -> List[PageNode]:
        """Get all pages that have links TO the given URL."""
        if url not in self.pages:
            return []
        incoming_urls = self.pages[url].incoming_from
        return [self.pages[u] for u in incoming_urls if u in self.pages]

    def get_path_from_home(self, target_url: str) -> List[str]:
        """
        Find the shortest path from homepage to target URL.
        Returns list of URLs representing the path, or empty if no path exists.
        """
        if not self.homepage_url or self.homepage_url not in self.pages:
            return []
        if target_url == self.homepage_url:
            return [self.homepage_url]

        # BFS to find shortest path
        visited = {self.homepage_url}
        queue = [(self.homepage_url, [self.homepage_url])]

        while queue:
            current_url, path = queue.pop(0)
            if current_url not in self.pages:
                continue

            for link in self.pages[current_url].outgoing_links:
                next_url = link.verified_destination or link.href
                if not next_url:
                    continue

                # Normalize URL
                next_url = self._normalize_url(next_url, current_url)

                if next_url == target_url:
                    return path + [next_url]

                if next_url not in visited and next_url in self.pages:
                    visited.add(next_url)
                    queue.append((next_url, path + [next_url]))

        return []

    def _normalize_url(self, url: str, base_url: str) -> str:
        """Normalize a URL relative to a base URL."""
        if url.startswith(('http://', 'https://')):
            return url
        return urljoin(base_url, url)

    def calculate_depths(self):
        """Calculate depth from homepage for all pages."""
        if not self.homepage_url or self.homepage_url not in self.pages:
            return

        self.pages[self.homepage_url].depth_from_home = 0
        self.pages[self.homepage_url].is_entry_point = True

        # BFS from homepage
        visited = {self.homepage_url}
        queue = [(self.homepage_url, 0)]

        while queue:
            current_url, depth = queue.pop(0)
            if current_url not in self.pages:
                continue

            for link in self.pages[current_url].outgoing_links:
                next_url = link.verified_destination or link.href
                if not next_url:
                    continue
                next_url = self._normalize_url(next_url, current_url)

                if next_url not in visited and next_url in self.pages:
                    visited.add(next_url)
                    self.pages[next_url].depth_from_home = depth + 1
                    queue.append((next_url, depth + 1))

    def get_page_context(self, url: str) -> Dict[str, Any]:
        """
        Get navigation context for a page to pass to the analyzer.

        This is the key output that tells the analyzer about a page's
        position in the site structure.
        """
        if url not in self.pages:
            return {"error": "Page not in navigation graph"}

        page = self.pages[url]
        path_from_home = self.get_path_from_home(url)
        incoming_pages = self.get_pages_linking_to(url)

        # Determine what CTAs users have already seen on the path to this page
        ctas_seen_before = []
        for path_url in path_from_home[:-1]:  # Exclude current page
            if path_url in self.pages:
                for link in self.pages[path_url].outgoing_links:
                    if link.is_primary_cta:
                        ctas_seen_before.append({
                            "text": link.text,
                            "on_page": self.pages[path_url].title,
                            "destination": link.verified_destination or link.href
                        })

        return {
            "url": url,
            "title": page.title,
            "role": page.role,
            "is_entry_point": page.is_entry_point,
            "depth_from_home": page.depth_from_home,
            "path_from_home": [
                {"url": u, "title": self.pages[u].title if u in self.pages else "Unknown"}
                for u in path_from_home
            ],
            "incoming_from": [
                {"url": p.url, "title": p.title, "role": p.role}
                for p in incoming_pages
            ],
            "ctas_seen_on_path": ctas_seen_before,
            "outgoing_ctas": [
                link.to_dict() for link in page.outgoing_links if link.is_primary_cta
            ]
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the entire graph."""
        return {
            "homepage_url": self.homepage_url,
            "pages": {url: page.to_dict() for url, page in self.pages.items()},
            "verified_flows": self.verified_flows
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the navigation structure."""
        total_pages = len(self.pages)
        entry_points = [p for p in self.pages.values() if p.is_entry_point]
        orphan_pages = [p for p in self.pages.values() if p.depth_from_home == -1]

        return {
            "total_pages": total_pages,
            "entry_points": [{"url": p.url, "title": p.title} for p in entry_points],
            "orphan_pages": [{"url": p.url, "title": p.title} for p in orphan_pages],
            "max_depth": max((p.depth_from_home for p in self.pages.values() if p.depth_from_home >= 0), default=0)
        }


# CTA detection patterns - buttons/links that look like primary actions
CTA_PATTERNS = [
    # Purchase-related
    r'\b(buy|purchase|order|shop|add to cart|checkout|get started)\b',
    # Sign-up related
    r'\b(sign up|register|create account|join|subscribe|start free)\b',
    # Contact-related
    r'\b(contact|get in touch|request|inquire|book|schedule)\b',
    # Download/action
    r'\b(download|try|demo|learn more|see more|view|explore)\b',
]

CTA_PATTERN = re.compile('|'.join(CTA_PATTERNS), re.IGNORECASE)


class NavigationGraphBuilder:
    """
    Builds a NavigationGraph by extracting links and CTAs from pages.

    Usage:
        builder = NavigationGraphBuilder()

        # Add pages as they're crawled
        for page in crawled_pages:
            await builder.extract_navigation(page, playwright_page)

        # Build the graph
        graph = builder.build_graph()

        # Verify key CTAs by clicking them
        await builder.verify_cta_destinations(playwright_page)
    """

    def __init__(self, base_domain: Optional[str] = None):
        """
        Initialize the builder.

        Args:
            base_domain: Restrict graph to this domain (e.g., "example.com")
        """
        self.base_domain = base_domain
        self.graph = NavigationGraph()
        self.ctas_to_verify: List[Tuple[str, NavigationElement]] = []  # (page_url, element)

    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain."""
        if not self.base_domain:
            return True
        try:
            parsed = urlparse(url)
            return parsed.netloc == self.base_domain or parsed.netloc == ""
        except Exception:
            return False

    def _is_cta(self, text: str, element_type: str, classes: str = "") -> bool:
        """Determine if an element looks like a primary CTA."""
        if not text:
            return False

        # Check text against CTA patterns
        if CTA_PATTERN.search(text):
            return True

        # Check for button-like classes that suggest primary action
        cta_classes = ['cta', 'primary', 'action', 'hero', 'main-btn', 'buy-btn']
        if any(c in classes.lower() for c in cta_classes):
            return True

        # Buttons with short, action-oriented text are often CTAs
        if element_type == "button" and len(text.split()) <= 3:
            action_words = ['go', 'start', 'begin', 'get', 'try', 'see', 'view', 'buy', 'shop']
            if any(text.lower().startswith(w) for w in action_words):
                return True

        return False

    async def extract_navigation(
        self,
        page_info: Dict[str, Any],
        playwright_page,
        page_role: str = "unknown"
    ) -> PageNode:
        """
        Extract navigation elements from a page.

        Args:
            page_info: Dict with url, title keys
            playwright_page: Playwright Page object
            page_role: Role from page_classifier (e.g., "homepage", "product")

        Returns:
            PageNode with extracted navigation
        """
        url = page_info.get("url", "")
        title = page_info.get("title", "")

        # Add page to graph
        node = self.graph.add_page(url, title, page_role)

        # Check if this is the homepage
        parsed = urlparse(url)
        if parsed.path in ['/', '', '/index.html', '/index.php'] or page_role == "homepage":
            self.graph.homepage_url = url
            node.is_entry_point = True

        # Extract all links
        links = await self._extract_links(playwright_page, url)

        # Extract buttons (may trigger navigation via JS)
        buttons = await self._extract_buttons(playwright_page, url)

        # Combine and deduplicate
        all_elements = links + buttons
        seen_hrefs = set()

        for element in all_elements:
            href = element.href
            if href and href in seen_hrefs:
                continue
            if href:
                seen_hrefs.add(href)

            node.outgoing_links.append(element)

            # Track CTAs for later verification
            if element.is_primary_cta:
                self.ctas_to_verify.append((url, element))

            # Add to graph edges if we know the destination
            if href and self._is_same_domain(href):
                dest_url = urljoin(url, href)
                # We'll add the destination page later when it's crawled
                # For now, just record that this page links there

        return node

    async def _extract_links(self, page, base_url: str) -> List[NavigationElement]:
        """Extract all anchor links from the page."""
        elements = []

        try:
            links = await page.query_selector_all('a[href]')

            for link in links:
                try:
                    href = await link.get_attribute('href')
                    if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                        continue

                    text = (await link.text_content() or "").strip()
                    aria_label = await link.get_attribute('aria-label')
                    classes = await link.get_attribute('class') or ""

                    # Skip empty or very long text (probably not navigation)
                    if not text and not aria_label:
                        continue
                    if len(text) > 100:
                        continue

                    display_text = text or aria_label or ""
                    is_cta = self._is_cta(display_text, "link", classes)

                    elements.append(NavigationElement(
                        element_type="link",
                        text=display_text[:50],  # Truncate long text
                        href=href,
                        aria_label=aria_label,
                        is_primary_cta=is_cta
                    ))
                except Exception:
                    continue

        except Exception:
            pass

        return elements

    async def _extract_buttons(self, page, base_url: str) -> List[NavigationElement]:
        """Extract buttons that might trigger navigation."""
        elements = []

        button_selectors = [
            'button',
            'input[type="button"]',
            'input[type="submit"]',
            '[role="button"]',
            '.btn',
            '.button'
        ]

        for selector in button_selectors:
            try:
                buttons = await page.query_selector_all(selector)

                for button in buttons:
                    try:
                        # Skip if not visible
                        if not await button.is_visible():
                            continue

                        text = (await button.text_content() or "").strip()
                        if not text:
                            # Try value attribute for input buttons
                            text = await button.get_attribute('value') or ""
                        aria_label = await button.get_attribute('aria-label')
                        classes = await button.get_attribute('class') or ""

                        display_text = text or aria_label or ""
                        if not display_text or len(display_text) > 50:
                            continue

                        is_cta = self._is_cta(display_text, "button", classes)

                        # Only track buttons that look like CTAs (likely to navigate)
                        if is_cta:
                            elements.append(NavigationElement(
                                element_type="button",
                                text=display_text,
                                href=None,  # Buttons don't have href, need to click to verify
                                aria_label=aria_label,
                                is_primary_cta=True
                            ))
                    except Exception:
                        continue
            except Exception:
                continue

        return elements

    async def verify_cta_destinations(
        self,
        page,
        max_ctas: int = 10,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Verify where CTAs actually lead by clicking them.

        Args:
            page: Playwright Page object
            max_ctas: Maximum number of CTAs to verify
            progress_callback: Optional callback(message, current, total)

        Returns:
            List of verified CTA flows with before/after info
        """
        verified = []
        ctas = self.ctas_to_verify[:max_ctas]

        for i, (source_url, element) in enumerate(ctas):
            if progress_callback:
                progress_callback(
                    f"Verifying CTA: {element.text}",
                    i + 1,
                    len(ctas)
                )

            try:
                # Navigate to the source page
                await page.goto(source_url, wait_until='networkidle', timeout=30000)

                # Find the element
                if element.href:
                    # For links, we can find by href
                    selector = f'a[href="{element.href}"]'
                else:
                    # For buttons, find by text content
                    selector = f'button:has-text("{element.text}"), [role="button"]:has-text("{element.text}")'

                target = await page.query_selector(selector)
                if not target:
                    continue

                # Record before state
                before_url = page.url

                # Click the element
                await target.click()

                # Wait for navigation
                await asyncio.sleep(1)
                try:
                    await page.wait_for_load_state('networkidle', timeout=5000)
                except Exception:
                    pass

                # Record after state
                after_url = page.url
                after_title = await page.title()

                # Update the element with verified destination
                element.verified_destination = after_url

                flow_result = {
                    "source_url": source_url,
                    "element_text": element.text,
                    "element_type": element.element_type,
                    "destination_url": after_url,
                    "destination_title": after_title,
                    "navigated": before_url != after_url
                }

                verified.append(flow_result)
                self.graph.verified_flows.append(flow_result)

                # Update graph with verified destination
                if after_url != before_url and self._is_same_domain(after_url):
                    # Add destination page to graph if not already there
                    if after_url not in self.graph.pages:
                        self.graph.add_page(after_url, after_title, "unknown")
                    self.graph.pages[after_url].incoming_from.add(source_url)

            except Exception as e:
                print(f"Failed to verify CTA '{element.text}': {e}")
                continue

        return verified

    def build_graph(self) -> NavigationGraph:
        """
        Finalize and return the navigation graph.

        Call this after all pages have been extracted.
        """
        # Calculate depths from homepage
        self.graph.calculate_depths()

        return self.graph

    def get_graph(self) -> NavigationGraph:
        """Get the current state of the graph."""
        return self.graph


def generate_flow_context_prompt(nav_context: Dict[str, Any]) -> str:
    """
    Generate prompt text explaining the page's position in the site flow.

    This is added to the analyzer prompt to prevent false positives
    about missing elements that exist on earlier pages in the flow.
    """
    lines = []

    lines.append("=== PAGE NAVIGATION CONTEXT ===")
    lines.append(f"Page: {nav_context.get('title', 'Unknown')}")
    lines.append(f"Role: {nav_context.get('role', 'unknown')}")
    lines.append(f"URL: {nav_context.get('url', '')}")
    lines.append("")

    # Entry point status
    if nav_context.get('is_entry_point'):
        lines.append("ENTRY POINT: Yes - users may land here directly")
    else:
        depth = nav_context.get('depth_from_home', -1)
        if depth > 0:
            lines.append(f"ENTRY POINT: No - this is {depth} click(s) from the homepage")
            lines.append("Users arriving at this page have already navigated through the site.")
        elif depth == -1:
            lines.append("ENTRY POINT: Unknown - page may be orphaned")

    # Path from home
    path = nav_context.get('path_from_home', [])
    if len(path) > 1:
        lines.append("")
        lines.append("PATH TO THIS PAGE:")
        for i, step in enumerate(path):
            prefix = "  " + ("→ " if i > 0 else "• ")
            lines.append(f"{prefix}{step.get('title', 'Unknown')} ({step.get('url', '')})")

    # CTAs already seen
    ctas_seen = nav_context.get('ctas_seen_on_path', [])
    if ctas_seen:
        lines.append("")
        lines.append("CTAs USERS HAVE ALREADY SEEN:")
        for cta in ctas_seen:
            lines.append(f"  • \"{cta.get('text', '')}\" on {cta.get('on_page', '')} → {cta.get('destination', '')}")
        lines.append("")
        lines.append("IMPORTANT: Do NOT flag missing purchase/contact options if users have")
        lines.append("already seen these CTAs on their path to this page.")

    # Incoming links
    incoming = nav_context.get('incoming_from', [])
    if incoming:
        lines.append("")
        lines.append("PAGES LINKING TO THIS PAGE:")
        for page in incoming:
            lines.append(f"  • {page.get('title', 'Unknown')} ({page.get('role', 'unknown')})")

    lines.append("")
    lines.append("=== END NAVIGATION CONTEXT ===")
    lines.append("")

    return "\n".join(lines)
