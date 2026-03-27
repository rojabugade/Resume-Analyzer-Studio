from fastapi.testclient import TestClient

from ai_agent_system.main import app


def test_health() -> None:
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
