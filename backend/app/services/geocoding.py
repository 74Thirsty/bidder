"""Geocoding utilities relying on public providers."""
from __future__ import annotations

import logging
from typing import Dict, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def geocode_location(location: str) -> Optional[Dict[str, float]]:
    """Resolve a free-form location string into coordinates using Nominatim."""

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    headers = {"User-Agent": "Bidder/1.0 (https://example.com)"}

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

    if not data:
        logger.warning("No geocoding results for location '%s'", location)
        return None

    result = data[0]
    return {
        "lat": float(result["lat"]),
        "lon": float(result["lon"]),
        "display_name": result.get("display_name", location),
        "postal_code": result.get("address", {}).get("postcode"),
        "state": result.get("address", {}).get("state"),
        "country": result.get("address", {}).get("country"),
    }


async def geoapify_cost_index(postal_code: Optional[str]) -> Optional[float]:
    """Retrieve a location cost index via Geoapify if configured."""

    if not postal_code or not settings.geoapify_key:
        return None

    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": postal_code, "apiKey": settings.geoapify_key}

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    features = data.get("features", [])
    if not features:
        return None

    properties = features[0].get("properties", {})
    return properties.get("datasource", {}).get("confidence")
