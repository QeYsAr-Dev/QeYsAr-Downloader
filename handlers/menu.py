from html import escape

from aiogram import F, Router
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from config import settings
from database.repositories.preferences import get_default_quality
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
        "ظ‹ع؛â€œآ¥ <b>ط·آ´ط·آ±ط¸ث†ط·آ¹ ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯</b>\n"
        "أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾\n\n"
        "ط¸â€‍ط؛إ’ط¸â€ ط¹آ© ط¸â€¦ط·آ­ط·ع¾ط¸ث†ط·آ§ط؛إ’ ط¸â€¦ط¸ث†ط·آ±ط·آ¯ط¸â€ ط·آ¸ط·آ±ط·ع¾ ط·آ±ط·آ§ ط·آ§ط·آ±ط·آ³ط·آ§ط¸â€‍ ط¹آ©ط¸â€ .\n\n"
        "ظ‹ع؛إ’ع¯ <b>ط¸آ¾ط¸â€‍ط·ع¾ط¸ظ¾ط·آ±ط¸â€¦أ¢â‚¬إ’ط¸â€،ط·آ§ط؛إ’ ط¸آ¾ط·آ´ط·ع¾ط؛إ’ط·آ¨ط·آ§ط¸â€ ط؛إ’أ¢â‚¬إ’ط·آ´ط·آ¯ط¸â€،</b>\n"
        "ظ‹ع؛â€œآ¸ Instagram\n"
        "ظ‹ع؛عکآµ TikTok\n"
        "ظ‹ع؛â€œإ’ Pinterest\n\n"
        "ظ‹ع؛â€œآ¦ ط·آ­ط·آ¯ط·آ§ط¹آ©ط·آ«ط·آ± ط·آ­ط·آ¬ط¸â€¦ ط¸ظ¾ط·آ§ط؛إ’ط¸â€‍: <b>50 MB</b>\n"
        "ظ‹ع؛â€‌آ¢ ط·آ³ط¸â€،ط¸â€¦ط؛إ’ط¸â€، ط·آ±ط¸ث†ط·آ²ط·آ§ط¸â€ ط¸â€،: <b>10 ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯</b>\n"
        "أ¢ع‘طŒ ط¸â€،ط·آ± ط¹آ©ط·آ§ط·آ±ط·آ¨ط·آ± ط·آ¯ط·آ± ط¸â€،ط·آ± ط¸â€‍ط·آ­ط·آ¸ط¸â€،: <b>1 ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ ط¸ظ¾ط·آ¹ط·آ§ط¸â€‍</b>\n\n"
        "ط¸آ¾ط·آ³ ط·آ§ط·آ² ط·آ¯ط·آ±ط؛إ’ط·آ§ط¸ظ¾ط·ع¾ ط¸ظ¾ط·آ§ط؛إ’ط¸â€‍ط·إ’ ط¸â€¦ط؛إ’أ¢â‚¬إ’ط·ع¾ط¸ث†ط·آ§ط¸â€ ط؛إ’ ط¸â€‍ط؛إ’ط¸â€ ط¹آ© ط·آ¨ط·آ¹ط·آ¯ط؛إ’ ط·آ±ط·آ§ ط·آ§ط·آ±ط·آ³ط·آ§ط¸â€‍ ط¹آ©ط¸â€ ط؛إ’.",
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
        "ظ‹ع؛â€œظ¹ <b>ط·آ¯ط·آ§ط·آ´ط·آ¨ط¸ث†ط·آ±ط·آ¯ ط·آ¢ط¸â€¦ط·آ§ط·آ± ط·آ´ط¸â€¦ط·آ§</b>\n"
        "أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾\n\n"
        f"ظ‹ع؛â€کآ¤ ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط¸â€،ط·آ§ط؛إ’ ط¸â€¦ط¸ث†ط¸ظ¾ط¸â€ڑ: <b>{personal_total}</b>\n"
        f"ظ‹ع؛â€œآ¥ ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط¸â€،ط·آ§ط؛إ’ ط·آ§ط¸â€¦ط·آ±ط¸ث†ط·آ²: <b>{today_count}</b>\n"
        f"ظ‹ع؛ع؛آ¢ ط·آ³ط¸â€،ط¸â€¦ط؛إ’ط¸â€، ط·آ¨ط·آ§ط¸â€ڑط؛إ’أ¢â‚¬إ’ط¸â€¦ط·آ§ط¸â€ ط·آ¯ط¸â€،: <b>{remaining}</b>\n"
        f"ظ‹ع؛â€کآ¥ ط¹آ©ط¸â€‍ ط¹آ©ط·آ§ط·آ±ط·آ¨ط·آ±ط·آ§ط¸â€  ط·آ±ط·آ¨ط·آ§ط·ع¾: <b>{total_users:,}</b>\n\n"
        f"ظ‹ع؛â€œآ¦ ط·آ­ط·آ¯ط·آ§ط¹آ©ط·آ«ط·آ± ط·آ­ط·آ¬ط¸â€¦ ط¸â€،ط·آ± ط¸ظ¾ط·آ§ط؛إ’ط¸â€‍: <b>{settings.max_file_size_mb} MB</b>",
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
            "ظ‹ع؛â€¢ع© <b>ط·ع¾ط·آ§ط·آ±ط؛إ’ط·آ®ط¹â€ ط¸â€، ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط¸â€،ط·آ§</b>\n"
            "أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾\n\n"
            "ط¸â€،ط¸â€ ط¸ث†ط·آ² ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط؛إ’ ط·آ¨ط·آ±ط·آ§ط؛إ’ ط·آ­ط·آ³ط·آ§ط·آ¨ ط·آ´ط¸â€¦ط·آ§ ط·آ«ط·آ¨ط·ع¾ ط¸â€ ط·آ´ط·آ¯ط¸â€، ط·آ§ط·آ³ط·ع¾.",
        )
        return

    lines = [
        "ظ‹ع؛â€¢ع© <b>ط·آ¢ط·آ®ط·آ±ط؛إ’ط¸â€  ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط¸â€،ط·آ§ط؛إ’ ط·آ´ط¸â€¦ط·آ§</b>",
        "أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾",
        "",
    ]

    for row in rows:
        download_id = row_value(row, "id", 0)
        platform = escape(str(row_value(row, "platform", 3) or "-"))
        status = escape(str(row_value(row, "status", 5) or "-"))
        created = escape(str(row_value(row, "created_at", 7) or "-"))

        lines.append(
            f"ظ‹ع؛â€œآ¦ <b>#{escape(str(download_id))}</b> ط¢آ· {platform}\n"
            f"ط¸ث†ط·آ¶ط·آ¹ط؛إ’ط·ع¾: <b>{status}</b>\n"
            f"ظ‹ع؛â€¢â€™ {created}"
        )

    await answer_panel(message, "\n\n".join(lines))


