"""
tests/test_health.py

Tests for the /health and /info endpoints.
"""

from fastapi import status


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

    def test_health_response_structure(self, client):
        data = client.get("/health").json()
        assert "status" in data
        assert "app_name" in data
        assert "version" in data
        assert "translation_engine" in data
        assert "database" in data
        assert "timestamp" in data

    def test_health_status_is_healthy(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_health_database_is_connected(self, client):
        data = client.get("/health").json()
        assert data["database"] == "connected"

    def test_info_endpoint(self, client):
        response = client.get("/info")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "supported_languages" in data
        assert "limits" in data
        assert isinstance(data["supported_languages"], list)
        assert len(data["supported_languages"]) > 0
