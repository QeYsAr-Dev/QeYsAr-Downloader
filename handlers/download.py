import logging

from aiogram import Router
from aiogram.types import Message

from services.download_service import download_service

router = Router()

logger = logging.getLogger(__name__)


@router.message()
async def download_entry_handler(
    message: Message,
) -> None:
    if not message.text:
        return

    text = message.text.strip()

    if not text or text.startswith("/"):
        return

    try:
        await download_service.process(
            message=message,
            url=text,
        )
    except Exception:
        logger.exception(
            "Unhandled download handler exception. user_id=%s",
            message.from_user.id if message.from_user else None,
        )

        await message.answer(
            "❌ <b>خطای غیرمنتظره‌ای رخ داد.</b>\n\n"
            "لطفاً دوباره تلاش کنید."
        )
