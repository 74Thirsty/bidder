"""Labor rate helpers using BLS public datasets."""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def fetch_bls_labor_rate(occupation_code: str, state: Optional[str]) -> Optional[float]:
    """Fetch hourly wage information from the BLS API."""

    if not state:
        state = "US"

    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    series_id = f"OEUN0000000000000{occupation_code}"
    headers = {"Content-type": "application/json"}
    payload = {
        "seriesid": [series_id],
    }

    if settings.bls_api_key:
        payload["registrationkey"] = settings.bls_api_key

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    series = data.get("Results", {}).get("series", [])
    if not series:
        logger.warning("No BLS series found for %s", series_id)
        return None

    data_points = series[0].get("data", [])
    if not data_points:
        return None

    latest = data_points[0]
    value = latest.get("value")
    return float(value) if value else None


async def resolve_trade_labor_rate(trade: str, state: Optional[str]) -> float:
    """Resolve a trade-specific labor rate with sensible fallbacks."""

    trade_to_occupation = {
        "concrete": "472061",  # Construction laborers
        "electrical": "472111",  # Electricians
        "plumbing": "472152",  # Plumbers
        "hvac": "499021",  # HVAC mechanics
        "landscaping": "372011",  # Landscaping workers
    }

    occupation_code = trade_to_occupation.get(trade.lower(), "472061")
    rate = await fetch_bls_labor_rate(occupation_code, state)

    if rate is None:
        # Fallback to national average hourly rate in USD
        fallback_rates = {
            "concrete": 24.50,
            "electrical": 32.25,
            "plumbing": 30.40,
            "hvac": 28.10,
            "landscaping": 20.75,
        }
        rate = fallback_rates.get(trade.lower(), 25.0)

    return rate
