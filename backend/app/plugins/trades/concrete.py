"""Configurable trade plugin implementations for skilled trades."""
from __future__ import annotations

import logging
import math
import uuid
from datetime import datetime
from typing import Any, Dict, List

from app.plugins.base import BaseTradePlugin
from app.services import geocoding, instructions, labor, materials, weather

logger = logging.getLogger(__name__)

DEFAULT_DIMENSIONS = {"length": 20.0, "width": 10.0, "depth": 0.5}

TRADE_PROFILES: Dict[str, Dict[str, Any]] = {
    "concrete": {
        "default_materials": ["concrete mix", "rebar", "gravel"],
        "default_margin": 0.15,
        "calculation": "volume",
        "labor_metric": "volume_cy",
        "labor_hours_per_unit": 6.0,
        "min_labor_hours": 4.0,
        "overhead_rate": 0.10,
        "instruction_query": "pour a concrete slab",
        "material_heuristics": {
            "concrete mix": {"unit": "bag", "metric": "volume_cy", "multiplier": 45, "min_quantity": 10, "precision": 1},
            "rebar": {"unit": "ft", "metric": "volume_cy", "multiplier": 30, "precision": 1},
            "gravel": {"unit": "lb", "metric": "volume_cy", "multiplier": 100, "precision": 1},
        },
    },
    "electrical": {
        "default_materials": ["electrical wire", "breaker panel", "plywood"],
        "default_margin": 0.18,
        "calculation": "area",
        "labor_metric": "area_sqft",
        "labor_hours_per_unit": 0.12,
        "min_labor_hours": 6.0,
        "overhead_rate": 0.15,
        "instruction_query": "install residential electrical wiring",
        "material_heuristics": {
            "electrical wire": {"unit": "ft", "metric": "area_sqft", "multiplier": 2.5, "precision": 0, "min_quantity": 50},
            "breaker panel": {"unit": "ea", "base_quantity": 1, "metric": "area_sqft", "multiplier": 0.005, "precision": 0, "min_quantity": 1},
            "plywood": {"unit": "sheet", "metric": "area_sqft", "multiplier": 0.02, "precision": 2, "min_quantity": 2},
        },
    },
    "plumbing": {
        "default_materials": ["copper pipe", "pvc pipe", "plywood"],
        "default_margin": 0.17,
        "calculation": "linear",
        "labor_metric": "linear_ft",
        "labor_hours_per_unit": 0.35,
        "min_labor_hours": 5.0,
        "overhead_rate": 0.14,
        "instruction_query": "rough in residential plumbing",
        "material_heuristics": {
            "copper pipe": {"unit": "ft", "metric": "linear_ft", "multiplier": 1.1, "precision": 1, "min_quantity": 15},
            "pvc pipe": {"unit": "ft", "metric": "linear_ft", "multiplier": 0.9, "precision": 1, "min_quantity": 10},
            "plywood": {"unit": "sheet", "metric": "area_sqft", "multiplier": 0.015, "precision": 2, "min_quantity": 1},
        },
    },
    "hvac": {
        "default_materials": ["ductwork", "thermostat", "heat pump"],
        "default_margin": 0.20,
        "calculation": "area",
        "labor_metric": "area_sqft",
        "labor_hours_per_unit": 0.22,
        "min_labor_hours": 8.0,
        "overhead_rate": 0.18,
        "instruction_query": "install residential hvac system",
        "material_heuristics": {
            "ductwork": {"unit": "ft", "metric": "area_sqft", "multiplier": 0.6, "precision": 1, "min_quantity": 20},
            "thermostat": {"unit": "ea", "base_quantity": 1, "precision": 0, "min_quantity": 1},
            "heat pump": {"unit": "ea", "base_quantity": 1, "metric": "area_sqft", "multiplier": 0.002, "precision": 0, "min_quantity": 1},
        },
    },
    "landscaping": {
        "default_materials": ["landscape fabric", "garden soil", "sprinkler head"],
        "default_margin": 0.16,
        "calculation": "area",
        "labor_metric": "area_sqft",
        "labor_hours_per_unit": 0.08,
        "min_labor_hours": 4.0,
        "overhead_rate": 0.12,
        "instruction_query": "install residential landscaping",
        "material_heuristics": {
            "landscape fabric": {"unit": "sq ft", "metric": "area_sqft", "multiplier": 1.1, "precision": 1},
            "garden soil": {"unit": "cu ft", "metric": "volume_cuft", "multiplier": 0.5, "precision": 1},
            "sprinkler head": {"unit": "ea", "metric": "area_sqft", "multiplier": 0.005, "precision": 0, "min_quantity": 2},
        },
    },
}


