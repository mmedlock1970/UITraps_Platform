"""
Page Classifier for UI Traps Analyzer

Classifies page types and maps tasks to appropriate pages for context-aware analysis.

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

from typing import Dict, List, Tuple
from urllib.parse import urlparse
import re


# Page role definitions with keywords and URL patterns
PAGE_ROLES = {
    "homepage": {
        "url_patterns": [r"^/$", r"^/index", r"^/home"],
        "title_keywords": ["home", "welcome"],
        "description": "Introduces product/service, directs to next steps"
    },
    "product": {
        "url_patterns": [r"/product", r"/item", r"/shop/[^/]+$", r"/store/[^/]+$"],
        "title_keywords": ["product", "buy", "shop", "store", "price"],
        "description": "Shows product details, pricing, add-to-cart"
    },
    "category": {
        "url_patterns": [r"/category", r"/products$", r"/shop$", r"/store$", r"/catalog"],
        "title_keywords": ["products", "catalog", "browse", "all items"],
        "description": "Browse multiple items, filtering, sorting"
    },
    "cart": {
        "url_patterns": [r"/cart", r"/basket", r"/bag"],
        "title_keywords": ["cart", "basket", "bag", "your items"],
        "description": "Review selected items, adjust quantities"
    },
    "checkout": {
        "url_patterns": [r"/checkout", r"/payment", r"/order"],
        "title_keywords": ["checkout", "payment", "order", "purchase"],
        "description": "Complete purchase transaction"
    },
    "contact": {
        "url_patterns": [r"/contact", r"/reach-us", r"/get-in-touch", r"/support"],
        "title_keywords": ["contact", "reach us", "get in touch", "support"],
        "description": "Communication channel - form, email, phone"
    },
    "about": {
        "url_patterns": [r"/about", r"/team", r"/our-story", r"/who-we-are", r"/company"],
        "title_keywords": ["about", "team", "our story", "who we are", "company"],
        "description": "Background, credibility, team info"
    },
    "account": {
        "url_patterns": [r"/account", r"/profile", r"/dashboard", r"/my-", r"/login", r"/register"],
        "title_keywords": ["account", "profile", "login", "register", "sign in", "my "],
        "description": "User management, settings, history"
    },
    "help": {
        "url_patterns": [r"/help", r"/faq", r"/support", r"/knowledge"],
        "title_keywords": ["help", "faq", "frequently asked", "support", "how to"],
        "description": "Support content, answers to common questions"
    },
    "legal": {
        "url_patterns": [r"/privacy", r"/terms", r"/policy", r"/legal", r"/disclaimer"],
        "title_keywords": ["privacy", "terms", "policy", "legal", "disclaimer"],
        "description": "Legal documents, policies, disclaimers"
    }
}

# Task-to-page-role mapping
# Defines which tasks are FULLY relevant vs PARTIALLY relevant for each page type
TASK_PAGE_MAPPING = {
    "homepage": {
        "full": [
            "Find out what this site offers",
            "Learn more about",
            "Understand the product",
            "Discover features"
        ],
        "partial": [
            "Buy",
            "Purchase",
            "Contact",
            "Get pricing"
        ],
        "navigation_only": [
            "Checkout",
            "View cart",
            "Account settings"
        ]
    },
    "product": {
        "full": [
            "Buy",
            "Purchase",
            "Get pricing",
            "Add to cart",
            "Learn about product",
            "Compare options",
            "Find bulk discounts"
        ],
        "partial": [
            "Find out what this site offers"
        ],
        "navigation_only": [
            "Contact",
            "About the company"
        ]
    },
    "category": {
        "full": [
            "Browse products",
            "Find products",
            "Compare options",
            "Shop"
        ],
        "partial": [
            "Buy",
            "Purchase"
        ],
        "navigation_only": [
            "Contact",
            "Checkout"
        ]
    },
    "cart": {
        "full": [
            "Review items",
            "Proceed to checkout",
            "Modify order",
            "View cart"
        ],
        "partial": [
            "Buy",
            "Purchase",
            "Complete order"
        ],
        "navigation_only": [
            "Contact",
            "Browse more"
        ]
    },
    "checkout": {
        "full": [
            "Complete purchase",
            "Pay for order",
            "Enter shipping",
            "Enter payment"
        ],
        "partial": [],
        "navigation_only": [
            "Return to cart",
            "Continue shopping"
        ]
    },
    "contact": {
        "full": [
            "Contact",
            "Get in touch",
            "Ask a question",
            "Request information",
            "Send a message",
            "Find bulk discounts",  # Often handled via contact
            "Request quote"
        ],
        "partial": [
            "Get support",
            "Report issue"
        ],
        "navigation_only": [
            "Buy",
            "Browse products"
        ]
    },
    "about": {
        "full": [
            "Learn about the company",
            "Find out who",
            "Understand the team",
            "Company background",
            "Learn more about"
        ],
        "partial": [
            "Build trust",
            "Verify credibility"
        ],
        "navigation_only": [
            "Buy",
            "Contact",
            "Browse"
        ]
    },
    "account": {
        "full": [
            "View account",
            "Update profile",
            "View orders",
            "Change settings",
            "Login",
            "Register"
        ],
        "partial": [],
        "navigation_only": [
            "Buy",
            "Browse"
        ]
    },
    "help": {
        "full": [
            "Get help",
            "Find answers",
            "How to",
            "Troubleshoot"
        ],
        "partial": [
            "Contact support"
        ],
        "navigation_only": [
            "Buy",
            "Browse"
        ]
    },
    "legal": {
        "full": [
            "Read privacy policy",
            "Review terms",
            "Understand policies"
        ],
        "partial": [],
        "navigation_only": []
    }
}


def classify_page(url: str, title: str) -> str:
    """
    Classify a page's role based on its URL and title.

    Args:
        url: Full URL or path of the page
        title: Page title

    Returns:
        Page role string (e.g., "homepage", "product", "contact")
    """
    # Parse URL to get path
    parsed = urlparse(url)
    path = parsed.path.lower()
    title_lower = title.lower() if title else ""

    # Check each page role
    scores = {}
    for role, config in PAGE_ROLES.items():
        score = 0

        # Check URL patterns
        for pattern in config["url_patterns"]:
            if re.search(pattern, path):
                score += 2  # URL match is strong signal

        # Check title keywords
        for keyword in config["title_keywords"]:
            if keyword.lower() in title_lower:
                score += 1

        scores[role] = score

    # Get highest scoring role
    if scores:
        best_role = max(scores, key=scores.get)
        if scores[best_role] > 0:
            return best_role

    # Default to homepage if root path, otherwise "unknown"
    if path in ["/", "", "/index.html", "/index.php"]:
        return "homepage"

    return "unknown"


def get_relevant_tasks(page_role: str, all_tasks: List[str]) -> Dict[str, List[str]]:
    """
    Get tasks relevant to a page role, categorized by relevance level.

    Args:
        page_role: The classified page role
        all_tasks: List of all user tasks

    Returns:
        Dict with keys: "full", "partial", "navigation_only", each containing list of matching tasks
    """
    if page_role not in TASK_PAGE_MAPPING:
        # Unknown page type - return all tasks as partial
        return {
            "full": [],
            "partial": all_tasks,
            "navigation_only": []
        }

    mapping = TASK_PAGE_MAPPING[page_role]
    result = {
        "full": [],
        "partial": [],
        "navigation_only": []
    }

    for task in all_tasks:
        task_lower = task.lower()
        matched = False

        # Check full relevance
        for keyword in mapping["full"]:
            if keyword.lower() in task_lower:
                result["full"].append(task)
                matched = True
                break

        if matched:
            continue

        # Check partial relevance
        for keyword in mapping["partial"]:
            if keyword.lower() in task_lower:
                result["partial"].append(task)
                matched = True
                break

        if matched:
            continue

        # Check navigation-only relevance
        for keyword in mapping["navigation_only"]:
            if keyword.lower() in task_lower:
                result["navigation_only"].append(task)
                matched = True
                break

        # If no match, treat as partial (evaluate with discretion)
        if not matched:
            result["partial"].append(task)

    return result


def classify_all_pages(pages: List[Dict]) -> Dict[str, Dict]:
    """
    Classify all pages in a site crawl.

    Args:
        pages: List of page dicts with 'url' and 'title' keys

    Returns:
        Dict mapping page URL to classification info
    """
    classifications = {}

    for page in pages:
        url = page.get("url", "")
        title = page.get("title", "")

        role = classify_page(url, title)

        classifications[url] = {
            "role": role,
            "title": title,
            "description": PAGE_ROLES.get(role, {}).get("description", "Unknown page type")
        }

    return classifications


def get_task_flow(task: str, site_pages: Dict[str, Dict]) -> List[Dict]:
    """
    Determine the expected page flow for a given task.

    Args:
        task: The user task
        site_pages: Dict of page classifications from classify_all_pages()

    Returns:
        List of dicts describing expected flow steps
    """
    task_lower = task.lower()

    # Define common task flows
    flows = {
        "buy": ["homepage", "category", "product", "cart", "checkout"],
        "purchase": ["homepage", "category", "product", "cart", "checkout"],
        "contact": ["homepage", "contact"],
        "learn": ["homepage", "about"],
        "find out": ["homepage", "about", "product"],
        "bulk discount": ["homepage", "product", "contact"],
        "pricing": ["homepage", "product"],
    }

    # Find matching flow
    expected_flow = None
    for keyword, flow in flows.items():
        if keyword in task_lower:
            expected_flow = flow
            break

    if not expected_flow:
        # Default: homepage is always a starting point
        expected_flow = ["homepage"]

    # Map expected flow to actual site pages
    flow_steps = []
    for role in expected_flow:
        # Find pages with this role
        matching_pages = [
            {"url": url, "title": info["title"], "role": role}
            for url, info in site_pages.items()
            if info["role"] == role
        ]

        if matching_pages:
            flow_steps.append({
                "expected_role": role,
                "found_pages": matching_pages,
                "status": "found"
            })
        else:
            flow_steps.append({
                "expected_role": role,
                "found_pages": [],
                "status": "missing"
            })

    return flow_steps


def generate_flow_analysis(all_tasks: List[str], site_pages: Dict[str, Dict]) -> List[Dict]:
    """
    Analyze task flows across the site.

    Args:
        all_tasks: List of user tasks
        site_pages: Dict of page classifications

    Returns:
        List of flow analysis dicts
    """
    flow_analyses = []

    for task in all_tasks:
        flow = get_task_flow(task, site_pages)

        # Determine if flow is complete
        missing_steps = [step for step in flow if step["status"] == "missing"]

        flow_analyses.append({
            "task": task,
            "flow": flow,
            "complete": len(missing_steps) == 0,
            "missing_page_types": [step["expected_role"] for step in missing_steps],
            "assessment": _assess_flow(flow, task)
        })

    return flow_analyses


def _assess_flow(flow: List[Dict], task: str) -> str:
    """Generate human-readable flow assessment."""
    missing = [step["expected_role"] for step in flow if step["status"] == "missing"]

    if not missing:
        return f"Complete path exists for '{task}'"

    if len(missing) == 1:
        return f"Missing {missing[0]} page for '{task}' - users may struggle to complete this task"

    return f"Missing {', '.join(missing)} pages for '{task}' - significant gaps in task flow"
