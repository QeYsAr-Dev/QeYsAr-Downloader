import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from services.download_service import download_service
from services.queue_service import download_manager
from services.quality_selection import resolve_selection

router = Router()

logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("quality_select:"))
async def quality_select_callback(
    callback: CallbackQuery,
) -> None:
    if callback.message is None:
        await callback.answer(
            "پیام انتخاب کیفیت در دسترس نیست.",
            show_alert=True,
        )
        return

    try:
        quality = int(
            (callback.data or "").split(":", 1)[1]
        )
    except (ValueError, IndexError):
        await callback.answer(
            "کیفیت انتخاب‌شده معتبر نیست.",
            show_alert=True,
        )
        return

    resolved = resolve_selection(
        user_id=callback.from_user.id,
        message_id=callback.message.message_id,
        quality=quality,
    )

    if not resolved:
        await callback.answer(
            "این انتخاب منقضی شده یا متعلق به شما نیست.",
            show_alert=True,
        )
        return

    await callback.answer(
        f"کیفیت {quality}p انتخاب شد."
    )


@router.callback_query(F.data == "quality_cancel")
async def quality_cancel_callback(
    callback: CallbackQuery,
) -> None:
    if callback.message is None:
        await callback.answer()
        return

    resolved = resolve_selection(
        user_id=callback.from_user.id,
        message_id=callback.message.message_id,
        quality=None,
    )

    if not resolved:
        await callback.answer(
            "درخواست انتخاب کیفیت فعال نیست.",
            show_alert=True,
        )
        return

    await callback.answer(
        "انتخاب کیفیت لغو شد."
    )


@router.callback_query(F.data == "download_cancel")
async def cancel_download_callback(
    callback: CallbackQuery,
) -> None:
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id

    cancelled = download_manager.cancel_download(
        user_id,
        callback.message.chat.id,
        callback.message.message_id,
    )

    if cancelled:
        await callback.answer(
            "درخواست لغو دانلود ثبت شد."
        )
    else:
        await callback.answer(
            "دانلود فعالی برای لغو وجود ندارد.",
            show_alert=True,
        )


@router.message()
async def download_entry_handler(
    message: Message,
) -> None:
    if not message.text:
        return

    text = message.text.strip()

    if not text or text.startswith("/"):
        return

    try:
        await download_service.process(
            message=message,
            url=text,
        )

    except Exception:
        logger.exception(
            "Unhandled download handler exception. user_id=%s",
            message.from_user.id if message.from_user else None,
        )

        await message.answer(
            "❌ <b>خطای غیرمنتظره‌ای رخ داد.</b>\n\n"
            "لطفاً دوباره تلاش کنید."
        )