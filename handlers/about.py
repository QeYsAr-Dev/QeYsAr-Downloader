from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("about"))
async def about_handler(
    message: Message,
) -> None:
    await message.answer(
        "🤖 <b>QeYsAr Downloader</b>\n\n"
        "Telegram Downloader برای:\n"
        "• YouTube\n"
        "• Instagram\n"
        "• TikTok\n"
        "• Pinterest\n\n"
        "⚡ Async Processing\n"
        "📋 Per-user Download Control\n"
        "🛡️ Security & Rate Limiting\n"
        "🗄️ SQLite Database"
    )
