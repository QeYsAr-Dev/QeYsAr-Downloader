from html import escape

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from config import settings
from database.repositories.downloads import get_user_history
from database.repositories.statistics import get_total_users
from database.repositories.users import (
    get_today_download_count,
    get_user,
)
from keyboards.main import (
    main_menu_keyboard,
    panel_navigation_keyboard,
)
from services.admin_service import admin_service

router = Router()


def row_value(row, key: str, index: int):
    if row is None:
        return None

    if hasattr(row, "keys") and key in row.keys():
        return row[key]

    return row[index]


async def show_panel(
    callback: CallbackQuery,
    text: str,
    navigation: bool = True,
) -> None:
    if callback.message and hasattr(callback.message, "edit_text"):
        try:
            await callback.message.edit_text(
                text,
                reply_markup=(
                    panel_navigation_keyboard()
                    if navigation
                    else None
                ),
            )
        except TelegramBadRequest as exc:
            if "message is not modified" not in str(exc).lower():
                raise

    await callback.answer()


async def show_main_panel(callback: CallbackQuery) -> None:
    user = callback.from_user
    total_users = await get_total_users()
    is_creator = await admin_service.is_authorized(user.id)

    text = (
        "🧊 <b>QeYsAr Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 <b>مرکز هوشمند دانلود محتوا</b>\n"
        "🟢 وضعیت سرویس: آنلاین\n\n"
        f"👥 کاربران ربات: <b>{total_users:,}</b>\n\n"
        "🌐 <b>پلتفرم‌های فعال</b>\n"
        "📸 Instagram\n"
        "🎵 TikTok\n"
        "📌 Pinterest\n\n"
        "📦 حداکثر حجم: <b>50 MB</b>\n"
        "🔢 سقف روزانه: <b>10 دانلود</b>\n\n"
        "بخش موردنظرت را انتخاب کن."
    )

    if callback.message and hasattr(callback.message, "edit_text"):
        try:
            await callback.message.edit_text(
                text,
                reply_markup=main_menu_keyboard(is_creator),
            )
        except TelegramBadRequest as exc:
            if "message is not modified" not in str(exc).lower():
                raise

    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback: CallbackQuery) -> None:
    await show_main_panel(callback)


@router.callback_query(F.data == "close_panel")
async def close_panel_callback(callback: CallbackQuery) -> None:
    if callback.message and hasattr(callback.message, "edit_text"):
        await callback.message.edit_text(
            "✅ پنل بسته شد.\n\nبرای باز کردن دوباره، دستور /start را بفرست.",
            reply_markup=None,
        )

    await callback.answer()


@router.callback_query(F.data == "download_help")
async def download_help_callback(callback: CallbackQuery) -> None:
    await show_panel(
        callback,
        "📥 <b>شروع دانلود</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "یکی از لینک‌های زیر را برای ربات ارسال کن:\n\n"
        "📸 Instagram\n"
        "🎵 TikTok\n"
        "📌 Pinterest\n\n"
        "🟢 پس از ارسال لینک، دانلود به‌صورت خودکار شروع می‌شود.\n"
        "📦 حداکثر حجم هر فایل: <b>50 MB</b>",
    )


@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery) -> None:
    await show_panel(
        callback,
        "ℹ️ <b>راهنمای استفاده</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ لینک محتوای موردنظر را کپی کن.\n"
        "2️⃣ آن را برای ربات ارسال کن.\n"
        "3️⃣ منتظر پردازش بمان.\n"
        "4️⃣ فایل را در تلگرام دریافت کن.\n\n"
        "🌐 پلتفرم‌ها: Instagram، TikTok و Pinterest\n"
        "📦 محدودیت حجم: 50 MB\n"
        "🔢 محدودیت روزانه: 10 دانلود",
    )


@router.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery) -> None:
    await show_panel(
        callback,
        "👤 <b>درباره QeYsAr Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "یک ابزار تلگرامی برای دریافت محتوای پشتیبانی‌شده از:\n\n"
        "📸 Instagram\n"
        "🎵 TikTok\n"
        "📌 Pinterest\n\n"
        "⚡ پردازش خودکار\n"
        "🛡️ کنترل محدودیت کاربران\n"
        "📋 تاریخچه دانلودها\n"
        "📊 آمار واقعی از دیتابیس",
    )


