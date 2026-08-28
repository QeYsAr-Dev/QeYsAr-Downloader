from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📥 Download",
                    callback_data="download_help",
                ),
                InlineKeyboardButton(
                    text="📊 Stats",
                    callback_data="stats",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🕘 History",
                    callback_data="history",
                ),
                InlineKeyboardButton(
                    text="ℹ️ Help",
                    callback_data="help",
                ),
            ],
        ]
    )
