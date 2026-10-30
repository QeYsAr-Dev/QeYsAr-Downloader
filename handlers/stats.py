from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from database.repositories.statistics import get_total_users
from database.repositories.users import get_today_download_count, get_user


router = Router()


@router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

    count = await get_today_download_count(user.id)
    user_record = await get_user(user.id)
    total_users = await get_total_users()

    total_downloads = 0
    if user_record is not None:
        try:
            total_downloads = int(user_record["total_downloads"] or 0)
        except (KeyError, TypeError, IndexError):
            try:
                total_downloads = int(user_record[5] or 0)
            except (TypeError, IndexError):
                total_downloads = 0

    remaining = max(settings.daily_download_limit - count, 0)

    await message.answer(
        "📊 <b>آمار حساب شما</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ دانلودهای موفق: <b>{total_downloads}</b>\n"
        f"📥 دانلودهای امروز: <b>{count}</b>\n"
        f"🟢 سهمیه باقی‌مانده: <b>{remaining}</b>\n"
        f"🔢 سقف روزانه: <b>{settings.daily_download_limit}</b>\n"
        f"📦 حداکثر حجم فایل: <b>{settings.max_file_size_mb} MB</b>\n"
        f"👥 کل کاربران ربات: <b>{total_users:,}</b>"
    )
