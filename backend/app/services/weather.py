"""Weather adjustment utilities."""
from __future__ import annotations

from typing import Optional

import httpx

from app.core.config import get_settings

settings = get_settings()


async def fetch_weather_modifier(lat: float, lon: float) -> Optional[float]:
    """Fetch a simple weather-based cost modifier from OpenWeatherMap."""

    if not settings.openweather_api_key:
        return None

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": settings.openweather_api_key, "units": "imperial"}

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    main = data.get("main", {})
    temperature = main.get("temp")
    if temperature is None:
        return None

    # Example heuristic: adjust ±5% based on deviation from 65°F
    deviation = abs(temperature - 65)
    modifier = min(0.1, deviation / 100)
    return modifier
