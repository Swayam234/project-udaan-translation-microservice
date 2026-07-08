"""
app/database/models.py

SQLAlchemy ORM models for persisting translation request logs in SQLite.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from app.database.connection import Base


class TranslationLog(Base):
    """
    Stores a log entry for every translation request (single or bulk item).

    Columns
    -------
    id              : Auto-incremented primary key.
    request_id      : UUID string shared across all items in one HTTP request.
    original_text   : Input text (up to 1000 chars).
    translated_text : Output text returned by the engine.
    source_language : Detected or provided source language code.
    target_language : Target language code supplied by the caller.
    engine          : 'google' or 'mock'.
    success         : Whether the translation succeeded.
    error_message   : Error detail when success=False.
    characters      : Character count of the original text.
    latency_ms      : Round-trip translation latency in milliseconds.
    is_bulk         : True when the request came from the bulk endpoint.
    created_at      : UTC timestamp of the log entry.
    client_host     : IP address of the caller (optional).
    """

    __tablename__ = "translation_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(String(36), nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=True)
    source_language = Column(String(10), nullable=False, default="auto")
    target_language = Column(String(10), nullable=False)
    engine = Column(String(20), nullable=False, default="mock")
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    characters = Column(Integer, nullable=False, default=0)
    latency_ms = Column(Float, nullable=True)
    is_bulk = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    client_host = Column(String(50), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<TranslationLog id={self.id} "
            f"lang={self.target_language} "
            f"engine={self.engine} "
            f"success={self.success}>"
        )
