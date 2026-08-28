from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import api


def test_webhook_requires_initialized_service() -> None:
    original_bot = api.bot
    original_dispatcher = api.dispatcher

    try:
        api.bot = None
        api.dispatcher = None

        client = TestClient(app=api.app)

        response = client.post(
            "/telegram/webhook",
            json={
                "update_id": 123,
            },
        )

        assert response.status_code == 503

    finally:
        api.bot = original_bot
        api.dispatcher = original_dispatcher


def test_webhook_processes_update_with_mock_service() -> None:
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
                "update_id": 321,
            },
        )

        assert response.status_code == 200
        assert response.json()["ok"] is True
        mock_dispatcher.feed_update.assert_awaited_once()

    finally:
        api.bot = original_bot
        api.dispatcher = original_dispatcher
