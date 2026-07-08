"""
app/config/settings.py

Centralised configuration using Pydantic BaseSettings.
All values can be overridden via environment variables or a .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings."""

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "Udaan Translation Microservice"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "A lightweight, modular REST API for translating text "
        "into multiple Indian languages."
    )
    DEBUG: bool = False

    # ── Server ────────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Google Translate ──────────────────────────────────────────────────────
    # Set GOOGLE_API_KEY in your .env or environment to enable live translation.
    # When absent the service falls back to the built-in mock dictionary.
    GOOGLE_API_KEY: str = ""

    # ── Database ──────────────────────────────────────────────────────────────
    # Path (relative or absolute) to the SQLite database file.
    DATABASE_URL: str = "sqlite:///./udaan_logs.db"

    # ── Translation limits ────────────────────────────────────────────────────
    MAX_TEXT_LENGTH: int = 1000        # characters per single request
    MAX_BULK_SENTENCES: int = 50       # maximum sentences in a bulk request

    # ── Supported ISO language codes ──────────────────────────────────────────
    SUPPORTED_LANGUAGES: list[str] = [
        "hi",   # Hindi
        "ta",   # Tamil
        "kn",   # Kannada
        "bn",   # Bengali
        "te",   # Telugu
        "mr",   # Marathi
        "gu",   # Gujarati
        "ml",   # Malayalam
        "pa",   # Punjabi
        "ur",   # Urdu
        "or",   # Odia
        "as",   # Assamese
        "fr",   # French  (demo extra)
        "de",   # German  (demo extra)
        "es",   # Spanish (demo extra)
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()
