from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import api


def _setup_mock_telegram_service():
    mock_bot = object()

    mock_dispatcher = type(
        "DispatcherStub",
        (),
        {
            "feed_update": AsyncMock(),
        },
    )()

    original_bot = api.bot
    original_dispatcher = api.dispatcher

    api.bot = mock_bot
    api.dispatcher = mock_dispatcher

    return (
        original_bot,
        original_dispatcher,
        mock_dispatcher,
    )


def test_webhook_rejects_invalid_secret(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "WEBHOOK_SECRET",
        "correct-secret",
    )

    (
        original_bot,
        original_dispatcher,
        _,
    ) = _setup_mock_telegram_service()

    try:
        client = TestClient(app=api.app)

        response = client.post(
            "/telegram/webhook",
            headers={
                "X-Telegram-Bot-Api-Secret-Token": "wrong-secret",
            },
            json={
                "update_id": 999,
            },
        )

        assert response.status_code == 403

    finally:
        api.bot = original_bot
        api.dispatcher = original_dispatcher


def test_webhook_accepts_valid_secret(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "WEBHOOK_SECRET",
        "correct-secret",
    )

    (
        original_bot,
        original_dispatcher,
        mock_dispatcher,
    ) = _setup_mock_telegram_service()

    try:
        client = TestClient(app=api.app)

        response = client.post(
            "/telegram/webhook",
            headers={
                "X-Telegram-Bot-Api-Secret-Token": "correct-secret",
            },
            json={
                "update_id": 999,
            },
        )

        assert response.status_code == 200
        assert response.json()["ok"] is True
        mock_dispatcher.feed_update.assert_awaited_once()

    finally:
        api.bot = original_bot
        api.dispatcher = original_dispatcher

