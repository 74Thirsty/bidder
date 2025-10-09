"""Pydantic schemas for Job endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MaterialItem(BaseModel):
    """Material item representation following the canonical schema."""

    name: str
    quantity: float
    unit: str
    unit_cost: float
    total_cost: float


class LaborBreakdown(BaseModel):
    """Labor cost details."""

    hours: float
    rate: float
    total: float


class JobBase(BaseModel):
    """Shared fields between request and response models."""

    trade: str
    location: str
    materials: List[MaterialItem]
    labor: LaborBreakdown
    overhead: float
    profit_margin: float
    total_bid: float
    steps: List[str]
    timestamp: datetime = Field(alias="_timestamp")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class JobCreateRequest(BaseModel):
    """Request payload for creating a job."""

    trade: str
    location: str
    dimensions: dict
    materials: Optional[List[str]] = None
    margin: Optional[float] = Field(default=0.15, ge=0, le=1)


class JobResponse(JobBase):
    """Response schema returned from job creation."""

    job_id: str
