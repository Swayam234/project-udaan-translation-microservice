"""
tests/conftest.py

Shared pytest fixtures for the entire test suite.
Uses FastAPI's TestClient backed by an in-memory SQLite database so tests
never touch the production database file.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import create_app
from app.database.connection import Base, get_db

# ── In-memory test database ────────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


def override_get_db():
    """Replace the production DB session with an in-memory session during tests."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def app():
    """Create the FastAPI app with the test database override."""
    # Create all tables in the in-memory database
    from app.database import models  # noqa: F401
    Base.metadata.create_all(bind=test_engine)

    application = create_app()
    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest.fixture(scope="session")
def client(app):
    """Return a synchronous TestClient for the test app."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
