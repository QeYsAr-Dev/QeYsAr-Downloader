from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "ℹ️ <b>QeYsAr Downloader</b>\n\n"
        "لینک محتوا را مستقیماً برای ربات ارسال کنید.\n\n"
        "<b>پلتفرم‌های پشتیبانی‌شده:</b>\n"
        "• YouTube\n"
        "• Instagram\n"
        "• TikTok\n"
        "• Pinterest\n\n"
        "<b>محدودیت‌ها:</b>\n"
        "• حداکثر 10 دانلود در روز برای هر کاربر\n"
        "• حداکثر حجم هر فایل: 50 MB\n"
        "• هر کاربر در هر لحظه فقط یک دانلود فعال دارد\n\n"
        "بعد از ارسال کامل فایل، لینک بعدی را ارسال کنید."
    )
