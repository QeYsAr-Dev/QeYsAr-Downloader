from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


CHANNEL_URL = "https://t.me/QeYsAr_Dev"


def force_join_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 عضویت در کانال سازنده",
                    url=CHANNEL_URL,
                    style="success",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ عضو شدم",
                    callback_data="force_join_check",
                    style="primary",
                )
            ],
        ]
    )


def creator_channel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="باز کردن کانال QeYsAr_Dev",
                    url=CHANNEL_URL,
                    style="success",
                )
            ]
        ]
    )
