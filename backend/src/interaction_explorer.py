"""
UI Traps Analyzer - Interaction Explorer Module

Copyright © 2009-present UI Traps LLC. All Rights Reserved.

CONFIDENTIAL AND PROPRIETARY
This code contains proprietary UI Tenets & Traps framework logic.
Unauthorized use, reproduction, or distribution is strictly prohibited.

This module enables moment-by-moment UI interaction analysis by:
1. Systematically capturing hover states on interactive elements
2. Recording click feedback and state transitions
3. Probing form validation behaviors
4. Capturing scroll-triggered UI changes
5. Testing responsive layout behavior across viewports
"""

import asyncio
import base64
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path


@dataclass
class InteractionCapture:
    """
    Represents a captured UI interaction sequence.

    Contains screenshots taken before, during, and after an interaction,
    along with metadata about the element and interaction type.
    """
    element_description: str
    interaction_type: str  # "hover", "click", "form", "scroll", "responsive", "navigation"
    screenshots: List[bytes] = field(default_factory=list)  # ordered: before, during, after
    labels: List[str] = field(default_factory=list)  # "before_hover", "during_hover", etc.
    dom_changes: Optional[str] = None
    video_path: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    # Navigation-specific fields
    source_url: Optional[str] = None
    destination_url: Optional[str] = None
    destination_title: Optional[str] = None

    def to_base64_images(self) -> List[Dict[str, Any]]:
        """
        Convert screenshots to base64-encoded image dicts for Claude API.

        Returns:
            List of image dicts ready for Claude vision API
        """
        images = []
        for screenshot in self.screenshots:
            images.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": base64.standard_b64encode(screenshot).decode('utf-8')
                }
            })
        return images


@dataclass
class InteractionExplorerConfig:
    """Configuration options for interaction exploration."""
    # Element limits (to control time/cost)
    max_hover_elements: int = 20
    max_click_elements: int = 10
    max_forms: int = 3
    max_navigation_ctas: int = 5  # Max CTAs to verify by clicking

    # Timing
    hover_delay_ms: int = 300      # Time to wait for hover CSS transitions
    click_immediate_ms: int = 150  # Time to capture immediate click feedback
    click_settle_ms: int = 1000    # Time to wait for click result to settle
    scroll_delay_ms: int = 400     # Time to wait after scroll
    viewport_delay_ms: int = 500   # Time to wait after viewport resize
    navigation_settle_ms: int = 2000  # Time to wait after navigation click

    # Capture toggles
    capture_hover: bool = True
    capture_click: bool = True
    capture_form: bool = True
    capture_scroll: bool = True
    capture_responsive: bool = True
    capture_navigation: bool = True  # Capture CTA navigation flows

    # Responsive viewports
    viewports: List[tuple] = field(default_factory=lambda: [
        ("mobile", 375, 812),
        ("tablet", 768, 1024),
        ("desktop", 1440, 900),
    ])

    # Video recording (for future Gemini integration)
    record_video: bool = False
    video_dir: Optional[str] = None


