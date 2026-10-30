from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "ℹ️ <b>راهنمای QeYsAr Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "<b>۱.</b> لینک محتوای موردنظر را کپی کنید.\n"
        "<b>۲.</b> لینک را مستقیماً برای ربات بفرستید.\n"
        "<b>۳.</b> منتظر پردازش و دریافت فایل بمانید.\n\n"
        "<b>پلتفرم‌های فعال:</b>\n"
        "• Instagram\n"
        "• TikTok\n"
        "• Pinterest\n\n"
        "<b>محدودیت‌ها:</b>\n"
        "• حداکثر <b>10 دانلود</b> در روز\n"
        "• حداکثر حجم هر فایل: <b>50 MB</b>\n"
        "• حداکثر <b>1 دانلود فعال</b> برای هر کاربر"
    )
