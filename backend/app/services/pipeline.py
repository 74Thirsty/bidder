"""Pipeline orchestration for job creation."""
from __future__ import annotations

import logging
import uuid
from typing import Dict

from app.db.session import get_session
from app.models.job import Job
from app.plugins.trades.concrete import ConfigurableTradePlugin, build_plugins

logger = logging.getLogger(__name__)

PLUGIN_REGISTRY: Dict[str, ConfigurableTradePlugin] = build_plugins()


async def process_job(payload: Dict) -> Dict:
    """Execute the plugin pipeline for the provided job payload."""

    trade = payload.get("trade", "").lower()
    plugin = PLUGIN_REGISTRY.get(trade)
    if not plugin:
        raise ValueError(f"Unsupported trade: {trade}")

    logger.info("Processing job for trade '%s'", trade)

    normalized = await plugin.normalize_data(payload)
    enriched = await plugin.fetch_public_data(normalized)
    bid = await plugin.compute_bid(enriched)
    steps = await plugin.generate_instructions(bid)
    bid["steps"] = steps
    final_payload = await plugin.export_bid_report(bid)

    job = Job(**final_payload)
    with get_session() as session:
        session.add(job)
        session.commit()
        session.refresh(job)

    logger.info("Generated job %s with total bid %.2f", final_payload.get("job_id"), final_payload.get("total_bid", 0.0))

    return final_payload


def generate_job_id() -> str:
    """Generate a unique job identifier."""

    return str(uuid.uuid4())
