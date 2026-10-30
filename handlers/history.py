from html import escape

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repositories.downloads import get_user_history


router = Router()


def row_value(row, key: str, index: int):
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


@router.message(Command("history"))
async def history_handler(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

    rows = await get_user_history(user.id, limit=10)

    if not rows:
        await message.answer(
            "🕘 <b>تاریخچه دانلودها</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "هنوز دانلودی برای حساب شما ثبت نشده است."
        )
        return

    lines = [
        "🕘 <b>آخرین دانلودهای شما</b>",
        "━━━━━━━━━━━━━━━━━━",
        "",
    ]

    for row in rows:
        download_id = escape(str(row_value(row, "id", 0) or "-"))
        platform = escape(str(row_value(row, "platform", 3) or "-"))
        status = escape(str(row_value(row, "status", 5) or "-"))
        file_type = escape(str(row_value(row, "file_type", 6) or "-"))
        created = escape(str(row_value(row, "created_at", 7) or "-"))

        lines.append(
            f"📦 <b>#{download_id}</b> · {platform}\n"
            f"وضعیت: <b>{status}</b>\n"
            f"نوع فایل: <b>{file_type}</b>\n"
            f"🕒 {created}"
        )

    await message.answer("\n\n".join(lines))
