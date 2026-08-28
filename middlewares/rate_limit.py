from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from services.rate_limit_service import rate_limit_service


class RateLimitMiddleware(BaseMiddleware):
    """
    Applies rate limiting to ordinary message traffic.

    Commands are also protected because they are still incoming
    Telegram requests and can otherwise be abused for spam.
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

        result = await rate_limit_service.check(
            user.id
        )

        if result.allowed:
            return await handler(event, data)

        retry_seconds = max(
            1,
            int(result.retry_after + 0.999),
        )

        if result.reason in {
            "spam",
            "rate_limit",
            "blocked",
        }:
            await event.answer(
                "🛡️ <b>درخواست‌های شما بیش از حد مجاز است.</b>\n\n"
                f"لطفاً <b>{retry_seconds}</b> ثانیه صبر کنید."
            )

        return None
