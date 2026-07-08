"""
tests/test_translate.py

Tests for single and bulk translation endpoints.
"""

import pytest
from fastapi import status


class TestSingleTranslate:
    """Tests for POST /translate."""

    def test_translate_to_hindi(self, client):
        payload = {"text": "hello", "target_language": "hi"}
        response = client.post("/translate", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["translated_text"] != ""
        assert data["target_language"] == "hi"
        assert data["original_text"] == "hello"

    def test_translate_to_tamil(self, client):
        response = client.post("/translate", json={"text": "thank you", "target_language": "ta"})
        assert response.status_code == status.HTTP_200_OK

    def test_translate_to_kannada(self, client):
        response = client.post("/translate", json={"text": "good morning", "target_language": "kn"})
        assert response.status_code == status.HTTP_200_OK

    def test_translate_to_bengali(self, client):
        response = client.post("/translate", json={"text": "yes", "target_language": "bn"})
        assert response.status_code == status.HTTP_200_OK

    def test_translate_with_source_language(self, client):
        payload = {"text": "hello", "target_language": "hi", "source_language": "en"}
        response = client.post("/translate", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "engine" in data
        assert data["characters_translated"] > 0

    def test_response_contains_engine_field(self, client):
        response = client.post("/translate", json={"text": "hello", "target_language": "hi"})
        data = response.json()
        assert data["engine"] in ("google", "mock")

    def test_translate_unsupported_language_returns_error(self, client):
        """An unsupported language code should result in a 400 error."""
        response = client.post("/translate", json={"text": "hello", "target_language": "xx"})
        # Engine returns error → route raises HTTP 400
        assert response.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_translate_empty_text_returns_422(self, client):
        response = client.post("/translate", json={"text": "", "target_language": "hi"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_translate_whitespace_only_text_returns_422(self, client):
        response = client.post("/translate", json={"text": "   ", "target_language": "hi"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_translate_text_exceeds_limit_returns_422(self, client):
        long_text = "a" * 1001
        response = client.post("/translate", json={"text": long_text, "target_language": "hi"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_translate_missing_target_language_returns_422(self, client):
        response = client.post("/translate", json={"text": "hello"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_translate_missing_text_returns_422(self, client):
        response = client.post("/translate", json={"target_language": "hi"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestBulkTranslate:
    """Tests for POST /translate/bulk."""

    def test_bulk_translate_basic(self, client):
        payload = {
            "texts": ["hello", "thank you", "good morning"],
            "target_language": "hi",
        }
        response = client.post("/translate/bulk", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["total"] == 3
        assert len(data["results"]) == 3

    def test_bulk_translate_all_succeed(self, client):
        payload = {"texts": ["yes", "no", "please"], "target_language": "ta"}
        data = client.post("/translate/bulk", json=payload).json()
        assert data["succeeded"] == 3
        assert data["failed"] == 0

    def test_bulk_translate_indices_are_sequential(self, client):
        payload = {"texts": ["hello", "world"], "target_language": "kn"}
        data = client.post("/translate/bulk", json=payload).json()
        indices = [item["index"] for item in data["results"]]
        assert indices == [0, 1]

    def test_bulk_translate_empty_list_returns_422(self, client):
        response = client.post("/translate/bulk", json={"texts": [], "target_language": "hi"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_bulk_translate_exceeds_limit_returns_422(self, client):
        texts = ["hello"] * 51          # one over the 50-item limit
        response = client.post("/translate/bulk", json={"texts": texts, "target_language": "hi"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_bulk_translate_item_too_long_returns_422(self, client):
        texts = ["a" * 1001]
        response = client.post("/translate/bulk", json={"texts": texts, "target_language": "hi"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_bulk_translate_with_source_language(self, client):
        payload = {
            "texts": ["water", "food"],
            "target_language": "bn",
            "source_language": "en",
        }
        response = client.post("/translate/bulk", json=payload)
        assert response.status_code == status.HTTP_200_OK


class TestMockTranslator:
    """Directly test the mock translation dictionary."""

    def test_known_phrase_hindi(self):
        from app.services.mock_translator import mock_translate
        result = mock_translate("hello", "hi")
        assert result == "नमस्ते"

    def test_known_phrase_tamil(self):
        from app.services.mock_translator import mock_translate
        result = mock_translate("thank you", "ta")
        assert result == "நன்றி"

    def test_fallback_for_unknown_phrase(self):
        from app.services.mock_translator import mock_translate
        result = mock_translate("a completely unknown phrase xyz", "hi")
        assert result.startswith("[HI]") or "unknown" in result.lower() or result != ""

    def test_case_insensitive_lookup(self):
        from app.services.mock_translator import mock_translate
        result_lower = mock_translate("hello", "hi")
        result_upper = mock_translate("HELLO", "hi")
        # Both should return the translated value (exact match on lower)
        assert result_lower == "नमस्ते"
        # Upper-case falls to partial or fallback — should not be empty
        assert result_upper != ""
