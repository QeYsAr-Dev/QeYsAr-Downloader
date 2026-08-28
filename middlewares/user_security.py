from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from database.repositories.users import (
    is_user_banned,
)
from utils.url import is_valid_url


class UserSecurityMiddleware(BaseMiddleware):
    """
    Blocks banned users before handler execution.

    URL validation itself remains in the download service because
    it needs platform-level logic there.
    """

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

        if await is_user_banned(user.id):
            await event.answer(
                "🚫 <b>دسترسی شما به ربات مسدود شده است.</b>"
            )
            return None

        return await handler(event, data)