class ConfigurableTradePlugin(BaseTradePlugin):
    """Configurable trade plugin performing job computations."""

    def __init__(self, trade_name: str, profile: Dict[str, Any]):
        self.trade_name = trade_name
        self.profile = profile

    @staticmethod
    def _to_float(value: Any, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    async def normalize_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("Normalizing payload for %s: %s", self.trade_name, payload)
        dimensions = payload.get("dimensions") or {}
        defaults = self.profile.get("default_dimensions", DEFAULT_DIMENSIONS)

        length = self._to_float(dimensions.get("length"), defaults.get("length", 0.0))
        width = self._to_float(dimensions.get("width"), defaults.get("width", 0.0))
        depth = self._to_float(dimensions.get("depth"), defaults.get("depth", 0.0))

        area_sqft = length * width
        linear_ft = 2 * (length + width)
        volume_cuft = area_sqft * depth
        volume_cy = volume_cuft / 27 if volume_cuft else 0.0

        metrics = {
            "length_ft": round(length, 2),
            "width_ft": round(width, 2),
            "depth_ft": round(depth, 2),
            "area_sqft": round(area_sqft, 2),
            "linear_ft": round(linear_ft, 2),
            "volume_cuft": round(volume_cuft, 2),
            "volume_cy": round(volume_cy, 2),
        }

        materials_input = payload.get("materials")
        if isinstance(materials_input, str):
            materials_list = [item.strip() for item in materials_input.split(",") if item.strip()]
        elif isinstance(materials_input, list):
            materials_list = [str(item).strip() for item in materials_input if str(item).strip()]
        else:
            materials_list = []

        if not materials_list:
            materials_list = list(self.profile.get("default_materials", []))
        else:
            materials_list = list(dict.fromkeys(materials_list))

        margin = self._to_float(payload.get("margin"), self.profile.get("default_margin", 0.15))

        normalized = {
            **payload,
            "trade": self.trade_name,
            "margin": margin,
            "materials": materials_list,
            "metrics": metrics,
        }
        return normalized

    async def fetch_public_data(self, normalized_payload: Dict[str, Any]) -> Dict[str, Any]:
        location = normalized_payload.get("location")
        geo = await geocoding.geocode_location(location) if location else None
        normalized_payload["geocode"] = geo
        normalized_payload["location_details"] = geo

        material_costs = await materials.resolve_material_costs(normalized_payload.get("materials", []))
        normalized_payload["material_costs"] = material_costs

        state = geo.get("state") if geo else None
        labor_rate = await labor.resolve_trade_labor_rate(self.trade_name, state)
        normalized_payload["labor_rate"] = labor_rate

        if geo:
            modifier = await weather.fetch_weather_modifier(geo.get("lat"), geo.get("lon"))
            normalized_payload["weather_modifier"] = modifier or 0.0
        else:
            normalized_payload["weather_modifier"] = 0.0

        return normalized_payload

    async def compute_bid(self, enriched_payload: Dict[str, Any]) -> Dict[str, Any]:
        material_items: List[Dict[str, Any]] = []
        material_costs = enriched_payload.get("material_costs", {})
        metrics = enriched_payload.get("metrics", {})
        profile_heuristics = self.profile.get("material_heuristics", {})

        for material_name, unit_cost in material_costs.items():
            key = material_name.lower()
            heuristics = profile_heuristics.get(key, {})
            metric_key = heuristics.get("metric", self.profile.get("labor_metric", "volume_cy"))
            metric_value = metrics.get(metric_key)
            if not metric_value:
                metric_value = metrics.get("volume_cy") or metrics.get("area_sqft") or 1.0

            quantity = heuristics.get("base_quantity", 0.0) + metric_value * heuristics.get("multiplier", 1.0)
            if heuristics.get("min_quantity"):
                quantity = max(quantity, heuristics["min_quantity"])

            if heuristics.get("round_up"):
                quantity = math.ceil(quantity)

            precision = heuristics.get("precision", 2)
            quantity = round(quantity, precision) if precision >= 0 else quantity
            if precision == 0:
                quantity = int(quantity)

            unit = heuristics.get("unit", "unit")
            total_cost = quantity * unit_cost

            material_items.append(
                {
                    "name": material_name,
                    "quantity": quantity,
                    "unit": unit,
                    "unit_cost": round(unit_cost, 2),
                    "total_cost": round(total_cost, 2),
                }
            )

        material_total = sum(item["total_cost"] for item in material_items)

        labor_metric_key = self.profile.get("labor_metric", "volume_cy")
        labor_metric_value = metrics.get(labor_metric_key) or metrics.get("area_sqft") or metrics.get("volume_cy") or 1.0
        labor_hours = labor_metric_value * self.profile.get("labor_hours_per_unit", 1.0)
        labor_hours = max(labor_hours, self.profile.get("min_labor_hours", 2.0))

        labor_rate = enriched_payload.get("labor_rate", 25.0)
        labor_total = labor_hours * labor_rate

        overhead_rate = self.profile.get("overhead_rate", 0.1)
        overhead = (material_total + labor_total) * overhead_rate

        weather_modifier = float(enriched_payload.get("weather_modifier", 0.0))
        subtotal = material_total + labor_total + overhead
        weather_adjusted_subtotal = subtotal * (1 + weather_modifier)

        profit_margin = float(enriched_payload.get("margin", self.profile.get("default_margin", 0.15)))
        profit_amount = weather_adjusted_subtotal * profit_margin
        total_bid = weather_adjusted_subtotal + profit_amount

        timestamp = datetime.utcnow().isoformat() + "Z"

        cost_breakdown = {
            "materials": round(material_total, 2),
            "labor": round(labor_total, 2),
            "overhead": round(overhead, 2),
            "profit": round(profit_amount, 2),
            "subtotal": round(weather_adjusted_subtotal, 2),
            "weather_modifier": round(weather_modifier, 3),
        }

        metrics_output = {key: value for key, value in metrics.items() if value is not None}

        bid = {
            "job_id": _generate_job_id(),
            "trade": self.trade_name,
            "location": enriched_payload.get("location", ""),
            "materials": material_items,
            "labor": {
                "hours": round(labor_hours, 2),
                "rate": round(labor_rate, 2),
                "total": round(labor_total, 2),
            },
            "overhead": round(overhead, 2),
            "profit_margin": round(profit_margin, 4),
            "profit_amount": round(profit_amount, 2),
            "material_total": round(material_total, 2),
            "labor_total": round(labor_total, 2),
            "total_bid": round(total_bid, 2),
            "weather_modifier": round(weather_modifier, 3),
            "cost_breakdown": cost_breakdown,
            "metrics": metrics_output,
            "location_details": enriched_payload.get("location_details"),
            "_timestamp": timestamp,
        }

        return bid

    async def generate_instructions(self, bid_payload: Dict[str, Any]) -> List[str]:
        query = self.profile.get("instruction_query", f"{self.trade_name} project plan")
        steps = await instructions.fetch_wikihow_steps(query)
        if not steps:
            steps = instructions.fallback_steps(self.trade_name)
        return steps

    async def export_bid_report(self, bid_payload: Dict[str, Any]) -> Dict[str, Any]:
        bid_payload.setdefault("_timestamp", datetime.utcnow().isoformat() + "Z")
        return bid_payload


def build_plugins() -> Dict[str, ConfigurableTradePlugin]:
    """Create plugin instances for every configured trade."""

    return {
        trade: ConfigurableTradePlugin(trade, profile)
        for trade, profile in TRADE_PROFILES.items()
    }


def _generate_job_id() -> str:
    """Return a unique identifier for a generated job."""

    return str(uuid.uuid4())
