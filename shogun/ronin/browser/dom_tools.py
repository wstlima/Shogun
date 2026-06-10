"""DOM Tools — utility functions for browser DOM interaction.

Provides helper functions for element finding, text extraction,
and page structure analysis, complementing the Playwright controller.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("shogun.ronin.browser.dom")


async def find_element(page: Any, selector: str) -> dict[str, Any] | None:
    """Find a DOM element and return its properties."""
    try:
        element = await page.query_selector(selector)
        if not element:
            return None
        return {
            "tag": await element.evaluate("e => e.tagName.toLowerCase()"),
            "text": await element.text_content(),
            "visible": await element.is_visible(),
            "enabled": await element.is_enabled(),
            "bounding_box": await element.bounding_box(),
        }
    except Exception as exc:
        log.debug("DOM: find_element failed for '%s': %s", selector, exc)
        return None


async def extract_page_text(page: Any) -> str:
    """Extract all visible text from a page."""
    try:
        return await page.evaluate("() => document.body.innerText")
    except Exception:
        return ""


async def get_page_structure(page: Any) -> dict[str, Any]:
    """Get a simplified structure of the page for agent understanding."""
    try:
        structure = await page.evaluate("""() => {
            const elements = [];
            const interactable = document.querySelectorAll(
                'a, button, input, select, textarea, [role="button"], [onclick]'
            );
            interactable.forEach((el, i) => {
                if (i < 50) {
                    elements.push({
                        tag: el.tagName.toLowerCase(),
                        type: el.type || null,
                        text: (el.innerText || el.value || el.placeholder || '').slice(0, 100),
                        id: el.id || null,
                        name: el.name || null,
                        href: el.href || null,
                        selector: el.id ? '#' + el.id : null,
                    });
                }
            });
            return {
                title: document.title,
                url: window.location.href,
                element_count: interactable.length,
                elements: elements,
            };
        }""")
        return structure
    except Exception as exc:
        log.debug("DOM: get_page_structure failed: %s", exc)
        return {"title": "", "url": "", "element_count": 0, "elements": []}
