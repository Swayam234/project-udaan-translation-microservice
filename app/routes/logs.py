"""
app/routes/logs.py

Admin endpoint to retrieve stored translation logs from the SQLite database.

GET /logs            — paginated list of translation logs
GET /logs/{log_id}   — retrieve a single log entry by ID
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.repository import count_logs, get_log_by_id, get_logs
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get(
    "",
    summary="List translation logs",
    description="Retrieve paginated translation logs. Supports filtering by language and status.",
)
async def list_logs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return (1–100)"),
    target_language: Optional[str] = Query(None, description="Filter by target language code"),
    success: Optional[bool] = Query(None, description="Filter by success flag"),
) -> dict:
    """Return paginated translation logs with optional filters."""
    logs = get_logs(
        db,
        skip=skip,
        limit=limit,
        target_language=target_language,
        success=success,
    )
    total = count_logs(db)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "results": [
            {
                "id": log.id,
                "request_id": log.request_id,
                "original_text": log.original_text[:100] + ("…" if len(log.original_text) > 100 else ""),
                "translated_text": (log.translated_text or "")[:100],
                "source_language": log.source_language,
                "target_language": log.target_language,
                "engine": log.engine,
                "success": log.success,
                "error_message": log.error_message,
                "characters": log.characters,
                "latency_ms": log.latency_ms,
                "is_bulk": log.is_bulk,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "client_host": log.client_host,
            }
            for log in logs
        ],
    }


@router.get(
    "/{log_id}",
    summary="Get a single translation log",
    description="Retrieve full details of a translation log entry by its ID.",
)
async def get_single_log(
    log_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Return a single translation log entry by primary key."""
    log = get_log_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log entry with id={log_id} not found.",
        )
    return {
        "id": log.id,
        "request_id": log.request_id,
        "original_text": log.original_text,
        "translated_text": log.translated_text,
        "source_language": log.source_language,
        "target_language": log.target_language,
        "engine": log.engine,
        "success": log.success,
        "error_message": log.error_message,
        "characters": log.characters,
        "latency_ms": log.latency_ms,
        "is_bulk": log.is_bulk,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        "client_host": log.client_host,
    }
