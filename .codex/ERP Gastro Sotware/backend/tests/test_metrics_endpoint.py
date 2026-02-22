from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_metrics_endpoint_exposed_with_expected_series() -> None:
    with TestClient(app) as client:
        # Prime request counters once before scraping metrics.
        health = client.get("/api/v1/health")
        assert health.status_code == 200

        response = client.get("/metrics")
        assert response.status_code == 200
        body = response.text
        assert "http_requests_total" in body
        assert "gastro_active_sessions" in body
        assert "gastro_db_query_duration_seconds" in body
        assert "gastro_mhd_critical_count" in body