class InteractionExplorer:
    """
    Explores UI interactions and captures screenshot sequences.

    Uses Playwright to systematically interact with UI elements and
    capture before/during/after states for analysis.

    Usage:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)

            explorer = InteractionExplorer(page)
            captures = await explorer.run_full_exploration()
    """

    def __init__(
        self,
        page,  # Playwright Page object
        config: Optional[InteractionExplorerConfig] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ):
        """
        Initialize the interaction explorer.

        Args:
            page: Playwright page object (already navigated to target URL)
            config: Configuration options
            progress_callback: Optional callback(message, current, total) for progress updates
        """
        self.page = page
        self.config = config or InteractionExplorerConfig()
        self.progress_callback = progress_callback
        self.captures: List[InteractionCapture] = []
        self.original_viewport = None

    def _report_progress(self, message: str, current: int = 0, total: int = 0):
        """Report progress if callback is set."""
        if self.progress_callback:
            self.progress_callback(message, current, total)
        else:
            print(f"  {message}")

    async def screenshot_as_bytes(self, full_page: bool = False) -> bytes:
        """
        Take a screenshot and return as bytes.

        Args:
            full_page: Whether to capture full scrollable page

        Returns:
            Screenshot as PNG bytes
        """
        return await self.page.screenshot(full_page=full_page)

    async def _describe_element(self, element) -> str:
        """
        Generate a human-readable description of an element.

        Args:
            element: Playwright ElementHandle

        Returns:
            Description string like "<button> 'Submit' aria-label='Submit form'"
        """
        try:
            tag = await element.evaluate("e => e.tagName.toLowerCase()")
            text = (await element.text_content() or "").strip()[:50]
            aria = await element.get_attribute("aria-label") or ""
            role = await element.get_attribute("role") or ""

            desc = f"<{tag}>"
            if text:
                desc += f" '{text}'"
            if aria:
                desc += f" aria-label='{aria}'"
            if role:
                desc += f" role='{role}'"
            return desc
        except Exception:
            return "<element>"

    async def _is_element_interactive(self, element) -> bool:
        """Check if element appears to be interactive."""
        try:
            # Check if visible
            if not await element.is_visible():
                return False

            # Check bounding box (element has size)
            box = await element.bounding_box()
            if not box or box['width'] < 10 or box['height'] < 10:
                return False

            return True
        except Exception:
            return False

    async def explore_hover_states(self) -> List[InteractionCapture]:
        """
        Hover over interactive elements and capture state changes.

        Captures CSS hover states, tooltips, and visual feedback.

        Returns:
            List of InteractionCapture objects for hover interactions
        """
        if not self.config.capture_hover:
            return []

        self._report_progress("Exploring hover states...")
        hover_captures = []

        # Selectors for interactive elements that commonly have hover states
        interactive_selectors = [
            'button',
            'a',
            '[role="button"]',
            '[role="tab"]',
            '[role="menuitem"]',
            'input[type="submit"]',
            'input[type="button"]',
            '.btn',
            '.button',
            '[data-tooltip]',
            '[title]',
        ]

        elements_found = []
        for selector in interactive_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for el in elements:
                    if await self._is_element_interactive(el):
                        elements_found.append(el)
            except Exception:
                continue

        # Deduplicate and limit
        # (same element might match multiple selectors)
        seen_descriptions = set()
        unique_elements = []
        for el in elements_found:
            desc = await self._describe_element(el)
            if desc not in seen_descriptions:
                seen_descriptions.add(desc)
                unique_elements.append((el, desc))

        elements_to_check = unique_elements[:self.config.max_hover_elements]
        total = len(elements_to_check)

        for i, (element, description) in enumerate(elements_to_check):
            try:
                self._report_progress(f"Hover {i+1}/{total}: {description[:40]}", i+1, total)

                capture = InteractionCapture(
                    element_description=description,
                    interaction_type="hover"
                )

                # Capture before state
                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append("before_hover")

                # Hover over element
                await element.hover()
                await asyncio.sleep(self.config.hover_delay_ms / 1000)

                # Capture during hover
                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append("during_hover")

                # Move mouse away to reset
                await self.page.mouse.move(0, 0)

                hover_captures.append(capture)
                self.captures.append(capture)

            except Exception as e:
                print(f"    Warning: Failed to capture hover for {description}: {e}")
                continue

        return hover_captures

    async def explore_click_feedback(self) -> List[InteractionCapture]:
        """
        Click interactive elements and capture before/loading/after states.

        Only clicks elements that are likely safe (buttons not in forms,
        tabs, toggles). Avoids navigation links and form submissions.

        Returns:
            List of InteractionCapture objects for click interactions
        """
        if not self.config.capture_click:
            return []

        self._report_progress("Exploring click feedback...")
        click_captures = []

        # Selectors for clickable elements that are safe to test
        # (not navigation links, not form submits)
        safe_click_selectors = [
            'button:not([type="submit"])',
            '[role="button"]',
            '[role="tab"]',
            '[role="switch"]',
            '[role="checkbox"]',
            '.toggle',
            '.accordion-header',
            '.collapse-trigger',
            '.dropdown-trigger',
        ]

        elements_found = []
        for selector in safe_click_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for el in elements:
                    if await self._is_element_interactive(el):
                        elements_found.append(el)
            except Exception:
                continue

        # Deduplicate
        seen_descriptions = set()
        unique_elements = []
        for el in elements_found:
            desc = await self._describe_element(el)
            if desc not in seen_descriptions:
                seen_descriptions.add(desc)
                unique_elements.append((el, desc))

        elements_to_check = unique_elements[:self.config.max_click_elements]
        total = len(elements_to_check)

        original_url = self.page.url

        for i, (element, description) in enumerate(elements_to_check):
            try:
                self._report_progress(f"Click {i+1}/{total}: {description[:40]}", i+1, total)

                capture = InteractionCapture(
                    element_description=description,
                    interaction_type="click"
                )

                # Capture before state
                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append("before_click")

                # Click the element
                await element.click()

                # Capture immediate feedback (loading state, visual response)
                await asyncio.sleep(self.config.click_immediate_ms / 1000)
                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append("immediate_feedback")

                # Wait for any async operations to settle
                await asyncio.sleep(self.config.click_settle_ms / 1000)
                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append("after_settled")

                click_captures.append(capture)
                self.captures.append(capture)

                # Check if we navigated away
                if self.page.url != original_url:
                    self._report_progress(f"    Navigated to {self.page.url}, going back...")
                    await self.page.go_back()
                    await self.page.wait_for_load_state('networkidle')
                    original_url = self.page.url  # Update in case of redirects

            except Exception as e:
                print(f"    Warning: Failed to capture click for {description}: {e}")
                # Try to recover if we're on a different page
                try:
                    if self.page.url != original_url:
                        await self.page.go_back()
                        await self.page.wait_for_load_state('networkidle')
                except Exception:
                    pass
                continue

        return click_captures

    async def explore_form_validation(self) -> List[InteractionCapture]:
        """
        Submit forms with invalid data to capture validation states.

        Tests inline validation, error messages, and form feedback.

        Returns:
            List of InteractionCapture objects for form validation
        """
        if not self.config.capture_form:
            return []

        self._report_progress("Exploring form validation...")
        form_captures = []

        try:
            forms = await self.page.query_selector_all('form')
        except Exception:
            return []

        forms_to_check = forms[:self.config.max_forms]
        total = len(forms_to_check)

        for i, form in enumerate(forms_to_check):
            try:
                self._report_progress(f"Form {i+1}/{total}", i+1, total)

                # Check if form is visible
                if not await form.is_visible():
                    continue

                capture = InteractionCapture(
                    element_description=f"Form {i+1}",
                    interaction_type="form"
                )

                # Capture empty state
                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append("form_empty")

                # Try to find required fields and fill with invalid data
                inputs = await form.query_selector_all('input, textarea, select')
                for input_el in inputs:
                    try:
                        input_type = await input_el.get_attribute('type') or 'text'
                        required = await input_el.get_attribute('required')

                        if input_type == 'email':
                            # Invalid email to trigger validation
                            await input_el.fill('invalid-email')
                        elif input_type in ['text', 'password', 'tel']:
                            if required:
                                # Single character often triggers "too short" validation
                                await input_el.fill('x')
                        elif input_type == 'number':
                            await input_el.fill('-999999')
                    except Exception:
                        continue

                # Capture filled state
                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append("form_filled_invalid")

                # Try to submit to trigger validation
                submit_btn = await form.query_selector(
                    'button[type="submit"], input[type="submit"], button:not([type])'
                )

                if submit_btn and await submit_btn.is_visible():
                    try:
                        # Click submit but prevent actual form submission
                        await self.page.evaluate("""
                            document.querySelectorAll('form').forEach(f => {
                                f.addEventListener('submit', e => e.preventDefault(), {once: true});
                            });
                        """)
                        await submit_btn.click()
                        await asyncio.sleep(0.5)

                        # Capture validation errors
                        capture.screenshots.append(await self.screenshot_as_bytes())
                        capture.labels.append("validation_errors")
                    except Exception:
                        pass

                if len(capture.screenshots) >= 2:
                    form_captures.append(capture)
                    self.captures.append(capture)

            except Exception as e:
                print(f"    Warning: Failed to capture form validation: {e}")
                continue

        return form_captures

    async def explore_scroll_behavior(self) -> List[InteractionCapture]:
        """
        Scroll through the page and capture sticky headers, parallax, etc.

        Captures UI at different scroll positions to detect:
        - Sticky navigation
        - Parallax effects
        - Lazy-loaded content
        - Scroll-triggered animations

        Returns:
            List with single InteractionCapture containing scroll sequence
        """
        if not self.config.capture_scroll:
            return []

        self._report_progress("Exploring scroll behavior...")

        try:
            viewport_height = await self.page.evaluate("window.innerHeight")
            scroll_height = await self.page.evaluate("document.body.scrollHeight")
        except Exception:
            return []

        # Only capture scroll if page is scrollable
        if scroll_height <= viewport_height * 1.2:
            self._report_progress("  Page not scrollable, skipping")
            return []

        capture = InteractionCapture(
            element_description="Full page scroll",
            interaction_type="scroll"
        )

        positions = [0, 0.25, 0.5, 0.75, 1.0]

        for pct in positions:
            try:
                y = int(pct * (scroll_height - viewport_height))
                await self.page.evaluate(f"window.scrollTo(0, {y})")
                await asyncio.sleep(self.config.scroll_delay_ms / 1000)

                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append(f"scroll_{int(pct*100)}pct")

                self._report_progress(f"  Scroll position: {int(pct*100)}%")
            except Exception as e:
                print(f"    Warning: Failed at scroll {int(pct*100)}%: {e}")
                continue

        # Scroll back to top
        await self.page.evaluate("window.scrollTo(0, 0)")

        if capture.screenshots:
            self.captures.append(capture)
            return [capture]

        return []

    async def explore_responsive_behavior(self) -> List[InteractionCapture]:
        """
        Resize viewport and capture layout changes.

        Tests responsive breakpoints for:
        - Mobile layout
        - Tablet layout
        - Desktop layout

        Returns:
            List with single InteractionCapture containing responsive sequence
        """
        if not self.config.capture_responsive:
            return []

        self._report_progress("Exploring responsive behavior...")

        # Save original viewport
        try:
            self.original_viewport = await self.page.evaluate("""
                () => ({width: window.innerWidth, height: window.innerHeight})
            """)
        except Exception:
            self.original_viewport = {"width": 1920, "height": 1080}

        capture = InteractionCapture(
            element_description="Responsive layout",
            interaction_type="responsive"
        )

        for label, width, height in self.config.viewports:
            try:
                self._report_progress(f"  Viewport: {label} ({width}x{height})")

                await self.page.set_viewport_size({"width": width, "height": height})
                await asyncio.sleep(self.config.viewport_delay_ms / 1000)

                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append(f"viewport_{label}_{width}x{height}")
            except Exception as e:
                print(f"    Warning: Failed at viewport {label}: {e}")
                continue

        # Restore original viewport
        try:
            await self.page.set_viewport_size(self.original_viewport)
        except Exception:
            pass

        if capture.screenshots:
            self.captures.append(capture)
            return [capture]

        return []

    async def explore_navigation_flows(
        self,
        cta_elements: Optional[List[Dict]] = None
    ) -> List[InteractionCapture]:
        """
        Click CTAs and capture before/after page states for flow verification.

        This captures the actual user journey by clicking primary action buttons
        and recording what page they lead to. Essential for detecting:
        - Inviting Dead End traps (CTA leads to unexpected destination)
        - Flow issues (purchase button doesn't lead to purchase)
        - Misleading labels (button text doesn't match result)

        Args:
            cta_elements: Optional list of CTAs to verify. Each dict should have:
                - selector: CSS selector to find the element
                - text: Expected button/link text
                If None, will auto-detect CTAs on the page.

        Returns:
            List of InteractionCapture objects with source/destination info
        """
        if not self.config.capture_navigation:
            return []

        self._report_progress("Exploring navigation flows...")
        navigation_captures = []

        # Auto-detect CTAs if not provided
        if cta_elements is None:
            cta_elements = await self._detect_ctas()

        ctas_to_check = cta_elements[:self.config.max_navigation_ctas]
        total = len(ctas_to_check)
        original_url = self.page.url

        for i, cta in enumerate(ctas_to_check):
            try:
                selector = cta.get('selector', '')
                expected_text = cta.get('text', 'Unknown CTA')

                self._report_progress(
                    f"Navigation {i+1}/{total}: {expected_text[:30]}",
                    i + 1, total
                )

                # Find the element
                element = await self.page.query_selector(selector)
                if not element or not await element.is_visible():
                    continue

                capture = InteractionCapture(
                    element_description=f"CTA: {expected_text}",
                    interaction_type="navigation",
                    source_url=self.page.url
                )

                # Capture before state (source page)
                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append("source_page")

                # Get source page title
                source_title = await self.page.title()

                # Click the CTA
                await element.click()

                # Wait for navigation to complete
                await asyncio.sleep(self.config.navigation_settle_ms / 1000)
                try:
                    await self.page.wait_for_load_state('networkidle', timeout=5000)
                except Exception:
                    pass

                # Capture after state (destination page)
                capture.screenshots.append(await self.screenshot_as_bytes())
                capture.labels.append("destination_page")

                # Record destination info
                capture.destination_url = self.page.url
                capture.destination_title = await self.page.title()

                # Add context about the navigation
                navigated = capture.destination_url != capture.source_url
                capture.dom_changes = (
                    f"Source: {source_title} ({capture.source_url})\n"
                    f"CTA clicked: {expected_text}\n"
                    f"Destination: {capture.destination_title} ({capture.destination_url})\n"
                    f"Navigation occurred: {navigated}"
                )

                navigation_captures.append(capture)
                self.captures.append(capture)

                # Navigate back to continue testing other CTAs
                if navigated:
                    await self.page.goto(original_url, wait_until='networkidle', timeout=30000)

            except Exception as e:
                print(f"    Warning: Failed to capture navigation for {cta.get('text', 'CTA')}: {e}")
                # Try to recover
                try:
                    if self.page.url != original_url:
                        await self.page.goto(original_url, wait_until='networkidle', timeout=30000)
                except Exception:
                    pass
                continue

        return navigation_captures

    async def _detect_ctas(self) -> List[Dict]:
        """
        Auto-detect primary CTAs on the page.

        Looks for buttons and links that appear to be primary actions
        based on text content, styling, and position.
        """
        import re
        ctas = []

        # CTA text patterns
        cta_patterns = re.compile(
            r'\b(buy|purchase|order|shop|add to cart|checkout|get started|'
            r'sign up|register|subscribe|contact|book|schedule|download|'
            r'try|demo|learn more|see more|view|explore|start)\b',
            re.IGNORECASE
        )

        # Check buttons first (higher priority)
        button_selectors = [
            'button',
            '[role="button"]',
            'input[type="submit"]',
            '.btn',
            '.button',
            '.cta'
        ]

        for selector in button_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for el in elements:
                    if not await el.is_visible():
                        continue

                    text = (await el.text_content() or "").strip()
                    if not text:
                        text = await el.get_attribute('value') or ""

                    if text and cta_patterns.search(text) and len(text) < 50:
                        # Generate a selector for this specific element
                        tag = await el.evaluate("e => e.tagName.toLowerCase()")
                        classes = await el.get_attribute('class') or ""

                        # Build specific selector
                        if classes:
                            first_class = classes.split()[0]
                            specific_selector = f'{tag}.{first_class}:has-text("{text[:20]}")'
                        else:
                            specific_selector = f'{tag}:has-text("{text[:20]}")'

                        ctas.append({
                            'selector': specific_selector,
                            'text': text,
                            'type': 'button'
                        })
            except Exception:
                continue

        # Check links
        try:
            links = await self.page.query_selector_all('a[href]')
            for link in links:
                if not await link.is_visible():
                    continue

                text = (await link.text_content() or "").strip()
                href = await link.get_attribute('href') or ""

                # Skip non-navigation links
                if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    continue

                if text and cta_patterns.search(text) and len(text) < 50:
                    ctas.append({
                        'selector': f'a:has-text("{text[:20]}")',
                        'text': text,
                        'type': 'link',
                        'href': href
                    })
        except Exception:
            pass

        return ctas

    async def run_full_exploration(self) -> List[InteractionCapture]:
        """
        Run all interaction explorations.

        Executes each exploration type in sequence:
        1. Scroll behavior (to understand full page content)
        2. Hover states (on interactive elements)
        3. Click feedback (on safe elements)
        4. Form validation (on forms)
        5. Responsive behavior (viewport changes)

        Returns:
            List of all InteractionCapture objects
        """
        self._report_progress("Starting full interaction exploration...")
        start_time = time.time()

        # Reset captures
        self.captures = []

        # Run explorations in logical order
        await self.explore_scroll_behavior()
        await self.explore_hover_states()
        await self.explore_click_feedback()
        await self.explore_form_validation()
        await self.explore_responsive_behavior()
        await self.explore_navigation_flows()  # Cross-page flow verification

        duration = time.time() - start_time
        self._report_progress(
            f"Exploration complete: {len(self.captures)} interactions captured in {duration:.1f}s"
        )

        return self.captures

    def get_captures_by_type(self, interaction_type: str) -> List[InteractionCapture]:
        """Get all captures of a specific interaction type."""
        return [c for c in self.captures if c.interaction_type == interaction_type]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of captured interactions.

        Returns:
            Dict with counts by interaction type
        """
        summary = {
            "total_captures": len(self.captures),
            "total_screenshots": sum(len(c.screenshots) for c in self.captures),
            "by_type": {}
        }

        for capture in self.captures:
            t = capture.interaction_type
            if t not in summary["by_type"]:
                summary["by_type"][t] = {"count": 0, "screenshots": 0}
            summary["by_type"][t]["count"] += 1
            summary["by_type"][t]["screenshots"] += len(capture.screenshots)

        return summary


async def explore_page_interactions(
    url: str,
    config: Optional[InteractionExplorerConfig] = None,
    progress_callback: Optional[Callable[[str, int, int], None]] = None
) -> List[InteractionCapture]:
    """
    Convenience function to explore interactions on a URL.

    Args:
        url: URL to explore
        config: Optional configuration
        progress_callback: Optional progress callback

    Returns:
        List of InteractionCapture objects
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise RuntimeError(
            "Playwright not installed. Install with:\n"
            "  pip install playwright\n"
            "  playwright install chromium"
        )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)

            explorer = InteractionExplorer(
                page=page,
                config=config,
                progress_callback=progress_callback
            )
            captures = await explorer.run_full_exploration()

            return captures
        finally:
            await context.close()
            await browser.close()


