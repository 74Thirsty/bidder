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


class CostBreakdown(BaseModel):
    """Cost allocation summary."""

    materials: float
    labor: float
    overhead: float
    profit: float
    subtotal: float
    weather_modifier: float


class LocationDetails(BaseModel):
    """Resolved location metadata from geocoding services."""

    display_name: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class ProjectMetrics(BaseModel):
    """Normalized dimensional metrics for the job."""

    length_ft: Optional[float] = None
    width_ft: Optional[float] = None
    depth_ft: Optional[float] = None
    area_sqft: Optional[float] = None
    linear_ft: Optional[float] = None
    volume_cuft: Optional[float] = None
    volume_cy: Optional[float] = None


class JobBase(BaseModel):
    """Shared fields between request and response models."""

    trade: str
    location: str
    materials: List[MaterialItem]
    labor: LaborBreakdown
    overhead: float
    profit_margin: float
    profit_amount: float
    material_total: float
    labor_total: float
    weather_modifier: float
    total_bid: float
    cost_breakdown: CostBreakdown
    metrics: ProjectMetrics
    location_details: Optional[LocationDetails] = None
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


class JobSummary(BaseModel):
    """Lightweight summary representation used for listings."""

    job_id: str
    trade: str
    location: str
    total_bid: float
    profit_margin: float
    material_total: Optional[float] = None
    labor_total: Optional[float] = None
    timestamp: datetime = Field(alias="_timestamp")
    cost_breakdown: Optional[CostBreakdown] = None
    metrics: Optional[ProjectMetrics] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class JobListResponse(BaseModel):
    """Paginated list of job summaries."""

    items: List[JobSummary]
    total: int
    limit: int
    offset: int


class TradeCount(BaseModel):
    """Statistics for a given trade."""

    trade: str
    count: int


class AnalyticsSummary(BaseModel):
    """Aggregated analytics surfaced to the UI."""

    total_jobs: int
    average_bid: float
    average_profit_margin: float
    average_material_cost: float
    average_labor_cost: float
    top_trades: List[TradeCount]
    recent_locations: List[str]
    last_updated: datetime
