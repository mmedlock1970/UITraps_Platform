"""
Platform-aware analysis context for UI Traps Analyzer.

Provides platform-specific prompt sections that get injected into analysis
prompts based on the platform type (iOS, Android, desktop, etc.).

Copyright (c) 2009-present UI Traps LLC. All Rights Reserved.
"""

from typing import Optional


# Platform-specific analysis guidance
# These get appended to the system prompt based on user's platform selection
PLATFORM_CONTEXT = {
    "web": """## PLATFORM: WEB APPLICATION
Apply standard web UI conventions:
- Navigation: standard nav patterns, breadcrumbs, browser back button behavior
- Components: links, buttons, forms, dropdowns, modals
- Responsive: should work across viewport sizes
- Accessibility: WCAG guidelines, keyboard navigation, screen reader support
- Interactions: hover states, focus indicators, click feedback""",

    "ios_native": """## PLATFORM: iOS NATIVE APPLICATION
Apply Apple Human Interface Guidelines (HIG) expectations:
- Navigation: UINavigationController patterns, tab bars, back buttons top-left
- Components: SF Symbols, standard UIKit/SwiftUI controls, sheets, action sheets
- Typography: San Francisco font, Dynamic Type support expected
- Layout: Safe Area compliance, notch/Dynamic Island avoidance
- Interactions: swipe-to-go-back gesture, pull-to-refresh, haptic feedback conventions
- Touch targets: minimum 44pt tap targets required
- Accessibility: VoiceOver support expected

COMMON iOS-SPECIFIC TRAPS:
- PHYSICAL CHALLENGE: Touch targets below 44pt
- FEEDBACK FAILURE: Missing haptic/visual response to gestures
- INCONSISTENT APPEARANCE: Non-standard navigation patterns""",

    "android_native": """## PLATFORM: ANDROID NATIVE APPLICATION
Apply Material Design 3 (Material You) expectations:
- Navigation: bottom navigation bar, navigation drawer, top app bar with back arrow
- Components: FABs, chips, snackbars, bottom sheets, Material 3 components
- Typography: Roboto/system font, Material type scale
- Layout: edge-to-edge design, proper inset handling, foldable awareness
- Interactions: predictive back gesture, ripple feedback, haptic patterns
- Touch targets: minimum 48dp touch targets required
- Theming: Material 3 color theming, dynamic color from wallpaper

COMMON ANDROID-SPECIFIC TRAPS:
- PHYSICAL CHALLENGE: Touch targets below 48dp
- INCONSISTENT APPEARANCE: Mixing iOS patterns with Android (e.g., iOS-style back arrows)
- FEEDBACK FAILURE: Missing ripple effects on interactive elements""",

    "desktop_windows": """## PLATFORM: WINDOWS DESKTOP APPLICATION
Apply Windows UI conventions:
- Navigation: menu bars, ribbon UI, or hamburger navigation
- Window controls: standard title bar with min/max/close, resizable windows
- Controls: standard Win32/WinUI controls, context menus (right-click)
- Interactions: keyboard shortcuts expected, drag-and-drop, hover states, tooltips
- Layout: resizable windows, snap layouts support, high DPI scaling
- Patterns: Settings pages, flyouts, dialogs, toast notifications

COMMON DESKTOP-SPECIFIC TRAPS:
- MEMORY CHALLENGE: No keyboard shortcuts for frequent actions
- INVISIBLE ELEMENT: Important functions hidden in deep menus
- PHYSICAL CHALLENGE: Tiny click targets sized for touch on a mouse-driven UI""",

    "desktop_macos": """## PLATFORM: macOS DESKTOP APPLICATION
Apply macOS Human Interface Guidelines expectations:
- Navigation: menu bar (always present at top of screen), toolbar, sidebar/source list
- Window controls: traffic light buttons (close/minimize/fullscreen) top-left
- Controls: standard AppKit/SwiftUI controls, SF Symbols
- Interactions: right-click context menus, keyboard shortcuts, trackpad gestures, Force Touch
- Layout: resizable windows, full screen mode, split view support
- Patterns: preference windows (not "Settings"), sheets, popovers
- Typography: San Francisco, system font sizes

COMMON macOS-SPECIFIC TRAPS:
- INCONSISTENT APPEARANCE: Windows-style UI patterns on Mac
- MEMORY CHALLENGE: Missing standard keyboard shortcuts (Cmd+C/V/Z)
- INVISIBLE ELEMENT: Functions missing from menu bar""",

    "desktop_linux": """## PLATFORM: LINUX DESKTOP APPLICATION
Apply desktop UI conventions (GNOME/KDE/GTK):
- Navigation: header bars (GNOME) or menu bars depending on toolkit
- Controls: standard GTK/Qt controls, icon themes
- Interactions: keyboard shortcuts, right-click menus, drag-and-drop
- Layout: resizable windows, tiling window manager support
- Patterns: standard dialog patterns, system notifications

Focus on general desktop usability rather than platform-specific conventions,
as Linux has multiple desktop environments.""",

    "mobile_app": """## PLATFORM: MOBILE APPLICATION (GENERIC)
Apply mobile UI conventions:
- Touch interactions: tap, swipe, pinch-zoom gestures
- Touch targets: minimum 44-48pt for comfortable tapping
- Navigation: bottom navigation, hamburger menus, gesture navigation
- Layout: single-column layouts, thumb-zone awareness
- Content: mobile-optimized content density, readable text without zooming
- Feedback: immediate visual/haptic response to touches

If you can identify whether this is iOS or Android, apply those specific guidelines.""",

    "desktop_app": """## PLATFORM: DESKTOP APPLICATION (GENERIC)
Apply desktop UI conventions:
- Mouse interactions: click, right-click, hover, drag-and-drop
- Keyboard: shortcuts expected for common actions, Tab navigation
- Windows: resizable, minimizable, multiple windows possible
- Menus: menu bar or context menus for commands
- Controls: standard desktop widgets (buttons, inputs, dropdowns)

Consider both mouse and keyboard users.""",

    "game": """## PLATFORM: VIDEO GAME INTERFACE
LIMITED ANALYSIS - Only analyze static UI elements:

CAN ANALYZE:
- Main menus, pause menus, settings screens
- Inventory, character, or stat screens
- HUD elements (health bars, minimaps, score displays)
- Tutorial screens and help overlays
- In-game shops or transaction screens
- Loading screens and progress indicators

CANNOT ANALYZE (DO NOT FLAG):
- Real-time gameplay (requires motion analysis)
- Animation quality or timing
- Sound/haptic feedback

BE CONSERVATIVE WITH:
- UNCOMPREHENDED ELEMENT: Game-specific terms (mana, XP, loot) are intentional
- Fantasy/sci-fi terminology is a stylistic choice, not a trap""",

    "pdf_document": """## PLATFORM: PDF / DOCUMENT INTERFACE
Apply document design heuristics:
- Reading flow: Is the reading order logical? For multi-column layouts, is flow clear?
- Typography: Clear heading hierarchy (H1/H2/H3), readable body text (min 10pt)
- Whitespace: Adequate spacing between sections, appropriate page density
- Forms: If form fields exist, are they clearly labeled and logically grouped?
- Accessibility: Proper heading structure, alt text for images, logical reading order
- Navigation: For long documents - table of contents, page numbers, running headers?

DOCUMENT-SPECIFIC CONSIDERATIONS:
- Print vs screen: Is this optimized for print or screen reading?
- Form factor: Consider how document will be consumed (phone, tablet, desktop, print)""",

    "other": """## PLATFORM: OTHER/UNSPECIFIED
Apply general UI/UX principles:
- Visual hierarchy: Is information organized by importance?
- Consistency: Do similar elements look and behave similarly?
- Feedback: Does the interface respond to user actions?
- Affordances: Is it clear what elements are interactive?
- Error prevention: Does the design prevent user mistakes?

Analyze based on general usability principles since specific platform conventions
may not apply.""",
}


