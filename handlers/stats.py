from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from database.repositories.users import (
    get_today_download_count,
)

router = Router()


@router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    user = message.from_user

    if user is None:
        return

    count = await get_today_download_count(user.id)
    remaining = max(
        settings.daily_download_limit - count,
        0,
    )

    await message.answer(
        "📊 <b>آمار امروز</b>\n\n"
        f"دانلود انجام‌شده: <b>{count}</b>\n"
        f"دانلود باقی‌مانده: <b>{remaining}</b>\n"
        f"سقف روزانه: <b>{settings.daily_download_limit}</b>\n"
        f"حداکثر حجم فایل: <b>{settings.max_file_size_mb} MB</b>"
    )
