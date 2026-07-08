"""
app/models/schemas.py

Pydantic v2 request / response schemas for the translation API.
All models include type hints, field-level validation, and OpenAPI examples.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ── Reusable field definitions ─────────────────────────────────────────────────

def _text_field() -> Field:  # type: ignore[return]
    return Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text to translate (1–1000 characters).",
        examples=["Hello, how are you?"],
    )


def _lang_field() -> Field:  # type: ignore[return]
    return Field(
        ...,
        min_length=2,
        max_length=5,
        description="ISO 639-1 target language code (e.g. hi, ta, kn, bn).",
        examples=["hi"],
    )


# ── Single-translation request ─────────────────────────────────────────────────

class TranslationRequest(BaseModel):
    """Payload for POST /translate."""

    text: str = _text_field()
    target_language: str = _lang_field()
    source_language: Optional[str] = Field(
        default="auto",
        description="ISO 639-1 source language code. Defaults to 'auto' (auto-detect).",
        examples=["en"],
    )

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be blank or whitespace only.")
        return v.strip()

    @field_validator("target_language", "source_language", mode="before")
    @classmethod
    def lowercase_lang(cls, v: Optional[str]) -> Optional[str]:
        return v.lower().strip() if v else v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Hello, how are you?",
                    "target_language": "hi",
                    "source_language": "en",
                }
            ]
        }
    }


# ── Single-translation response ────────────────────────────────────────────────

class TranslationResponse(BaseModel):
    """Response body for POST /translate."""

    success: bool = Field(True, description="Whether the translation succeeded.")
    original_text: str = Field(..., description="The original input text.")
    translated_text: str = Field(..., description="The translated output text.")
    source_language: str = Field(..., description="Detected or provided source language.")
    target_language: str = Field(..., description="Target language code.")
    engine: str = Field(..., description="Translation engine used (google | mock).")
    characters_translated: int = Field(..., description="Number of characters translated.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "original_text": "Hello, how are you?",
                    "translated_text": "नमस्ते, आप कैसे हैं?",
                    "source_language": "en",
                    "target_language": "hi",
                    "engine": "mock",
                    "characters_translated": 19,
                }
            ]
        }
    }


# ── Bulk-translation request ───────────────────────────────────────────────────

class BulkTranslationRequest(BaseModel):
    """Payload for POST /translate/bulk."""

    texts: list[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Array of texts to translate (1–50 items, each ≤ 1000 chars).",
    )
    target_language: str = _lang_field()
    source_language: Optional[str] = Field(
        default="auto",
        description="ISO 639-1 source language code. Defaults to 'auto'.",
    )

    @field_validator("texts", mode="before")
    @classmethod
    def validate_texts(cls, v: list) -> list:
        if not v:
            raise ValueError("texts array must not be empty.")
        for i, text in enumerate(v):
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"texts[{i}] is empty or not a string.")
            if len(text) > 1000:
                raise ValueError(
                    f"texts[{i}] exceeds 1000 characters (got {len(text)})."
                )
        return [t.strip() for t in v]

    @field_validator("target_language", "source_language", mode="before")
    @classmethod
    def lowercase_lang(cls, v: Optional[str]) -> Optional[str]:
        return v.lower().strip() if v else v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "texts": ["Good morning", "Thank you", "How are you?"],
                    "target_language": "ta",
                    "source_language": "en",
                }
            ]
        }
    }


# ── Bulk-translation response ──────────────────────────────────────────────────

class BulkTranslationItem(BaseModel):
    """A single item within a bulk translation response."""

    index: int = Field(..., description="Zero-based index from the input array.")
    original_text: str
    translated_text: str
    success: bool
    error: Optional[str] = Field(None, description="Error message if this item failed.")


class BulkTranslationResponse(BaseModel):
    """Response body for POST /translate/bulk."""

    success: bool
    target_language: str
    source_language: str
    engine: str
    total: int = Field(..., description="Total number of texts submitted.")
    succeeded: int = Field(..., description="Number of successfully translated texts.")
    failed: int = Field(..., description="Number of failed translations.")
    results: list[BulkTranslationItem]


# ── Health-check response ──────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str = Field(..., description="'healthy' or 'degraded'.")
    app_name: str
    version: str
    translation_engine: str = Field(
        ..., description="Active engine: 'google' or 'mock'."
    )
    database: str = Field(..., description="'connected' or 'error'.")
    timestamp: datetime


# ── Error response ─────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standard error envelope."""

    success: bool = False
    error: str
    detail: Optional[str] = None
