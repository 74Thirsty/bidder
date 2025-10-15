"""Analytics helpers for summarising job performance."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.job import Job


def _tuple_value(item):
    """Return the scalar value from a possible tuple result."""

    if isinstance(item, tuple):
        return item[0]
    return item


def compute_summary(session: Session) -> Dict[str, object]:
    """Compute aggregate analytics for all stored jobs."""

    total_result = session.exec(select(func.count()).select_from(Job)).one()
    total_jobs = int(_tuple_value(total_result))

    if total_jobs == 0:
        return {
            "total_jobs": 0,
            "average_bid": 0.0,
            "average_profit_margin": 0.0,
            "average_material_cost": 0.0,
            "average_labor_cost": 0.0,
            "top_trades": [],
            "recent_locations": [],
            "last_updated": datetime.utcnow(),
        }

    averages_row = session.exec(
        select(
            func.avg(Job.total_bid),
            func.avg(Job.profit_margin),
            func.avg(Job.material_total),
            func.avg(Job.labor_total),
        )
    ).one()

    avg_bid, avg_margin, avg_material, avg_labor = [float(value or 0.0) for value in averages_row]

    top_trades_rows: List[tuple] = session.exec(
        select(Job.trade, func.count())
        .group_by(Job.trade)
        .order_by(func.count().desc())
        .limit(5)
    ).all()
    top_trades = [
        {"trade": trade, "count": int(_tuple_value(count))}
        for trade, count in top_trades_rows
    ]

    recent_locations_rows = session.exec(
        select(Job.location)
        .order_by(Job.timestamp.desc())
        .limit(5)
    ).all()
    recent_locations = [
        _tuple_value(row) for row in recent_locations_rows if _tuple_value(row)
    ]

    last_timestamp = session.exec(
        select(Job.timestamp)
        .order_by(Job.timestamp.desc())
        .limit(1)
    ).first()
    last_updated = _tuple_value(last_timestamp) if last_timestamp else datetime.utcnow()

    return {
        "total_jobs": total_jobs,
        "average_bid": round(avg_bid, 2),
        "average_profit_margin": round(avg_margin, 4),
        "average_material_cost": round(avg_material, 2),
        "average_labor_cost": round(avg_labor, 2),
        "top_trades": top_trades,
        "recent_locations": recent_locations,
        "last_updated": last_updated,
    }
