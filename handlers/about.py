from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.force_join import creator_channel_keyboard


router = Router()


@router.message(Command("about"))
async def about_handler(message: Message) -> None:
    await message.answer(
        "🤖 <b>QeYsAr Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "ابزار تلگرامی دریافت محتوای پشتیبانی‌شده از:\n\n"
        "📸 <b>Instagram</b>\n"
        "🎵 <b>TikTok</b>\n"
        "📌 <b>Pinterest</b>\n\n"
        "⚡ <b>پردازش خودکار</b>\n"
        "📋 <b>تاریخچه دانلودها</b>\n"
        "🛡️ <b>کنترل امنیت و محدودیت کاربران</b>\n"
        "📊 <b>آمار مبتنی بر دیتابیس</b>\n\n"
        "سازنده: <b>QeYsAr_Dev</b>",
        reply_markup=creator_channel_keyboard(),
    )
