"""
app/routes/health.py

Health-check and application-info endpoints.

GET /health   — liveness / readiness probe
GET /info     — human-readable service metadata
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config.settings import get_settings
from app.database.connection import get_db
from app.models.schemas import HealthResponse
from app.services.google_translator import is_google_available
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description=(
        "Returns the current health status of the service, including the active "
        "translation engine and database connectivity."
    ),
)
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """Liveness / readiness probe used by load balancers and monitoring tools."""

    # ── Check database connectivity ────────────────────────────────────────
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Health check: database error — %s", exc)
        db_status = "error"

    engine = "google" if is_google_available() else "mock"

    logger.info("GET /health  db=%s  engine=%s", db_status, engine)

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        translation_engine=engine,
        database=db_status,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/info",
    summary="Service metadata",
    description="Returns application name, version, supported languages, and active engine.",
)
async def service_info() -> dict:
    """Return metadata about the running service."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "translation_engine": "google" if is_google_available() else "mock",
        "supported_languages": settings.SUPPORTED_LANGUAGES,
        "limits": {
            "max_text_length": settings.MAX_TEXT_LENGTH,
            "max_bulk_sentences": settings.MAX_BULK_SENTENCES,
        },
    }
