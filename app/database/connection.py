"""
app/database/connection.py

SQLite database connection and session management using SQLAlchemy.
The database file is created automatically on first run.
"""

import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import Engine
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ── Engine ─────────────────────────────────────────────────────────────────────

# connect_args is required for SQLite to allow multiple threads (FastAPI is async)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG,          # Log all SQL when DEBUG=True
)


@event.listens_for(Engine, "connect")
def enable_wal_mode(dbapi_connection, connection_record) -> None:
    """Enable WAL mode for better concurrent read/write performance."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.close()


# ── Session factory ────────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ── Declarative base ───────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


# ── Dependency ─────────────────────────────────────────────────────────────────

def get_db():
    """
    FastAPI dependency that yields a database session and ensures it is closed
    after the request completes, even if an exception is raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables defined in ORM models.
    Called once at application startup.
    """
    # Import models so SQLAlchemy registers them before creating tables.
    from app.database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialised — tables created (if not already present).")
