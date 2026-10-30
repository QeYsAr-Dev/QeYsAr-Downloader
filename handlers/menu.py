from html import escape

from aiogram import F, Router
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from config import settings
from database.repositories.downloads import get_user_history
from database.repositories.statistics import get_total_users
from database.repositories.users import (
    get_today_download_count,
    get_user,
)
from keyboards.force_join import CHANNEL_URL, creator_channel_keyboard
from keyboards.main import (
    ABOUT,
    CLOSE_PANEL,
    CREATOR_CHANNEL,
    CREATOR_PANEL,
    HELP,
    HISTORY,
    MY_STATS,
    SETTINGS,
    START_DOWNLOAD,
    main_menu_keyboard,
)
from services.admin_service import admin_service


router = Router()


def row_value(row, key: str, index: int):
    if row is None:
        return None

    if hasattr(row, "keys"):
        try:
            if key in row.keys():
                return row[key]
        except (TypeError, AttributeError):
            pass

    try:
        return row[index]
    except (IndexError, KeyError, TypeError):
        return None


async def answer_panel(message: Message, text: str) -> None:
    user = message.from_user
    show_creator = False

    if user is not None:
        show_creator = await admin_service.is_authorized(user.id)

    await message.answer(
        text,
        reply_markup=main_menu_keyboard(show_creator=show_creator),
    )


@router.message(F.text == START_DOWNLOAD)
async def start_download_menu(message: Message) -> None:
    await answer_panel(
        message,
        "📥 <b>شروع دانلود</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "لینک محتوای موردنظرت را ارسال کن.\n\n"
        "🌐 <b>پلتفرم‌های پشتیبانی‌شده</b>\n"
        "📸 Instagram\n"
        "🎵 TikTok\n"
        "📌 Pinterest\n\n"
        "📦 حداکثر حجم فایل: <b>50 MB</b>\n"
        "🔢 سهمیه روزانه: <b>10 دانلود</b>\n"
        "⚡ هر کاربر در هر لحظه: <b>1 دانلود فعال</b>\n\n"
        "پس از دریافت فایل، می‌توانی لینک بعدی را ارسال کنی.",
    )


@router.message(F.text == MY_STATS)
async def stats_menu(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

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

    await answer_panel(
        message,
        "📊 <b>داشبورد آمار شما</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 دانلودهای موفق: <b>{personal_total}</b>\n"
        f"📥 دانلودهای امروز: <b>{today_count}</b>\n"
        f"🟢 سهمیه باقی‌مانده: <b>{remaining}</b>\n"
        f"👥 کل کاربران ربات: <b>{total_users:,}</b>\n\n"
        f"📦 حداکثر حجم هر فایل: <b>{settings.max_file_size_mb} MB</b>",
    )


@router.message(F.text == HISTORY)
async def history_menu(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

    rows = await get_user_history(user.id, limit=5)

    if not rows:
        await answer_panel(
            message,
            "🕘 <b>تاریخچه دانلودها</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "هنوز دانلودی برای حساب شما ثبت نشده است.",
        )
        return

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
            f"📦 <b>#{escape(str(download_id))}</b> · {platform}\n"
            f"وضعیت: <b>{status}</b>\n"
            f"🕒 {created}"
        )

    await answer_panel(message, "\n\n".join(lines))


@router.message(F.text == SETTINGS)
async def settings_menu(message: Message) -> None:
    await answer_panel(
        message,
        "⚙️ <b>تنظیمات و محدودیت‌های سرویس</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔢 سقف دانلود روزانه: <b>{settings.daily_download_limit}</b>\n"
        f"📦 حداکثر حجم هر فایل: <b>{settings.max_file_size_mb} MB</b>\n"
        "⚡ دانلود فعال برای هر کاربر: "
        f"<b>{settings.max_active_downloads_per_user}</b>\n\n"
        "این محدودیت‌ها برای همه کاربران اعمال می‌شوند.",
    )


@router.message(F.text == HELP)
async def help_menu(message: Message) -> None:
    await answer_panel(
        message,
        "ℹ️ <b>راهنمای استفاده از ربات</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "<b>۱.</b> لینک محتوای موردنظر را کپی کن.\n"
        "<b>۲.</b> لینک را مستقیماً برای ربات بفرست.\n"
        "<b>۳.</b> منتظر پردازش و ارسال فایل بمان.\n"
        "<b>۴.</b> پس از دریافت فایل، لینک بعدی را بفرست.\n\n"
        "<b>پلتفرم‌ها:</b> Instagram، TikTok و Pinterest\n"
        "<b>محدودیت حجم:</b> 50 MB\n"
        "<b>سقف روزانه:</b> 10 دانلود",
    )


@router.message(F.text == ABOUT)
async def about_menu(message: Message) -> None:
    await answer_panel(
        message,
        "👤 <b>درباره QeYsAr Downloader</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "یک ابزار تلگرامی برای دریافت محتوای پشتیبانی‌شده.\n\n"
        "🌐 <b>Instagram · TikTok · Pinterest</b>\n\n"
        "⚡ پردازش خودکار\n"
        "🛡️ کنترل محدودیت کاربران\n"
        "📋 تاریخچه دانلودها\n"
        "📊 آمار مبتنی بر اطلاعات دیتابیس\n\n"
        "سازنده: <b>QeYsAr_Dev</b>",
    )


@router.message(F.text == CREATOR_CHANNEL)
async def creator_channel_menu(message: Message) -> None:
    await message.answer(
        "📢 <b>کانال رسمی سازنده</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "برای مشاهده کانال رسمی QeYsAr_Dev از دکمه زیر استفاده کن.",
        reply_markup=creator_channel_keyboard(),
    )


@router.message(F.text == CLOSE_PANEL)
async def close_panel_menu(message: Message) -> None:
    await message.answer(
        "✅ <b>منو بسته شد.</b>\n\n"
        "برای نمایش دوباره منو، دستور /start را ارسال کن.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.text == CREATOR_PANEL)
async def creator_panel_menu(message: Message) -> None:
    user = message.from_user

    if user is None or not await admin_service.is_authorized(user.id):
        await message.answer(
            "⛔ <b>دسترسی غیرمجاز</b>\n"
            "این بخش فقط برای سازنده ربات فعال است."
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
        f"🟢 کاربران فعال ۲۴ ساعت: <b>{data['active_users']:,}</b>\n"
        f"📥 کل دانلودهای موفق: <b>{data['total_downloads']:,}</b>\n"
        f"📅 دانلودهای ۲۴ ساعت: <b>{data['downloads_24h']:,}</b>\n"
        f"📆 دانلودهای ۷ روز: <b>{data['downloads_7d']:,}</b>\n"
        f"🗓 دانلودهای ۳۰ روز: <b>{data['downloads_30d']:,}</b>\n"
        f"⚡ دانلودهای فعال: <b>{data['active_downloads']}</b>\n\n"
        "<b>آمار پلتفرم‌ها</b>\n"
        f"{platforms_text}\n\n"
        "برای دستورات مدیریتی کامل، دستور <code>/admin</code> را ارسال کن."
    )

    await message.answer(
        text,
        reply_markup=main_menu_keyboard(show_creator=True),
    )