@router.callback_query(F.data == "settings")
async def settings_callback(callback: CallbackQuery) -> None:
    await show_panel(
        callback,
        "⚙️ <b>تنظیمات سرویس</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔢 سقف روزانه: <b>{settings.daily_download_limit}</b>\n"
        f"📦 حداکثر حجم: <b>{settings.max_file_size_mb} MB</b>\n"
        f"⚡ دانلود هم‌زمان هر کاربر: "
        f"<b>{settings.max_active_downloads_per_user}</b>\n\n"
        "این محدودیت‌ها برای همه کاربران اعمال می‌شوند.",
    )


@router.callback_query(F.data == "stats")
async def stats_callback(callback: CallbackQuery) -> None:
    user = callback.from_user
    today_count = await get_today_download_count(user.id)
    user_record = await get_user(user.id)
    total_users = await get_total_users()

    personal_total = int(
        row_value(user_record, "total_downloads", 5) or 0
    )

    remaining = max(
        settings.daily_download_limit - today_count,
        0,
    )

    await show_panel(
        callback,
        "📊 <b>داشبورد آمار</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 دانلودهای موفق شما: <b>{personal_total}</b>\n"
        f"📥 دانلود امروز: <b>{today_count}</b>\n"
        f"🟢 سهمیه باقی‌مانده: <b>{remaining}</b>\n"
        f"👥 کل کاربران ربات: <b>{total_users:,}</b>\n\n"
        "📦 حداکثر حجم هر فایل: "
        f"<b>{settings.max_file_size_mb} MB</b>",
    )


@router.callback_query(F.data == "history")
async def history_callback(callback: CallbackQuery) -> None:
    rows = await get_user_history(
        callback.from_user.id,
        limit=5,
    )

    if not rows:
        text = (
            "🕘 <b>تاریخچه دانلودها</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "هنوز دانلودی برای حساب شما ثبت نشده است."
        )
    else:
        lines = [
            "🕘 <b>آخرین دانلودهای شما</b>",
            "━━━━━━━━━━━━━━━━━━",
            "",
        ]

        for row in rows:
            download_id = row_value(row, "id", 0)
            platform = escape(str(row_value(row, "platform", 3) or "-"))
            status = escape(str(row_value(row, "status", 5) or "-"))
            created = escape(str(row_value(row, "created_at", 7) or "-"))

            lines.append(
                f"📦 <b>#{download_id}</b> · {platform}\n"
                f"وضعیت: {status}\n"
                f"🕒 {created}\n"
            )

        text = "\n".join(lines)

    await show_panel(callback, text)


@router.callback_query(F.data == "creator_panel")
async def creator_panel_callback(callback: CallbackQuery) -> None:
    if not await admin_service.is_authorized(callback.from_user.id):
        await show_panel(
            callback,
            "⛔ <b>دسترسی غیرمجاز</b>\nاین بخش فقط برای سازنده ربات فعال است.",
        )
        return

    data = await admin_service.get_dashboard()

    platform_lines = [
        f"• {escape(str(name))}: <b>{count}</b>"
        for name, count in data["platforms"]
    ]

    platforms_text = (
        "\n".join(platform_lines)
        if platform_lines
        else "هنوز آماری ثبت نشده است."
    )

    text = (
        "👑 <b>پنل اختصاصی سازنده</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 کل کاربران: <b>{data['total_users']:,}</b>\n"
        f"🟢 کاربران فعال 24 ساعت: <b>{data['active_users']:,}</b>\n"
        f"📥 کل دانلودهای موفق: <b>{data['total_downloads']:,}</b>\n"
        f"📅 دانلودهای 24 ساعت: <b>{data['downloads_24h']:,}</b>\n"
        f"📆 دانلودهای 7 روز: <b>{data['downloads_7d']:,}</b>\n"
        f"🗓 دانلودهای 30 روز: <b>{data['downloads_30d']:,}</b>\n"
        f"⚡ دانلودهای فعال: <b>{data['active_downloads']}</b>\n\n"
        "<b>آمار پلتفرم‌ها</b>\n"
        f"{platforms_text}\n\n"
        "🛠 برای دستورات مدیریتی کامل، /admin را ارسال کن."
    )

    await show_panel(callback, text)