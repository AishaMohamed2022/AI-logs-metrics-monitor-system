import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "aiops-backend"
    assert "metrics_url" in data


def test_liveness_probe():
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "uptime_seconds" in data
    assert "timestamp" in data


@patch("app.api.health.check_database_connection")
@patch("app.api.health.check_redis_connection")
def test_readiness_probe_healthy(mock_redis, mock_db):
    mock_db.return_value = (True, "PostgreSQL connection OK")
    mock_redis.return_value = (True, "Redis connection OK")

    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert data["database"]["status"] == "UP"
    assert data["redis"]["status"] == "UP"


@patch("app.api.health.check_database_connection")
@patch("app.api.health.check_redis_connection")
def test_readiness_probe_unhealthy_when_db_down(mock_redis, mock_db):
    mock_db.return_value = (False, "Connection refused")
    mock_redis.return_value = (True, "Redis connection OK")

    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "UNHEALTHY"
    assert data["database"]["status"] == "DOWN"


def test_prometheus_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "aiops_backend" in response.text or "http" in response.text
