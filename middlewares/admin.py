from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from services.admin_service import admin_service


class AdminOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[
            [Message, dict[str, Any]],
            Awaitable[Any],
        ],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user = event.from_user

        if user is None:
            return None

        if not await admin_service.is_authorized(
            user.id
        ):
            await event.answer(
                "⛔ <b>دسترسی غیرمجاز.</b>\n\n"
                "این بخش فقط برای Admin است."
            )
            return None

        return await handler(event, data)
