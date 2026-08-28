from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from database.repositories.admin import (
    get_banned_user_count,
    get_download_counts_by_status,
    get_limited_user_count,
)
from database.repositories.admins import (
    ensure_admin,
)
from database.repositories.logs import (
    add_log,
    get_recent_logs,
)
from database.repositories.users import (
    get_user,
    set_user_banned,
    set_user_limited,
)
from services.admin_service import admin_service
from services.broadcast_service import (
    broadcast_service,
)
from services.monitoring_service import (
    monitoring_service,
)

router = Router()


async def is_admin(
    message: Message,
) -> bool:
    user = message.from_user

    if user is None:
        return False

    return await admin_service.is_authorized(
        user.id
    )


def parse_target_user_id(
    message: Message,
) -> int | None:
    text = message.text or ""
    parts = text.split(
        maxsplit=1
    )

    if len(parts) != 2:
        return None

    value = parts[1].strip()

    if not value.isdigit():
        return None

    return int(value)


@router.message(Command("admin"))
async def admin_dashboard(
    message: Message,
) -> None:
    if not await is_admin(message):
        await message.answer(
            "⛔ <b>دسترسی غیرمجاز.</b>"
        )
        return

    dashboard = (
        await admin_service.get_dashboard()
    )

    banned_users = (
        await get_banned_user_count()
    )

    limited_users = (
        await get_limited_user_count()
    )

    status_rows = (
        await get_download_counts_by_status()
    )

    runtime = (
        monitoring_service.get_runtime_stats()
    )

    platform_lines = [
        f"• {platform}: <b>{count}</b>"
        for platform, count
        in dashboard["platforms"]
    ]

    status_lines = [
        f"• {status}: <b>{count}</b>"
        for status, count
        in status_rows
    ]

    platforms_text = (
        "\n".join(platform_lines)
        if platform_lines
        else "داده‌ای وجود ندارد."
    )

    statuses_text = (
        "\n".join(status_lines)
        if status_lines
        else "داده‌ای وجود ندارد."
    )

    active_ids = runtime.active_user_ids

    active_ids_text = (
        ", ".join(
            str(user_id)
            for user_id in active_ids
        )
        if active_ids
        else "هیچ‌کس"
    )

    await message.answer(
        "👑 <b>QeYsAr Admin Dashboard</b>\n\n"
        f"👤 کاربران: "
        f"<b>{dashboard['total_users']}</b>\n"
        f"🟢 فعال 24h: "
        f"<b>{dashboard['active_users']}</b>\n"
        f"📥 دانلود کل: "
        f"<b>{dashboard['total_downloads']}</b>\n"
        f"📅 دانلود 24h: "
        f"<b>{dashboard['downloads_24h']}</b>\n"
        f"📆 دانلود 7 روز: "
        f"<b>{dashboard['downloads_7d']}</b>\n"
        f"🗓 دانلود 30 روز: "
        f"<b>{dashboard['downloads_30d']}</b>\n"
        f"🚫 Ban شده: "
        f"<b>{banned_users}</b>\n"
        f"⛔ محدودشده: "
        f"<b>{limited_users}</b>\n"
        f"⚡ دانلود فعال: "
        f"<b>{runtime.active_downloads}</b>\n"
        f"👥 User IDs فعال: "
        f"<b>{active_ids_text}</b>\n\n"
        "<b>Platform Statistics</b>\n"
        f"{platforms_text}\n\n"
        "<b>Download Status</b>\n"
        f"{statuses_text}\n\n"
        "<b>Admin Commands</b>\n"
        "/admin\n"
        "/ban USER_ID\n"
        "/unban USER_ID\n"
        "/limit USER_ID\n"
        "/unlimit USER_ID\n"
        "/broadcast MESSAGE\n"
        "/logs"
    )


@router.message(Command("ban"))
async def ban_user(
    message: Message,
) -> None:
    if not await is_admin(message):
        await message.answer(
            "⛔ دسترسی غیرمجاز."
        )
        return

    target_id = parse_target_user_id(
        message
    )

    if target_id is None:
        await message.answer(
            "فرمت صحیح:\n"
            "<code>/ban USER_ID</code>"
        )
        return

    if target_id == settings.admin_id:
        await message.answer(
            "❌ Admin اصلی قابل Ban نیست."
        )
        return

    target = await get_user(target_id)

    if target is None:
        await message.answer(
            "❌ کاربر پیدا نشد."
        )
        return

    await set_user_banned(
        target_id,
        True,
    )

    await add_log(
        level="INFO",
        event="admin_ban",
        user_id=message.from_user.id,
        message=f"target={target_id}",
    )

    await message.answer(
        f"✅ کاربر <code>{target_id}</code> Ban شد."
    )