# CLI for testing
if __name__ == '__main__':
    import sys

    async def main():
        if len(sys.argv) < 2:
            print("Usage: python interaction_explorer.py <url>")
            print("\nExample:")
            print("  python interaction_explorer.py https://example.com")
            sys.exit(1)

        url = sys.argv[1]
        print(f"\nExploring interactions on: {url}\n")
        print("=" * 60)

        config = InteractionExplorerConfig(
            max_hover_elements=10,  # Reduced for testing
            max_click_elements=5,
            max_forms=2
        )

        captures = await explore_page_interactions(url, config)

        print("\n" + "=" * 60)
        print("EXPLORATION SUMMARY")
        print("=" * 60)

        # Build summary
        by_type = {}
        for c in captures:
            if c.interaction_type not in by_type:
                by_type[c.interaction_type] = []
            by_type[c.interaction_type].append(c)

        for itype, caps in by_type.items():
            print(f"\n{itype.upper()} ({len(caps)} captures):")
            for cap in caps:
                print(f"  - {cap.element_description[:50]}")
                print(f"    Screenshots: {', '.join(cap.labels)}")

        total_screenshots = sum(len(c.screenshots) for c in captures)
        print(f"\nTotal: {len(captures)} interactions, {total_screenshots} screenshots")

    asyncio.run(main())
