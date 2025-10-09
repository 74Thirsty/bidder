"""Material pricing helpers leveraging public data sources."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

BASELINE_PATH = Path(__file__).resolve().parent.parent / "data" / "material_baseline.json"


async def search_material_price(query: str) -> Optional[float]:
    """Attempt to retrieve live material pricing from Build.com search API."""

    url = "https://www.build.com/api/search/v1"
    params = {"q": query, "sort": "relevance", "limit": 1}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        logger.warning("Material price lookup failed for %s: %s", query, exc)
        return None

    items = payload.get("results", [])
    if not items:
        return None

    price = items[0].get("price")
    return float(price) if price else None


def load_baseline_prices() -> Dict[str, float]:
    """Load offline fallback pricing."""

    if not BASELINE_PATH.exists():
        return {}

    with BASELINE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


async def resolve_material_costs(materials: List[str]) -> Dict[str, float]:
    """Resolve material costs using live data with baseline fallback."""

    baselines = load_baseline_prices()
    costs: Dict[str, float] = {}

    for material in materials:
        price = await search_material_price(material)
        if price is None:
            price = baselines.get(material.lower(), baselines.get(material, 0.0))
        costs[material] = float(price)

    return costs
