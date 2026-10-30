from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard(
    show_creator: bool = False,
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text="📥 شروع دانلود",
                callback_data="download_help",
                style="primary",
            ),
            InlineKeyboardButton(
                text="📊 آمار من",
                callback_data="stats",
                style="success",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🕘 تاریخچه",
                callback_data="history",
            ),
            InlineKeyboardButton(
                text="⚙️ تنظیمات",
                callback_data="settings",
            ),
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ راهنما",
                callback_data="help",
            ),
            InlineKeyboardButton(
                text="👤 درباره ربات",
                callback_data="about",
            ),
        ],
    ]

    if show_creator:
        rows.append([
            InlineKeyboardButton(
                text="👑 پنل سازنده",
                callback_data="creator_panel",
                style="primary",
            ),
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def panel_navigation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔵 پنل اصلی",
                    callback_data="back_to_main",
                    style="primary",
                ),
                InlineKeyboardButton(
                    text="✖ بستن",
                    callback_data="close_panel",
                    style="danger",
                ),
            ],
        ]
    )