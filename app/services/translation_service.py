"""
app/services/translation_service.py

Orchestration layer: selects the appropriate translation engine (Google or mock),
calls it, handles errors, and returns a normalised result dictionary.

This is the only module that routes and other services should call for
translation tasks — it hides all engine-selection complexity.
"""

import time
from typing import Optional
from app.config.settings import get_settings
from app.services.google_translator import google_translate, is_google_available
from app.services.mock_translator import mock_translate
from app.utils.logger import get_logger
from app.utils.helpers import measure_ms

logger = get_logger(__name__)
settings = get_settings()


def translate_text(
    text: str,
    target_language: str,
    source_language: Optional[str] = "auto",
) -> dict:
    """
    Translate a single piece of text into the target language.

    Engine selection
    ----------------
    - If GOOGLE_API_KEY is set → use Google Cloud Translation API.
    - Otherwise              → use the built-in mock dictionary.

    Parameters
    ----------
    text            : Plain text to translate (1–1000 chars).
    target_language : ISO 639-1 target language code.
    source_language : ISO 639-1 source language, or 'auto' (default).

    Returns
    -------
    A normalised dict:
        translated_text  (str)
        source_language  (str)   — detected or provided
        target_language  (str)
        engine           (str)   — 'google' | 'mock'
        latency_ms       (float)
        success          (bool)
        error            (str | None)

    Never raises; errors are captured in the returned dict.
    """
    start = time.perf_counter()
    engine = "google" if is_google_available() else "mock"

    try:
        _validate_language(target_language)

        if engine == "google":
            result = google_translate(text, target_language, source_language)
            translated = result["translated_text"]
            detected_src = result["detected_source"]
        else:
            translated = mock_translate(text, target_language)
            detected_src = source_language if source_language and source_language != "auto" else "en"

        latency = measure_ms(start)
        logger.info(
            "Translation OK  engine=%-6s  lang=%s  chars=%d  latency=%.1fms",
            engine, target_language, len(text), latency,
        )
        return {
            "translated_text": translated,
            "source_language": detected_src,
            "target_language": target_language,
            "engine": engine,
            "latency_ms": latency,
            "success": True,
            "error": None,
        }

    except ValueError as exc:
        # Input validation error (unsupported language, etc.)
        latency = measure_ms(start)
        logger.warning("Translation validation error: %s", exc)
        return _error_result(str(exc), engine, target_language, source_language, latency)

    except RuntimeError as exc:
        # Google API error — attempt mock fallback
        logger.error("Google API failed (%s). Falling back to mock translator.", exc)
        try:
            translated = mock_translate(text, target_language)
            latency = measure_ms(start)
            return {
                "translated_text": translated,
                "source_language": source_language or "en",
                "target_language": target_language,
                "engine": "mock",          # note: switched to mock
                "latency_ms": latency,
                "success": True,
                "error": None,
            }
        except Exception as fallback_exc:
            latency = measure_ms(start)
            logger.exception("Mock fallback also failed: %s", fallback_exc)
            return _error_result(
                f"Both Google and mock translators failed: {fallback_exc}",
                "mock", target_language, source_language, latency,
            )

    except Exception as exc:
        latency = measure_ms(start)
        logger.exception("Unexpected translation error: %s", exc)
        return _error_result(str(exc), engine, target_language, source_language, latency)


def translate_bulk(
    texts: list[str],
    target_language: str,
    source_language: Optional[str] = "auto",
) -> list[dict]:
    """
    Translate multiple texts sequentially, returning one result dict per item.

    Each item is translated independently so a failure in one does not block
    the rest.

    Parameters
    ----------
    texts           : List of strings to translate (each ≤ 1000 chars).
    target_language : ISO 639-1 target language code.
    source_language : ISO 639-1 source language, or 'auto'.

    Returns
    -------
    List of result dicts (same structure as `translate_text`), one per input.
    """
    logger.info(
        "Bulk translation started: %d texts → %s", len(texts), target_language
    )
    results: list[dict] = []
    for i, text in enumerate(texts):
        result = translate_text(text, target_language, source_language)
        result["index"] = i
        result["original_text"] = text
        results.append(result)

    succeeded = sum(1 for r in results if r["success"])
    logger.info(
        "Bulk translation complete: %d/%d succeeded → %s",
        succeeded, len(texts), target_language,
    )
    return results


# ── Private helpers ────────────────────────────────────────────────────────────

def _validate_language(language_code: str) -> None:
    """Raise ValueError if the language code is not in the supported list."""
    if language_code.lower() not in [lang.lower() for lang in settings.SUPPORTED_LANGUAGES]:
        raise ValueError(
            f"Language '{language_code}' is not supported. "
            f"Supported codes: {', '.join(settings.SUPPORTED_LANGUAGES)}"
        )


def _error_result(
    error_msg: str,
    engine: str,
    target_language: str,
    source_language: Optional[str],
    latency_ms: float,
) -> dict:
    return {
        "translated_text": None,
        "source_language": source_language or "auto",
        "target_language": target_language,
        "engine": engine,
        "latency_ms": latency_ms,
        "success": False,
        "error": error_msg,
    }
