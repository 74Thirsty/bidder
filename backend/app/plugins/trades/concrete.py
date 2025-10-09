"""Concrete trade plugin implementation."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from app.plugins.base import BaseTradePlugin
from app.services import geocoding, instructions, labor, materials, weather
from app.services.pipeline import generate_job_id

logger = logging.getLogger(__name__)


class ConcreteTradePlugin(BaseTradePlugin):
    """Concrete trade plugin performing job computations."""

    trade_name = "concrete"

    async def normalize_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("Normalizing payload: %s", payload)
        dimensions = payload.get("dimensions", {})
        length = float(dimensions.get("length", 0))
        width = float(dimensions.get("width", 0))
        depth = float(dimensions.get("depth", 0))
        volume_cubic_yards = (length * width * depth) / 27  # convert cubic feet to cubic yards
        normalized = {
            **payload,
            "margin": payload.get("margin", 0.15),
            "materials": payload.get("materials", ["concrete mix", "rebar", "gravel"]),
            "volume_cy": volume_cubic_yards,
        }
        return normalized

    async def fetch_public_data(self, normalized_payload: Dict[str, Any]) -> Dict[str, Any]:
        location = normalized_payload.get("location")
        geo = await geocoding.geocode_location(location)
        normalized_payload["geocode"] = geo

        material_costs = await materials.resolve_material_costs(normalized_payload["materials"])
        normalized_payload["material_costs"] = material_costs

        state = geo.get("state") if geo else None
        labor_rate = await labor.resolve_trade_labor_rate(self.trade_name, state)
        normalized_payload["labor_rate"] = labor_rate

        if geo:
            modifier = await weather.fetch_weather_modifier(geo["lat"], geo["lon"])
            normalized_payload["weather_modifier"] = modifier or 0.0
        else:
            normalized_payload["weather_modifier"] = 0.0

        return normalized_payload

    async def compute_bid(self, enriched_payload: Dict[str, Any]) -> Dict[str, Any]:
        material_items: List[Dict[str, Any]] = []
        material_costs = enriched_payload.get("material_costs", {})
        volume_cy = enriched_payload.get("volume_cy", 0.0)

        # Basic quantity estimation heuristics
        base_yield_per_bag = 0.6  # cubic feet per 80lb bag
        bags_needed = max(volume_cy * 27 / base_yield_per_bag, 1)

        for material, unit_cost in material_costs.items():
            if material.lower() == "concrete mix":
                quantity = bags_needed
                unit = "bag"
            elif material.lower() == "rebar":
                quantity = volume_cy * 30  # feet of rebar per cubic yard heuristic
                unit = "ft"
            else:
                quantity = volume_cy * 100  # generic weight/volume
                unit = "lb"

            total_cost = quantity * unit_cost
            material_items.append(
                {
                    "name": material,
                    "quantity": round(quantity, 2),
                    "unit": unit,
                    "unit_cost": round(unit_cost, 2),
                    "total_cost": round(total_cost, 2),
                }
            )

        material_total = sum(item["total_cost"] for item in material_items)
        labor_hours = volume_cy * 6  # hours per cubic yard heuristic
        labor_rate = enriched_payload.get("labor_rate", 25.0)
        labor_total = labor_hours * labor_rate

        overhead = material_total * 0.1
        profit_margin = enriched_payload.get("margin", 0.15)
        modifier = 1 + enriched_payload.get("weather_modifier", 0.0)

        subtotal = (material_total + labor_total + overhead) * modifier
        total_bid = subtotal * (1 + profit_margin)

        timestamp = datetime.utcnow().isoformat() + "Z"

        return {
            "job_id": generate_job_id(),
            "trade": self.trade_name,
            "location": enriched_payload.get("location"),
            "materials": material_items,
            "labor": {
                "hours": round(labor_hours, 2),
                "rate": round(labor_rate, 2),
                "total": round(labor_total, 2),
            },
            "overhead": round(overhead, 2),
            "profit_margin": round(profit_margin, 2),
            "total_bid": round(total_bid, 2),
            "_timestamp": timestamp,
        }

    async def generate_instructions(self, bid_payload: Dict[str, Any]) -> List[str]:
        steps = await instructions.fetch_wikihow_steps("pour concrete slab")
        if not steps:
            steps = instructions.fallback_steps(self.trade_name)
        return steps

    async def export_bid_report(self, bid_payload: Dict[str, Any]) -> Dict[str, Any]:
        bid_payload.setdefault("_timestamp", datetime.utcnow().isoformat() + "Z")
        return bid_payload
