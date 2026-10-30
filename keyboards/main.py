from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


START_DOWNLOAD = "📥 شروع دانلود"
MY_STATS = "📊 آمار من"
HISTORY = "🕘 تاریخچه"
SETTINGS = "⚙️ تنظیمات"
HELP = "ℹ️ راهنما"
ABOUT = "👤 درباره"
CREATOR_CHANNEL = "📢 کانال سازنده"
CREATOR_PANEL = "👑 پنل سازنده"
CLOSE_PANEL = "✖️ بستن پنل"


def main_menu_keyboard(show_creator: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [
            KeyboardButton(text=START_DOWNLOAD, style="success"),
            KeyboardButton(text=MY_STATS, style="success"),
        ],
        [
            KeyboardButton(text=HISTORY, style="primary"),
            KeyboardButton(text=SETTINGS, style="primary"),
        ],
        [
            KeyboardButton(text=HELP, style="primary"),
            KeyboardButton(text=ABOUT, style="primary"),
        ],
    ]

    if show_creator:
        rows.append([
            KeyboardButton(text=CREATOR_PANEL, style="primary"),
        ])

    rows.extend([
        [
            KeyboardButton(text=CREATOR_CHANNEL, style="success"),
        ],
        [
            KeyboardButton(text=CLOSE_PANEL, style="danger"),
        ],
    ])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="یک بخش را از منوی پایین انتخاب کنید...",
    )


def panel_navigation_keyboard() -> ReplyKeyboardMarkup:
    """Backward-compatible helper for older imports."""
    return main_menu_keyboard()
