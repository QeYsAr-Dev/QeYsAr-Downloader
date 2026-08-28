from aiogram import F, Router
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "download_help")
async def download_help_callback(
    callback: CallbackQuery,
) -> None:
    if callback.message:
        await callback.message.answer(
            "📥 لینک YouTube، Instagram، TikTok یا Pinterest "
            "را ارسال کنید."
        )

    await callback.answer()


@router.callback_query(F.data == "help")
async def help_callback(
    callback: CallbackQuery,
) -> None:
    if callback.message:
        await callback.message.answer(
            "ℹ️ لینک محتوا را مستقیماً برای ربات ارسال کنید."
        )

    await callback.answer()


@router.callback_query(F.data == "history")
async def history_callback(
    callback: CallbackQuery,
) -> None:
    if callback.message:
        await callback.message.answer(
            "🕘 برای مشاهده تاریخچه از /history استفاده کنید."
        )

    await callback.answer()


@router.callback_query(F.data == "stats")
async def stats_callback(
    callback: CallbackQuery,
) -> None:
    if callback.message:
        await callback.message.answer(
            "📊 برای مشاهده آمار از /stats استفاده کنید."
        )

    await callback.answer()
