from unittest.mock import AsyncMock

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


def test_webhook_without_secret() -> None:
    original_bot = api.bot
    original_dispatcher = api.dispatcher

    try:
        mock_bot = object()

        mock_dispatcher = type(
            "DispatcherStub",
            (),
            {
                "feed_update": AsyncMock(),
            },
        )()

        api.bot = mock_bot
        api.dispatcher = mock_dispatcher

        client = TestClient(app=api.app)

        response = client.post(
            "/telegram/webhook",
            json={
                "update_id": 123,
            },
        )

        assert response.status_code == 200
        assert response.json()["ok"] is True
        mock_dispatcher.feed_update.assert_awaited_once()

    finally:
        api.bot = original_bot
        api.dispatcher = original_dispatcher
