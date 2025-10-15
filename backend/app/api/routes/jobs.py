"""Job API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func
from sqlmodel import select

from app.db.session import get_session
from app.models.job import Job
from app.schemas.job import (
    AnalyticsSummary,
    JobCreateRequest,
    JobListResponse,
    JobResponse,
    JobSummary,
)
from app.services.analytics import compute_summary
from app.services.pipeline import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
def list_jobs(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)) -> JobListResponse:
    """Return a paginated list of recently generated jobs."""

    with get_session() as session:
        total_result = session.exec(select(func.count()).select_from(Job)).one()
        total = int(total_result[0] if isinstance(total_result, tuple) else total_result)

        statement = select(Job).order_by(Job.timestamp.desc()).offset(offset).limit(limit)
        records = session.exec(statement).all()

    items = [JobSummary.from_orm(record) for record in records]
    return JobListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(request: JobCreateRequest) -> JobResponse:
    """Create a job bid based on user input."""

    try:
        result = await process_job(request.dict())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return JobResponse.parse_obj(result)


@router.get("/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary() -> AnalyticsSummary:
    """Return aggregate analytics computed from historical jobs."""

    with get_session() as session:
        summary = compute_summary(session)

    return AnalyticsSummary(**summary)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    """Retrieve a job by identifier."""

    with get_session() as session:
        job = session.get(Job, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse.from_orm(job)
