"""
app/database/repository.py

Data-access layer — all database read/write operations live here.
Routes and services never import SQLAlchemy directly; they call this module.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import TranslationLog

logger = logging.getLogger(__name__)


def create_log(db: Session, log_data: dict) -> TranslationLog:
    """
    Persist a new translation log entry.

    Parameters
    ----------
    db       : Active SQLAlchemy session (injected by FastAPI dependency).
    log_data : Dictionary matching the TranslationLog column names.

    Returns
    -------
    The newly created TranslationLog ORM instance.
    """
    log_entry = TranslationLog(**log_data)
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    logger.debug("Saved translation log id=%s request_id=%s", log_entry.id, log_entry.request_id)
    return log_entry


def get_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    target_language: Optional[str] = None,
    success: Optional[bool] = None,
) -> list[TranslationLog]:
    """
    Retrieve translation logs with optional filtering.

    Parameters
    ----------
    db              : Active SQLAlchemy session.
    skip            : Number of records to skip (pagination offset).
    limit           : Maximum records to return.
    target_language : Filter by target language code.
    success         : Filter by success flag.
    """
    query = db.query(TranslationLog)
    if target_language:
        query = query.filter(TranslationLog.target_language == target_language)
    if success is not None:
        query = query.filter(TranslationLog.success == success)
    return query.order_by(TranslationLog.created_at.desc()).offset(skip).limit(limit).all()


def get_log_by_id(db: Session, log_id: int) -> Optional[TranslationLog]:
    """Retrieve a single log entry by its primary key."""
    return db.query(TranslationLog).filter(TranslationLog.id == log_id).first()


def count_logs(db: Session) -> int:
    """Return the total number of translation log entries."""
    return db.query(TranslationLog).count()
