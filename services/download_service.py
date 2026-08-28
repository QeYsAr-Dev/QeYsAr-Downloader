import logging
from pathlib import Path

from aiogram.types import FSInputFile, Message

from config import settings
from database.repositories.downloads import (
    create_download,
    find_existing_url,
    update_download,
)
from database.repositories.users import (
    get_today_download_count,
    increment_download_count,
    is_user_banned,
    is_user_limited,
    touch_user,
)
from downloaders.manager import DownloaderManager
from downloaders.models import DownloadResult, MediaType
from services.progress_service import ProgressService
from services.queue_service import download_manager
from utils.cleanup import cleanup_file
from utils.url import get_platform, is_valid_url

logger = logging.getLogger(__name__)


class DownloadService:
    def __init__(self) -> None:
        self.manager = DownloaderManager()

    async def process(
        self,
        message: Message,
        url: str,
    ) -> None:
        user = message.from_user

        if user is None:
            return

        user_id = user.id
        url = url.strip()

        await touch_user(user_id)

        # ----------------------------------------------------
        # Security: Ban check
        # ----------------------------------------------------
        if await is_user_banned(user_id):
            await message.answer(
                "🚫 <b>دسترسی شما به ربات مسدود شده است.</b>"
            )
            return

        # ----------------------------------------------------
        # Security: User manual limitation
        # ----------------------------------------------------
        if await is_user_limited(user_id):
            await message.answer(
                "⛔ <b>دسترسی دانلود شما توسط Admin محدود شده است.</b>"
            )
            return

        # ----------------------------------------------------
        # URL validation
        # ----------------------------------------------------
        if not is_valid_url(url):
            await message.answer(
                "❌ <b>لینک نامعتبر است.</b>\n\n"
                "لطفاً یک لینک معتبر ارسال کنید."
            )
            return

        platform = get_platform(url)

        if platform is None:
            await message.answer(
                "❌ <b>این پلتفرم پشتیبانی نمی‌شود.</b>\n\n"
                "فقط YouTube، Instagram، TikTok و Pinterest."
            )
            return

        # ----------------------------------------------------
        # Per-user concurrency
        # ----------------------------------------------------
        if download_manager.is_busy(user_id):
            await message.answer(
                "⏳ <b>دانلود قبلی شما هنوز تمام نشده است.</b>\n\n"
                "بعد از دریافت فایل قبلی، لینک بعدی را ارسال کنید."
            )
            return

        # ----------------------------------------------------
        # Daily limit
        # ----------------------------------------------------
        today_count = await get_today_download_count(user_id)

        if today_count >= settings.daily_download_limit:
            await message.answer(
                "🚫 <b>سقف دانلود روزانه شما تکمیل شده است.</b>\n\n"
                f"سقف روزانه: "
                f"<b>{settings.daily_download_limit}</b> دانلود"
            )
            return

        # ----------------------------------------------------
        # Duplicate URL
        # ----------------------------------------------------
        existing = await find_existing_url(
            user_id=user_id,
            url=url,
        )

        if existing is not None:
            await message.answer(
                "♻️ <b>این لینک قبلاً دانلود شده است.</b>\n\n"
                f"شماره دانلود: <b>#{existing['id']}</b>"
            )
            return

        # ----------------------------------------------------
        # Lock per user
        # ----------------------------------------------------
        async with download_manager.lock(user_id):
            # Double-check security state after obtaining lock.
            if await is_user_banned(user_id):
                await message.answer(
                    "🚫 <b>دسترسی شما به ربات مسدود شده است.</b>"
                )
                return

            if await is_user_limited(user_id):
                await message.answer(
                    "⛔ <b>دسترسی دانلود شما محدود شده است.</b>"
                )
                return

            # Double-check daily quota.
            today_count = await get_today_download_count(user_id)

            if today_count >= settings.daily_download_limit:
                await message.answer(
                    "🚫 <b>سقف دانلود روزانه شما تکمیل شده است.</b>"
                )
                return

            # Double-check duplicate.
            existing = await find_existing_url(
                user_id=user_id,
                url=url,
            )

            if existing is not None:
                await message.answer(
                    "♻️ <b>این لینک قبلاً دانلود شده است.</b>"
                )
                return

            download_id = await create_download(
                user_id=user_id,
                url=url,
                platform=platform,
                status="queued",
            )

            status_message = await message.answer(
                "📥 <b>درخواست شما ثبت شد.</b>\n\n"
                f"پلتفرم: <b>{platform}</b>\n"
                "وضعیت: <b>در حال آماده‌سازی...</b>"
            )

            progress = ProgressService(status_message)

            await update_download(
                download_id=download_id,
                status="downloading",
            )

            await progress.update(
                (
                    "⬇️ <b>در حال دانلود...</b>\n\n"
                    f"پلتفرم: <b>{platform}</b>"
                ),
                force=True,
            )

            result: DownloadResult = (
                await self.manager.download(url)
            )

            if not result.success:
                await update_download(
                    download_id=download_id,
                    status=result.status.value,
                    error=result.error,
                )

                await progress.update(
                    (
                        "❌ <b>دانلود انجام نشد.</b>\n\n"
                        f"{result.error or 'خطای نامشخص'}"
                    ),
                    force=True,
                )
                return

            if not result.files:
                await update_download(
                    download_id=download_id,
                    status="failed",
                    error="No downloadable files were produced.",
                )

                await progress.update(
                    "❌ <b>فایلی برای ارسال پیدا نشد.</b>",
                    force=True,
                )
                return

            sent_count = 0
            largest_file_size = 0
            first_media_type: str | None = None

            try:
                total_files = len(result.files)

                for index, downloaded_file in enumerate(
                    result.files,
                    start=1,
                ):
                    file_path = Path(
                        downloaded_file.path
                    )

                    if not file_path.exists():
                        continue

                    current_size = file_path.stat().st_size

                    if current_size <= 0:
                        continue

                    if current_size > settings.max_file_size_bytes:
                        logger.warning(
                            "File rejected because it exceeds limit. "
                            "user_id=%s size=%s",
                            user_id,
                            current_size,
                        )
                        continue

                    largest_file_size = max(
                        largest_file_size,
                        current_size,
                    )

                    if first_media_type is None:
                        first_media_type = (
                            downloaded_file.media_type.value
                        )

                    await progress.update(
                        (
                            "📤 <b>در حال ارسال...</b>\n\n"
                            f"فایل: <b>{index}/{total_files}</b>"
                        ),
                        force=True,
                    )

                    input_file = FSInputFile(
                        file_path,
                        filename=file_path.name,
                    )

                    caption = (
                        "✅ <b>QeYsAr Downloader</b>\n"
                        f"Platform: {platform}\n"
                        f"File: {index}/{total_files}"
                    )

                    if downloaded_file.media_type == MediaType.PHOTO:
                        await message.answer_photo(
                            photo=input_file,
                            caption=caption,
                        )

                    elif downloaded_file.media_type == MediaType.VIDEO:
                        await message.answer_video(
                            video=input_file,
                            caption=caption,
                        )

                    else:
                        await message.answer_document(
                            document=input_file,
                            caption=caption,
                        )

                    sent_count += 1

                if sent_count == 0:
                    await update_download(
                        download_id=download_id,
                        status="rejected",
                        error="No file was eligible for Telegram delivery.",
                    )

                    await progress.update(
                        (
                            "❌ <b>فایل قابل ارسال نیست.</b>\n\n"
                            "حداکثر حجم فایل 50 MB است."
                        ),
                        force=True,
                    )
                    return

                await update_download(
                    download_id=download_id,
                    status="completed",
                    file_type=first_media_type,
                    file_size=largest_file_size,
                )

                await increment_download_count(user_id)

                remaining = max(
                    settings.daily_download_limit
                    - await get_today_download_count(user_id),
                    0,
                )

                await progress.update(
                    (
                        "✅ <b>دانلود با موفقیت انجام شد.</b>\n\n"
                        f"فایل‌های ارسال‌شده: <b>{sent_count}</b>\n"
                        f"دانلود باقی‌مانده امروز: <b>{remaining}</b>"
                    ),
                    force=True,
                )

            except Exception as exc:
                logger.exception(
                    "Telegram upload failed for user=%s",
                    user_id,
                )

                await update_download(
                    download_id=download_id,
                    status="failed",
                    error=str(exc)[:700],
                )

                await progress.update(
                    "❌ <b>ارسال فایل با خطا مواجه شد.</b>",
                    force=True,
                )

            finally:
                for downloaded_file in result.files:
                    cleanup_file(
                        downloaded_file.path
                    )


download_service = DownloadService()