@router.message(Command("unban"))
async def unban_user(
    message: Message,
) -> None:
    if not await is_admin(message):
        await message.answer(
            "⛔ دسترسی غیرمجاز."
        )
        return

    target_id = parse_target_user_id(
        message
    )

    if target_id is None:
        await message.answer(
            "فرمت صحیح:\n"
            "<code>/unban USER_ID</code>"
        )
        return

    target = await get_user(target_id)

    if target is None:
        await message.answer(
            "❌ کاربر پیدا نشد."
        )
        return

    await set_user_banned(
        target_id,
        False,
    )

    await add_log(
        level="INFO",
        event="admin_unban",
        user_id=message.from_user.id,
        message=f"target={target_id}",
    )

    await message.answer(
        f"✅ کاربر <code>{target_id}</code> Unban شد."
    )


@router.message(Command("limit"))
async def limit_user(
    message: Message,
) -> None:
    if not await is_admin(message):
        await message.answer(
            "⛔ دسترسی غیرمجاز."
        )
        return

    target_id = parse_target_user_id(
        message
    )

    if target_id is None:
        await message.answer(
            "فرمت صحیح:\n"
            "<code>/limit USER_ID</code>"
        )
        return

    target = await get_user(target_id)

    if target is None:
        await message.answer(
            "❌ کاربر پیدا نشد."
        )
        return

    await set_user_limited(
        target_id,
        True,
    )

    await add_log(
        level="INFO",
        event="admin_limit",
        user_id=message.from_user.id,
        message=f"target={target_id}",
    )

    await message.answer(
        f"✅ دانلود کاربر "
        f"<code>{target_id}</code> محدود شد."
    )


@router.message(Command("unlimit"))
async def unlimit_user(
    message: Message,
) -> None:
    if not await is_admin(message):
        await message.answer(
            "⛔ دسترسی غیرمجاز."
        )
        return

    target_id = parse_target_user_id(
        message
    )

    if target_id is None:
        await message.answer(
            "فرمت صحیح:\n"
            "<code>/unlimit USER_ID</code>"
        )
        return

    target = await get_user(target_id)

    if target is None:
        await message.answer(
            "❌ کاربر پیدا نشد."
        )
        return

    await set_user_limited(
        target_id,
        False,
    )

    await add_log(
        level="INFO",
        event="admin_unlimit",
        user_id=message.from_user.id,
        message=f"target={target_id}",
    )

    await message.answer(
        f"✅ محدودیت کاربر "
        f"<code>{target_id}</code> برداشته شد."
    )


@router.message(Command("broadcast"))
async def broadcast_user(
    message: Message,
) -> None:
    if not await is_admin(message):
        await message.answer(
            "⛔ دسترسی غیرمجاز."
        )
        return

    text = message.text or ""
    parts = text.split(
        maxsplit=1
    )

    if len(parts) != 2:
        await message.answer(
            "فرمت صحیح:\n"
            "<code>/broadcast MESSAGE</code>"
        )
        return

    broadcast_text = parts[1].strip()

    if not broadcast_text:
        await message.answer(
            "متن Broadcast خالی است."
        )
        return

    admin_user = message.from_user

    if admin_user is None:
        return

    status_message = await message.answer(
        "📢 <b>Broadcast شروع شد...</b>"
    )

    result = await broadcast_service.send(
        bot=message.bot,
        text=broadcast_text,
        admin_user_id=admin_user.id,
    )

    await status_message.edit_text(
        "📢 <b>Broadcast تمام شد.</b>\n\n"
        f"📨 کل: <b>{result.total}</b>\n"
        f"✅ موفق: <b>{result.sent}</b>\n"
        f"❌ ناموفق: <b>{result.failed}</b>"
    )


@router.message(Command("logs"))
async def logs_handler(
    message: Message,
) -> None:
    if not await is_admin(message):
        await message.answer(
            "⛔ دسترسی غیرمجاز."
        )
        return

    rows = await get_recent_logs(
        limit=15
    )

    if not rows:
        await message.answer(
            "📝 هنوز لاگی ثبت نشده است."
        )
        return

    lines = [
        "📝 <b>آخرین Logها</b>\n"
    ]

    for level, event, user_id, log_message, created_at in rows:
        lines.append(
            f"<b>{level}</b> | {event}\n"
            f"User: {user_id or '-'}\n"
            f"{log_message or '-'}\n"
            f"{created_at}"
        )

    await message.answer(
        "\n".join(lines)
    )


async def initialize_admin() -> None:
    if settings.admin_id > 0:
        await ensure_admin(
            settings.admin_id
        )
