from fastapi.testclient import TestClient

import api


def test_root_endpoint() -> None:
    client = TestClient(app=api.app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_endpoint() -> None:
    client = TestClient(app=api.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_endpoint() -> None:
    client = TestClient(app=api.app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_webhook_without_configured_secret_is_rejected(monkeypatch) -> None:
    monkeypatch.delenv("WEBHOOK_SECRET", raising=False)

    client = TestClient(app=api.app)

    response = client.post(
        "/telegram/webhook",
        json={"update_id": 123},
    )

    assert response.status_code == 503
