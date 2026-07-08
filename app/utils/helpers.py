"""
app/utils/helpers.py

Shared utility functions used across the application.
"""

import uuid
import time
from functools import wraps
from typing import Callable, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_request_id() -> str:
    """Generate a RFC 4122 UUID v4 string for correlating log entries."""
    return str(uuid.uuid4())


def timer(func: Callable) -> Callable:
    """
    Decorator that measures the execution time of a function (sync or async)
    and logs it at DEBUG level.

    Returns
    -------
    A tuple (result, elapsed_ms) when used, or the raw result when the
    wrapped function is called normally.
    """
    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.debug("%s completed in %.2f ms", func.__qualname__, elapsed_ms)
        return result, elapsed_ms

    return sync_wrapper


def measure_ms(start: float) -> float:
    """Return elapsed milliseconds since `start` (from time.perf_counter())."""
    return round((time.perf_counter() - start) * 1000, 2)


def truncate(text: str, max_len: int = 80) -> str:
    """Return a truncated string for safe log output."""
    return text if len(text) <= max_len else text[:max_len] + "…"


def language_name(iso_code: str) -> str:
    """Map common ISO 639-1 codes to human-readable language names."""
    _MAP = {
        "hi": "Hindi",      "ta": "Tamil",   "kn": "Kannada",
        "bn": "Bengali",    "te": "Telugu",  "mr": "Marathi",
        "gu": "Gujarati",   "ml": "Malayalam", "pa": "Punjabi",
        "ur": "Urdu",       "or": "Odia",    "as": "Assamese",
        "fr": "French",     "de": "German",  "es": "Spanish",
        "en": "English",    "auto": "Auto-detect",
    }
    return _MAP.get(iso_code.lower(), iso_code.upper())
