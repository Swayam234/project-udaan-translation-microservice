"""
app/utils/logger.py

Configures a structured, coloured console logger for the entire application.
Import `get_logger` in any module that needs logging.
"""

import logging
import sys
from app.config.settings import get_settings

settings = get_settings()

# ANSI colour codes for log levels (visible in terminals that support ANSI)
_LEVEL_COLOURS = {
    "DEBUG":    "\033[36m",   # Cyan
    "INFO":     "\033[32m",   # Green
    "WARNING":  "\033[33m",   # Yellow
    "ERROR":    "\033[31m",   # Red
    "CRITICAL": "\033[35m",   # Magenta
}
_RESET = "\033[0m"


class _ColouredFormatter(logging.Formatter):
    """Custom formatter that injects ANSI colour codes into the level name."""

    def format(self, record: logging.LogRecord) -> str:
        colour = _LEVEL_COLOURS.get(record.levelname, "")
        record.levelname = f"{colour}{record.levelname:<8}{_RESET}"
        return super().format(record)


def setup_logging() -> None:
    """
    Configure root logger.
    Called once at application startup from main.py.
    """
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = _ColouredFormatter(
        fmt="%(asctime)s  %(levelname)s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers when uvicorn reloads
    if not root.handlers:
        root.addHandler(handler)

    # Suppress overly verbose library loggers
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Call this instead of logging.getLogger directly."""
    return logging.getLogger(name)
