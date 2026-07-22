from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.2.0"}


def test_events_endpoint_and_limit_validation():
    assert client.get("/events?limit=10").json() == []
    assert client.get("/events?limit=0").status_code == 422
    assert client.get("/events?limit=1001").status_code == 422
