from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings

router = Router()


@router.message(Command("settings"))
async def settings_handler(message: Message) -> None:
    await message.answer(
        "⚙️ <b>Settings</b>\n\n"
        f"Daily download limit: <b>{settings.daily_download_limit}</b>\n"
        f"Maximum file size: <b>{settings.max_file_size_mb} MB</b>\n"
        f"Active downloads per user: "
        f"<b>{settings.max_active_downloads_per_user}</b>"
    )
