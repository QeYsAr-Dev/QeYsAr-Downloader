import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from keyboards.force_join import force_join_keyboard
from services.force_join_service import is_user_joined


logger = logging.getLogger(__name__)

JOIN_REQUIRED_TEXT = (
    "🔒 <b>عضویت در کانال الزامی است</b>\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    "برای استفاده از امکانات <b>QeYsAr Downloader</b>، "
    "ابتدا در کانال رسمی سازنده عضو شوید.\n\n"
    "پس از عضویت، روی دکمه «عضو شدم» بزنید تا عضویت شما بررسی شود."
)

CHECK_FAILED_TEXT = (
    "⚠️ <b>بررسی عضویت انجام نشد.</b>\n\n"
    "لطفاً کمی بعد دوباره امتحان کنید. "
    "در صورت ادامه مشکل، مدیر ربات باید دسترسی بررسی عضویت را در کانال فعال کند."
)


class ForceJoinMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        # The verification callback must reach its own handler.
        if isinstance(event, CallbackQuery) and event.data == "force_join_check":
            return await handler(event, data)

        user = getattr(event, "from_user", None)
        if user is None:
            return await handler(event, data)

        try:
            joined = await is_user_joined(event.bot, user.id)
        except Exception:
            logger.exception(
                "Channel membership check failed. user_id=%s",
                user.id,
            )

            if isinstance(event, Message):
                await event.answer(CHECK_FAILED_TEXT)
            else:
                await event.answer(
                    "بررسی عضویت فعلاً امکان‌پذیر نیست.",
                    show_alert=True,
                )

            return None

        if joined:
            return await handler(event, data)

        if isinstance(event, Message):
            await event.answer(
                JOIN_REQUIRED_TEXT,
                reply_markup=force_join_keyboard(),
            )
            return None

        await event.answer(
            "برای استفاده از ربات ابتدا در کانال سازنده عضو شوید.",
            show_alert=True,
        )

        if isinstance(event.message, Message):
            await event.message.answer(
                JOIN_REQUIRED_TEXT,
                reply_markup=force_join_keyboard(),
            )

        return None
