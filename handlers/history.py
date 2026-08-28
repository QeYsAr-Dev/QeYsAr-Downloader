from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repositories.downloads import get_user_history

router = Router()


@router.message(Command("history"))
async def history_handler(message: Message) -> None:
    user = message.from_user

    if user is None:
        return

    rows = await get_user_history(user.id, limit=10)

    if not rows:
        await message.answer(
            "🕘 <b>History</b>\n\n"
            "هنوز دانلودی ثبت نشده است."
        )
        return

    lines = [
        "🕘 <b>آخرین دانلودهای شما</b>\n"
    ]

    for row in rows:
        platform = row["platform"] or "unknown"
        status = row["status"]
        file_type = row["file_type"] or "-"
        created_at = row["created_at"]

        lines.append(
            f"#{row['id']} | "
            f"{platform} | "
            f"{file_type} | "
            f"{status}\n"
            f"{created_at}"
        )

    await message.answer("\n".join(lines))