@router.message(F.text == SETTINGS)
async def settings_menu(message: Message) -> None:
    user = message.from_user

    default_quality = (
        await get_default_quality(user.id)
        if user is not None
        else None
    )

    quality_text = (
        f"{default_quality}p"
        if default_quality is not None
        else "ط®ظˆط¯ع©ط§ط±"
    )

    await answer_panel(
        message,
        "âڑ™ï¸ڈ <b>طھظ†ط¸غŒظ…ط§طھ ط³ط±ظˆغŒط³</b>\n"
        "â”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پ\n\n"
        f"ع©غŒظپغŒطھ ظ¾غŒط´â€Œظپط±ط¶ ط´ظ…ط§: <b>{quality_text}</b>\n"
        "ظپط±ظ…طھ: <b>ط§ظ†طھط®ط§ط¨ ط®ظˆط¯ع©ط§ط± ط±ط¨ط§طھ</b>\n\n"
        f"ط³ظ‚ظپ ط¯ط§ظ†ظ„ظˆط¯ ط±ظˆط²ط§ظ†ظ‡: <b>{settings.daily_download_limit}</b>\n"
        f"ط­ط¯ط§ع©ط«ط± ط­ط¬ظ… ظ‡ط± ظپط§غŒظ„: <b>{settings.max_file_size_mb} MB</b>\n"
        f"ط¯ط§ظ†ظ„ظˆط¯ ظپط¹ط§ظ„ ط¨ط±ط§غŒ ظ‡ط± ع©ط§ط±ط¨ط±: "
        f"<b>{settings.max_active_downloads_per_user}</b>\n\n"
        "ط¨ط±ط§غŒ طھط؛غŒغŒط± طھظ†ط¸غŒظ…ط§طھ ع©غŒظپغŒطھ غŒط§ ط¨ط§ط²ظ†ط´ط§ظ†غŒ ط¢ظ†طŒ ط¯ط³طھظˆط± "
        "<code>/settings</code> ط±ط§ ط§ط±ط³ط§ظ„ ع©ظ†غŒط¯."
    )


