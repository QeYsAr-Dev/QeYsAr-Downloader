import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, User

from database.repositories.statistics import get_total_users
from database.repositories.users import upsert_user
from keyboards.force_join import force_join_keyboard
from keyboards.main import main_menu_keyboard
from middlewares.force_join import JOIN_REQUIRED_TEXT, CHECK_FAILED_TEXT
from services.admin_service import admin_service
from services.force_join_service import is_user_joined


router = Router()
logger = logging.getLogger(__name__)


async def send_welcome(message: Message, user: User) -> None:
    await upsert_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    total_users = await get_total_users()
    is_creator = await admin_service.is_authorized(user.id)

    welcome_text = (
        "🧊 <b>QeYsAr Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 <b>مرکز هوشمند دانلود محتوا</b>\n"
        "🟢 وضعیت سرویس: <b>آنلاین</b>\n\n"
        f"👥 تعداد کاربران: <b>{total_users:,}</b>\n\n"
        "🌐 <b>پلتفرم‌های فعال</b>\n"
        "📸 <b>Instagram</b>\n"
        "🎵 <b>TikTok</b>\n"
        "📌 <b>Pinterest</b>\n\n"
        "📦 حداکثر حجم هر فایل: <b>50 MB</b>\n"
        "🔢 سقف دانلود روزانه: <b>10 دانلود</b>\n"
        "⚡ دانلود فعال هم‌زمان: <b>1 مورد برای هر کاربر</b>\n\n"
        "از منوی پایین، بخش موردنظرت را انتخاب کن."
    )

    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard(show_creator=is_creator),
    )


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    user = message.from_user

    if user is None:
        return

    await send_welcome(message, user)


@router.callback_query(F.data == "force_join_check")
async def force_join_check_callback(callback: CallbackQuery) -> None:
    try:
        joined = await is_user_joined(
            callback.bot,
            callback.from_user.id,
        )
    except Exception:
        logger.exception(
            "Membership confirmation failed. user_id=%s",
            callback.from_user.id,
        )
        await callback.answer(
            "بررسی عضویت با خطا مواجه شد.",
            show_alert=True,
        )

        if isinstance(callback.message, Message):
            await callback.message.answer(CHECK_FAILED_TEXT)

        return

    if not joined:
        await callback.answer(
            "هنوز عضویت شما در کانال تأیید نشده است.",
            show_alert=True,
        )

        if isinstance(callback.message, Message):
            await callback.message.answer(
                JOIN_REQUIRED_TEXT,
                reply_markup=force_join_keyboard(),
            )

        return

    await callback.answer("عضویت شما تأیید شد ✅")

    if isinstance(callback.message, Message):
        await send_welcome(
            callback.message,
            callback.from_user,
        )
