from fastapi.testclient import TestClient

from app.main import app


def test_root_and_health_endpoints(monkeypatch):
    monkeypatch.setattr("app.main.vector_store.load", lambda: True)

    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/health").json() == {"status": "healthy"}