@router.message(F.text == HELP)
async def help_menu(message: Message) -> None:
    await answer_panel(
        message,
        "أ¢â€‍آ¹أ¯آ¸عˆ <b>ط·آ±ط·آ§ط¸â€،ط¸â€ ط¸â€¦ط·آ§ط؛إ’ ط·آ§ط·آ³ط·ع¾ط¸ظ¾ط·آ§ط·آ¯ط¸â€، ط·آ§ط·آ² ط·آ±ط·آ¨ط·آ§ط·ع¾</b>\n"
        "أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾\n\n"
        "<b>ط؛آ±.</b> ط¸â€‍ط؛إ’ط¸â€ ط¹آ© ط¸â€¦ط·آ­ط·ع¾ط¸ث†ط·آ§ط؛إ’ ط¸â€¦ط¸ث†ط·آ±ط·آ¯ط¸â€ ط·آ¸ط·آ± ط·آ±ط·آ§ ط¹آ©ط¸آ¾ط؛إ’ ط¹آ©ط¸â€ .\n"
        "<b>ط؛آ².</b> ط¸â€‍ط؛إ’ط¸â€ ط¹آ© ط·آ±ط·آ§ ط¸â€¦ط·آ³ط·ع¾ط¸â€ڑط؛إ’ط¸â€¦ط·آ§ط¸â€¹ ط·آ¨ط·آ±ط·آ§ط؛إ’ ط·آ±ط·آ¨ط·آ§ط·ع¾ ط·آ¨ط¸ظ¾ط·آ±ط·آ³ط·ع¾.\n"
        "<b>ط؛آ³.</b> ط¸â€¦ط¸â€ ط·ع¾ط·آ¸ط·آ± ط¸آ¾ط·آ±ط·آ¯ط·آ§ط·آ²ط·آ´ ط¸ث† ط·آ§ط·آ±ط·آ³ط·آ§ط¸â€‍ ط¸ظ¾ط·آ§ط؛إ’ط¸â€‍ ط·آ¨ط¸â€¦ط·آ§ط¸â€ .\n"
        "<b>ط؛آ´.</b> ط¸آ¾ط·آ³ ط·آ§ط·آ² ط·آ¯ط·آ±ط؛إ’ط·آ§ط¸ظ¾ط·ع¾ ط¸ظ¾ط·آ§ط؛إ’ط¸â€‍ط·إ’ ط¸â€‍ط؛إ’ط¸â€ ط¹آ© ط·آ¨ط·آ¹ط·آ¯ط؛إ’ ط·آ±ط·آ§ ط·آ¨ط¸ظ¾ط·آ±ط·آ³ط·ع¾.\n\n"
        "<b>ط¸آ¾ط¸â€‍ط·ع¾ط¸ظ¾ط·آ±ط¸â€¦أ¢â‚¬إ’ط¸â€،ط·آ§:</b> Instagramط·إ’ TikTok ط¸ث† Pinterest\n"
        "<b>ط¸â€¦ط·آ­ط·آ¯ط¸ث†ط·آ¯ط؛إ’ط·ع¾ ط·آ­ط·آ¬ط¸â€¦:</b> 50 MB\n"
        "<b>ط·آ³ط¸â€ڑط¸ظ¾ ط·آ±ط¸ث†ط·آ²ط·آ§ط¸â€ ط¸â€،:</b> 10 ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯",
    )


