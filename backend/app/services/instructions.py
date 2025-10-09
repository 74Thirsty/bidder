"""Instruction generation using public instructional resources."""
from __future__ import annotations

import logging
from typing import List

import httpx

logger = logging.getLogger(__name__)


async def fetch_wikihow_steps(query: str) -> List[str]:
    """Fetch step-by-step instructions from WikiHow search."""

    url = "https://www.wikihow.com/api.php"
    params = {
        "format": "json",
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 1,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()

    search_results = payload.get("query", {}).get("search", [])
    if not search_results:
        return []

    page_id = search_results[0].get("pageid")
    if not page_id:
        return []

    step_params = {
        "format": "json",
        "action": "parse",
        "pageid": page_id,
        "prop": "sections",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        step_response = await client.get(url, params=step_params)
        step_response.raise_for_status()
        step_payload = step_response.json()

    sections = step_payload.get("parse", {}).get("sections", [])
    steps = [section.get("line") for section in sections if section.get("line")]

    return [step for step in steps if isinstance(step, str)]


def fallback_steps(trade: str) -> List[str]:
    """Return a basic fallback instruction set when API data is unavailable."""

    basic_steps = {
        "concrete": [
            "Prepare site by grading and leveling the subbase.",
            "Install forms and reinforcement as specified.",
            "Mix concrete to the required slump.",
            "Pour and screed concrete evenly.",
            "Finish surface and allow proper curing time.",
        ],
        "electrical": [
            "Review circuit layout and safety codes.",
            "Shut off power and lock out panel.",
            "Install conduit and pull conductors.",
            "Terminate devices and fixtures.",
            "Test circuits and document results.",
        ],
    }

    return basic_steps.get(trade.lower(), ["Review project scope.", "Gather materials and tools.", "Complete work following best practices.", "Inspect and clean up site."])
