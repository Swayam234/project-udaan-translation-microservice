"""
app/services/google_translator.py

Google Cloud Translation API (v2 / Basic) adapter.

This module wraps the `google-cloud-translate` client library and exposes
a single `google_translate()` function.  If the GOOGLE_API_KEY environment
variable is set, the application will use this engine automatically.

Setup
-----
1. Obtain an API key from https://console.cloud.google.com/
2. Enable the "Cloud Translation API" for your project.
3. Set the key in your .env file:  GOOGLE_API_KEY=AIza...
"""

from typing import Optional
from app.utils.logger import get_logger
from app.config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


def google_translate(
    text: str,
    target_language: str,
    source_language: Optional[str] = None,
) -> dict:
    """
    Translate text using the Google Cloud Translation API (v2).

    Parameters
    ----------
    text            : Input text (≤ 1000 chars).
    target_language : ISO 639-1 target language code.
    source_language : ISO 639-1 source language, or None / 'auto' for auto-detect.

    Returns
    -------
    A dict with keys:
        translated_text  (str)
        detected_source  (str)   — language code as returned by Google

    Raises
    ------
    RuntimeError   : When the Google API call fails.
    ImportError    : When the google-cloud-translate package is not installed.
    """
    try:
        from google.cloud import translate_v2 as translate  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "The 'google-cloud-translate' package is not installed. "
            "Run: pip install google-cloud-translate"
        ) from exc

    try:
        client = translate.Client(client_options={"api_key": settings.GOOGLE_API_KEY})

        # Google auto-detects when source is not supplied or is 'auto'
        src = None if (not source_language or source_language == "auto") else source_language

        result = client.translate(
            text,
            target_language=target_language,
            source_language=src,
            format_="text",  # treat input as plain text (not HTML)
        )

        detected_source: str = result.get("detectedSourceLanguage", src or "unknown")
        translated: str = result["translatedText"]

        logger.info(
            "Google Translate: '%s' → '%s' (src=%s → tgt=%s)",
            text[:40],
            translated[:40],
            detected_source,
            target_language,
        )

        return {
            "translated_text": translated,
            "detected_source": detected_source,
        }

    except Exception as exc:
        logger.error("Google Translate API error: %s", exc)
        raise RuntimeError(f"Google Translate API error: {exc}") from exc


def is_google_available() -> bool:
    """Return True when a non-empty GOOGLE_API_KEY is configured."""
    return bool(settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY.strip())