@router.message(F.text == ABOUT)
async def about_menu(message: Message) -> None:
    await answer_panel(
        message,
        "ظ‹ع؛â€کآ¤ <b>ط·آ¯ط·آ±ط·آ¨ط·آ§ط·آ±ط¸â€، QeYsAr Downloader</b>\n"
        "أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾\n\n"
        "ط؛إ’ط¹آ© ط·آ§ط·آ¨ط·آ²ط·آ§ط·آ± ط·ع¾ط¸â€‍ط¹آ¯ط·آ±ط·آ§ط¸â€¦ط؛إ’ ط·آ¨ط·آ±ط·آ§ط؛إ’ ط·آ¯ط·آ±ط؛إ’ط·آ§ط¸ظ¾ط·ع¾ ط¸â€¦ط·آ­ط·ع¾ط¸ث†ط·آ§ط؛إ’ ط¸آ¾ط·آ´ط·ع¾ط؛إ’ط·آ¨ط·آ§ط¸â€ ط؛إ’أ¢â‚¬إ’ط·آ´ط·آ¯ط¸â€،.\n\n"
        "ظ‹ع؛إ’ع¯ <b>Instagram ط¢آ· TikTok ط¢آ· Pinterest</b>\n\n"
        "أ¢ع‘طŒ ط¸آ¾ط·آ±ط·آ¯ط·آ§ط·آ²ط·آ´ ط·آ®ط¸ث†ط·آ¯ط¹آ©ط·آ§ط·آ±\n"
        "ظ‹ع؛â€؛طŒأ¯آ¸عˆ ط¹آ©ط¸â€ ط·ع¾ط·آ±ط¸â€‍ ط¸â€¦ط·آ­ط·آ¯ط¸ث†ط·آ¯ط؛إ’ط·ع¾ ط¹آ©ط·آ§ط·آ±ط·آ¨ط·آ±ط·آ§ط¸â€ \n"
        "ظ‹ع؛â€œâ€¹ ط·ع¾ط·آ§ط·آ±ط؛إ’ط·آ®ط¹â€ ط¸â€، ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط¸â€،ط·آ§\n"
        "ظ‹ع؛â€œظ¹ ط·آ¢ط¸â€¦ط·آ§ط·آ± ط¸â€¦ط·آ¨ط·ع¾ط¸â€ ط؛إ’ ط·آ¨ط·آ± ط·آ§ط·آ·ط¸â€‍ط·آ§ط·آ¹ط·آ§ط·ع¾ ط·آ¯ط؛إ’ط·ع¾ط·آ§ط·آ¨ط؛إ’ط·آ³\n\n"
        "ط·آ³ط·آ§ط·آ²ط¸â€ ط·آ¯ط¸â€،: <b>QeYsAr_Dev</b>",
    )


@router.message(F.text == CREATOR_CHANNEL)
async def creator_channel_menu(message: Message) -> None:
    await message.answer(
        "ظ‹ع؛â€œآ¢ <b>ط¹آ©ط·آ§ط¸â€ ط·آ§ط¸â€‍ ط·آ±ط·آ³ط¸â€¦ط؛إ’ ط·آ³ط·آ§ط·آ²ط¸â€ ط·آ¯ط¸â€،</b>\n"
        "أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾\n\n"
        "ط·آ¨ط·آ±ط·آ§ط؛إ’ ط¸â€¦ط·آ´ط·آ§ط¸â€،ط·آ¯ط¸â€، ط¹آ©ط·آ§ط¸â€ ط·آ§ط¸â€‍ ط·آ±ط·آ³ط¸â€¦ط؛إ’ QeYsAr_Dev ط·آ§ط·آ² ط·آ¯ط¹آ©ط¸â€¦ط¸â€، ط·آ²ط؛إ’ط·آ± ط·آ§ط·آ³ط·ع¾ط¸ظ¾ط·آ§ط·آ¯ط¸â€، ط¹آ©ط¸â€ .",
        reply_markup=creator_channel_keyboard(),
    )


@router.message(F.text == CLOSE_PANEL)
async def close_panel_menu(message: Message) -> None:
    await message.answer(
        "أ¢إ“â€¦ <b>ط¸â€¦ط¸â€ ط¸ث† ط·آ¨ط·آ³ط·ع¾ط¸â€، ط·آ´ط·آ¯.</b>\n\n"
        "ط·آ¨ط·آ±ط·آ§ط؛إ’ ط¸â€ ط¸â€¦ط·آ§ط؛إ’ط·آ´ ط·آ¯ط¸ث†ط·آ¨ط·آ§ط·آ±ط¸â€، ط¸â€¦ط¸â€ ط¸ث†ط·إ’ ط·آ¯ط·آ³ط·ع¾ط¸ث†ط·آ± /start ط·آ±ط·آ§ ط·آ§ط·آ±ط·آ³ط·آ§ط¸â€‍ ط¹آ©ط¸â€ .",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.text == CREATOR_PANEL)
