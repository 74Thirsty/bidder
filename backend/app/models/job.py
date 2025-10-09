"""Database models for job bids."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlmodel import Column, Field, JSON, SQLModel


class MaterialItem(SQLModel, table=False):
    """Nested model representing a material line item."""

    name: str
    quantity: float
    unit: str
    unit_cost: float
    total_cost: float


class Job(SQLModel, table=True):
    """Persisted job entry containing canonical bid information."""

    job_id: str = Field(default=None, primary_key=True, index=True)
    trade: str
    location: str
    materials: List[MaterialItem] = Field(sa_column=Column(JSON), default_factory=list)
    labor: dict = Field(sa_column=Column(JSON), default_factory=dict)
    overhead: float
    profit_margin: float
    total_bid: float
    steps: List[str] = Field(sa_column=Column(JSON), default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow, alias="_timestamp")

    class Config:
        allow_population_by_field_name = True


class JobCreate(SQLModel):
    """Payload accepted from the API when creating a job."""

    trade: str
    location: str
    dimensions: dict
    materials: Optional[List[str]] = None
    margin: Optional[float] = Field(default=0.15, ge=0, le=1)
