"""
app/routes/translate.py

Translation endpoints:
  POST /translate        — single text translation
  POST /translate/bulk   — batch translation of multiple texts
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.repository import create_log
from app.models.schemas import (
    BulkTranslationRequest,
    BulkTranslationResponse,
    BulkTranslationItem,
    ErrorResponse,
    TranslationRequest,
    TranslationResponse,
)
from app.services.translation_service import translate_bulk, translate_text
from app.utils.helpers import generate_request_id, truncate
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/translate", tags=["Translation"])


# ── POST /translate ────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or unsupported language"},
        422: {"description": "Pydantic validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Translate a single text",
    description=(
        "Accepts a text string (≤ 1000 chars) and an ISO 639-1 target language code. "
        "Returns the translated text along with metadata about the translation engine used."
    ),
)
async def single_translate(
    request: Request,
    payload: TranslationRequest,
    db: Session = Depends(get_db),
) -> TranslationResponse:
    """Translate a single piece of text into the target language."""

    request_id = generate_request_id()
    client_host: str = request.client.host if request.client else "unknown"

    logger.info(
        "POST /translate  request_id=%s  lang=%s  chars=%d  client=%s",
        request_id, payload.target_language, len(payload.text), client_host,
    )

    result = translate_text(
        text=payload.text,
        target_language=payload.target_language,
        source_language=payload.source_language,
    )

    # ── Persist log entry ──────────────────────────────────────────────────
    _save_log(
        db=db,
        request_id=request_id,
        original_text=payload.text,
        result=result,
        is_bulk=False,
        client_host=client_host,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"],
        )

    return TranslationResponse(
        success=True,
        original_text=payload.text,
        translated_text=result["translated_text"],
        source_language=result["source_language"],
        target_language=result["target_language"],
        engine=result["engine"],
        characters_translated=len(payload.text),
    )


# ── POST /translate/bulk ───────────────────────────────────────────────────────

@router.post(
    "/bulk",
    response_model=BulkTranslationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        422: {"description": "Pydantic validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Translate multiple texts in one request",
    description=(
        "Accepts an array of strings (1–50 items, each ≤ 1000 chars) and a target language. "
        "Returns translated results for all items. Partial failures are reported per-item."
    ),
)
async def bulk_translate(
    request: Request,
    payload: BulkTranslationRequest,
    db: Session = Depends(get_db),
) -> BulkTranslationResponse:
    """Translate multiple texts in a single HTTP request."""

    request_id = generate_request_id()
    client_host = request.client.host if request.client else "unknown"

    logger.info(
        "POST /translate/bulk  request_id=%s  lang=%s  count=%d  client=%s",
        request_id, payload.target_language, len(payload.texts), client_host,
    )

    results = translate_bulk(
        texts=payload.texts,
        target_language=payload.target_language,
        source_language=payload.source_language,
    )

    # ── Persist one log entry per item ─────────────────────────────────────
    for result in results:
        _save_log(
            db=db,
            request_id=request_id,
            original_text=result["original_text"],
            result=result,
            is_bulk=True,
            client_host=client_host,
        )

    # ── Build response ─────────────────────────────────────────────────────
    items: list[BulkTranslationItem] = [
        BulkTranslationItem(
            index=r["index"],
            original_text=r["original_text"],
            translated_text=r["translated_text"] or "",
            success=r["success"],
            error=r.get("error"),
        )
        for r in results
    ]

    succeeded = sum(1 for r in results if r["success"])
    engine = results[0]["engine"] if results else "mock"
    src_lang = results[0]["source_language"] if results else payload.source_language or "auto"

    return BulkTranslationResponse(
        success=True,
        target_language=payload.target_language,
        source_language=src_lang,
        engine=engine,
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        results=items,
    )


# ── Private helper ─────────────────────────────────────────────────────────────

def _save_log(
    db: Session,
    request_id: str,
    original_text: str,
    result: dict,
    is_bulk: bool,
    client_host: str,
) -> None:
    """Persist a translation log entry. Errors are silently caught so they don't
    affect the HTTP response."""
    try:
        create_log(
            db=db,
            log_data={
                "request_id": request_id,
                "original_text": original_text,
                "translated_text": result.get("translated_text"),
                "source_language": result.get("source_language", "auto"),
                "target_language": result.get("target_language", ""),
                "engine": result.get("engine", "mock"),
                "success": result.get("success", False),
                "error_message": result.get("error"),
                "characters": len(original_text),
                "latency_ms": result.get("latency_ms"),
                "is_bulk": is_bulk,
                "client_host": client_host,
            },
        )
    except Exception as exc:
        logger.error("Failed to save translation log: %s", exc)
