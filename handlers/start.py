from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.repositories.users import upsert_user
from database.repositories.statistics import get_total_users
from keyboards.main import main_menu_keyboard
from services.admin_service import admin_service

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

    total_users = await get_total_users()
    is_creator = await admin_service.is_authorized(user.id)

    await message.answer(
        "🧊 <b>QeYsAr Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 <b>مرکز هوشمند دانلود محتوا</b>\n"
        "🟢 وضعیت سرویس: آنلاین\n\n"
        "👥 کاربران ربات: <b>{:,}</b>\n\n"
        "🌐 <b>پلتفرم‌های فعال</b>\n"
        "📸 Instagram\n"
        "🎵 TikTok\n"
        "📌 Pinterest\n\n"
        "📦 حداکثر حجم: <b>50 MB</b>\n"
        "🔢 سقف روزانه: <b>10 دانلود</b>\n\n"
        "از پنل زیر بخش موردنظرت را انتخاب کن.".format(total_users),
        reply_markup=main_menu_keyboard(
            show_creator=is_creator,
        ),
    )