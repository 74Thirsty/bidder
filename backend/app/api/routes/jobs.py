"""Job API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.job import JobCreateRequest, JobResponse
from app.services.pipeline import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse)
async def create_job(request: JobCreateRequest) -> JobResponse:
    """Create a job bid based on user input."""

    try:
        result = await process_job(request.dict())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return JobResponse(**result)