def get_platform_prompt_section(platform: str) -> str:
    """
    Return the platform-specific prompt section for a given platform type.

    Args:
        platform: Platform type string (e.g., 'ios_native', 'android_native', 'web')

    Returns:
        Platform-specific prompt section to append to analysis prompt,
        or empty string if platform not recognized.
    """
    context = PLATFORM_CONTEXT.get(platform, "")
    if not context:
        # Fall back to generic based on partial match
        if "ios" in platform.lower():
            context = PLATFORM_CONTEXT.get("ios_native", "")
        elif "android" in platform.lower():
            context = PLATFORM_CONTEXT.get("android_native", "")
        elif "mac" in platform.lower():
            context = PLATFORM_CONTEXT.get("desktop_macos", "")
        elif "windows" in platform.lower():
            context = PLATFORM_CONTEXT.get("desktop_windows", "")
        elif "linux" in platform.lower():
            context = PLATFORM_CONTEXT.get("desktop_linux", "")
        elif "mobile" in platform.lower():
            context = PLATFORM_CONTEXT.get("mobile_app", "")
        elif "desktop" in platform.lower():
            context = PLATFORM_CONTEXT.get("desktop_app", "")

    return f"\n\n{context}\n" if context else ""


def get_analysis_depth_label(input_type: str) -> str:
    """
    Return a human-readable label describing the analysis depth.

    Args:
        input_type: Type of input being analyzed

    Returns:
        Human-readable analysis type label
    """
    labels = {
        "single_image": "Single Screenshot Analysis",
        "multi_image": "Multi-Screenshot Analysis",
        "video": "Video Recording Analysis",
        "screenshot_sequence": "Interaction Flow Analysis",
        "figma": "Figma Design Analysis",
        "url": "Website Crawl Analysis",
        "pdf": "PDF Document Analysis",
    }
    return labels.get(input_type, "UI Analysis")


def get_platform_display_name(platform: str) -> str:
    """
    Get a user-friendly display name for a platform type.

    Args:
        platform: Platform type string

    Returns:
        Human-readable platform name
    """
    names = {
        "web": "Web Application",
        "ios_native": "iOS Native App",
        "android_native": "Android Native App",
        "desktop_windows": "Windows Desktop App",
        "desktop_macos": "macOS Desktop App",
        "desktop_linux": "Linux Desktop App",
        "mobile_app": "Mobile App",
        "desktop_app": "Desktop App",
        "game": "Video Game",
        "pdf_document": "PDF Document",
        "other": "Other",
    }
    return names.get(platform, platform.replace("_", " ").title())


# List of all supported platforms for validation
SUPPORTED_PLATFORMS = list(PLATFORM_CONTEXT.keys())
