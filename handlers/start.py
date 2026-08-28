from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.repositories.users import upsert_user
from keyboards.main import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    user = message.from_user

    if user is None:
        return

    await upsert_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    await message.answer(
        "🤖 <b>QeYsAr Downloader</b>\n\n"
        "لینک یکی از پلتفرم‌های زیر را ارسال کنید:\n\n"
        "• YouTube\n"
        "• Instagram\n"
        "• TikTok\n"
        "• Pinterest\n\n"
        "📦 حداکثر حجم فایل: <b>50 MB</b>\n"
        "🔢 سقف روزانه: <b>10 دانلود</b>",
        reply_markup=main_menu_keyboard(),
    )
