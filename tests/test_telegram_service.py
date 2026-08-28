from unittest.mock import AsyncMock

import pytest

from services.telegram_service import (
    TelegramService,
)


@pytest.mark.asyncio
async def test_process_update() -> None:
    bot = object()
    dispatcher = type(
        "DispatcherStub",
        (),
        {
            "feed_update": AsyncMock(),
        },
    )()

    service = TelegramService(
        bot=bot,
        dispatcher=dispatcher,
    )

    update = {
        "update_id": 123,
        "message": {
            "message_id": 1,
            "date": 1700000000,
            "chat": {
                "id": 100,
                "type": "private",
            },
            "from": {
                "id": 100,
                "is_bot": False,
                "first_name": "Test",
            },
            "text": "/start",
        },
    }

    await service.process_update(
        update
    )

    dispatcher.feed_update.assert_awaited_once()