async def creator_panel_menu(message: Message) -> None:
    user = message.from_user

    if user is None or not await admin_service.is_authorized(user.id):
        await message.answer(
            "أ¢â€؛â€‌ <b>ط·آ¯ط·آ³ط·ع¾ط·آ±ط·آ³ط؛إ’ ط·ط›ط؛إ’ط·آ±ط¸â€¦ط·آ¬ط·آ§ط·آ²</b>\n"
            "ط·آ§ط؛إ’ط¸â€  ط·آ¨ط·آ®ط·آ´ ط¸ظ¾ط¸â€ڑط·آ· ط·آ¨ط·آ±ط·آ§ط؛إ’ ط·آ³ط·آ§ط·آ²ط¸â€ ط·آ¯ط¸â€، ط·آ±ط·آ¨ط·آ§ط·ع¾ ط¸ظ¾ط·آ¹ط·آ§ط¸â€‍ ط·آ§ط·آ³ط·ع¾."
        )
        return

    data = await admin_service.get_dashboard()

    platform_lines = [
        f"أ¢â‚¬آ¢ {escape(str(name))}: <b>{count}</b>"
        for name, count in data["platforms"]
    ]

    platforms_text = (
        "\n".join(platform_lines)
        if platform_lines
        else "ط¸â€،ط¸â€ ط¸ث†ط·آ² ط·آ¢ط¸â€¦ط·آ§ط·آ±ط؛إ’ ط·آ«ط·آ¨ط·ع¾ ط¸â€ ط·آ´ط·آ¯ط¸â€، ط·آ§ط·آ³ط·ع¾."
    )

    text = (
        "ظ‹ع؛â€کâ€ک <b>ط¸آ¾ط¸â€ ط¸â€‍ ط·آ§ط·آ®ط·ع¾ط·آµط·آ§ط·آµط؛إ’ ط·آ³ط·آ§ط·آ²ط¸â€ ط·آ¯ط¸â€،</b>\n"
        "أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾أ¢â€‌ظ¾\n\n"
        f"ظ‹ع؛â€کآ¥ ط¹آ©ط¸â€‍ ط¹آ©ط·آ§ط·آ±ط·آ¨ط·آ±ط·آ§ط¸â€ : <b>{data['total_users']:,}</b>\n"
        f"ظ‹ع؛ع؛آ¢ ط¹آ©ط·آ§ط·آ±ط·آ¨ط·آ±ط·آ§ط¸â€  ط¸ظ¾ط·آ¹ط·آ§ط¸â€‍ ط؛آ²ط؛آ´ ط·آ³ط·آ§ط·آ¹ط·ع¾: <b>{data['active_users']:,}</b>\n"
        f"ظ‹ع؛â€œآ¥ ط¹آ©ط¸â€‍ ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط¸â€،ط·آ§ط؛إ’ ط¸â€¦ط¸ث†ط¸ظ¾ط¸â€ڑ: <b>{data['total_downloads']:,}</b>\n"
        f"ظ‹ع؛â€œâ€¦ ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط¸â€،ط·آ§ط؛إ’ ط؛آ²ط؛آ´ ط·آ³ط·آ§ط·آ¹ط·ع¾: <b>{data['downloads_24h']:,}</b>\n"
        f"ظ‹ع؛â€œâ€  ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط¸â€،ط·آ§ط؛إ’ ط؛آ· ط·آ±ط¸ث†ط·آ²: <b>{data['downloads_7d']:,}</b>\n"
        f"ظ‹ع؛â€”â€œ ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط¸â€،ط·آ§ط؛إ’ ط؛آ³ط؛آ° ط·آ±ط¸ث†ط·آ²: <b>{data['downloads_30d']:,}</b>\n"
        f"أ¢ع‘طŒ ط·آ¯ط·آ§ط¸â€ ط¸â€‍ط¸ث†ط·آ¯ط¸â€،ط·آ§ط؛إ’ ط¸ظ¾ط·آ¹ط·آ§ط¸â€‍: <b>{data['active_downloads']}</b>\n\n"
        "<b>ط·آ¢ط¸â€¦ط·آ§ط·آ± ط¸آ¾ط¸â€‍ط·ع¾ط¸ظ¾ط·آ±ط¸â€¦أ¢â‚¬إ’ط¸â€،ط·آ§</b>\n"
        f"{platforms_text}\n\n"
        "ط·آ¨ط·آ±ط·آ§ط؛إ’ ط·آ¯ط·آ³ط·ع¾ط¸ث†ط·آ±ط·آ§ط·ع¾ ط¸â€¦ط·آ¯ط؛إ’ط·آ±ط؛إ’ط·ع¾ط؛إ’ ط¹آ©ط·آ§ط¸â€¦ط¸â€‍ط·إ’ ط·آ¯ط·آ³ط·ع¾ط¸ث†ط·آ± <code>/admin</code> ط·آ±ط·آ§ ط·آ§ط·آ±ط·آ³ط·آ§ط¸â€‍ ط¹آ©ط¸â€ ."
    )

    await message.answer(
        text,
        reply_markup=main_menu_keyboard(show_creator=True),
    )
