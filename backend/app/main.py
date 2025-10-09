"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import jobs
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db

settings = get_settings()
configure_logging(settings.debug)

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(jobs.router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize resources on application startup."""

    init_db()
