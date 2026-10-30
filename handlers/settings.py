from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings


router = Router()


@router.message(Command("settings"))
async def settings_handler(message: Message) -> None:
    await message.answer(
        "⚙️ <b>تنظیمات سرویس</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔢 سقف دانلود روزانه: <b>{settings.daily_download_limit}</b>\n"
        f"📦 حداکثر حجم هر فایل: <b>{settings.max_file_size_mb} MB</b>\n"
        "⚡ دانلود فعال هم‌زمان برای هر کاربر: "
        f"<b>{settings.max_active_downloads_per_user}</b>\n\n"
        "این محدودیت‌ها برای همه کاربران اعمال می‌شوند."
    )
