from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import settings
from database.repositories.preferences import (
    clear_default_quality,
    get_default_quality,
)

router = Router()


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="بازگشت به کیفیت خودکار",
                    callback_data="quality_default_auto",
                )
            ]
        ]
    )


def settings_text(
    default_quality: int | None,
) -> str:
    quality_text = (
        f"{default_quality}p"
        if default_quality is not None
        else "انتخاب خودکار بهترین کیفیت"
    )

    return (
        "⚙️ <b>تنظیمات اختصاصی شما</b>\n\n"
        f"کیفیت پیش‌فرض ویدئو: <b>{quality_text}</b>\n"
        "فرمت فایل: <b>انتخاب خودکار توسط ربات</b>\n\n"
        f"حداکثر حجم هر فایل: <b>{settings.max_file_size_mb} MB</b>\n"
        f"سهمیه روزانه: <b>{settings.daily_download_limit}</b> دانلود\n\n"
        "کیفیت انتخاب‌شده هنگام دانلود بعدی نیز برای شما ذخیره می‌شود."
    )


@router.message(Command("settings"))
async def settings_handler(message: Message) -> None:
    user = message.from_user

    if user is None:
        return

    default_quality = await get_default_quality(user.id)

    await message.answer(
        settings_text(default_quality),
        reply_markup=settings_keyboard(),
    )


@router.callback_query(F.data == "quality_default_auto")
async def reset_quality_callback(
    callback: CallbackQuery,
) -> None:
    user_id = callback.from_user.id

    await clear_default_quality(user_id)

    if callback.message is not None:
        await callback.message.edit_text(
            settings_text(None),
            reply_markup=None,
        )

    await callback.answer(
        "کیفیت پیش‌فرض به حالت خودکار برگشت."
    )