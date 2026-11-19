from __future__ import annotations

import asyncio
import html
import time

from dataclasses import dataclass


PENDING_TTL_SECONDS = 900

QUALITY_OPTIONS = (240, 360, 480, 720, 1080, 1440)


@dataclass(slots=True)
class PendingQualitySelection:
    user_id: int
    message_id: int
    qualities: tuple[int, ...]
    future: asyncio.Future[int | None]
    created_at: float


_pending: dict[int, PendingQualitySelection] = {}


def create_selection(
    user_id: int,
    message_id: int,
    qualities: list[int],
) -> asyncio.Future[int | None]:
    cleanup_expired()

    existing = _pending.get(user_id)

    if existing is not None:
        if not existing.future.done():
            raise RuntimeError(
                "User already has a pending quality selection."
            )

        _pending.pop(user_id, None)

    available = tuple(
        sorted(
            {
                quality
                for quality in qualities
                if quality in QUALITY_OPTIONS
            }
        )
    )

    if not available:
        raise ValueError("No supported quality is available.")

    future = asyncio.get_running_loop().create_future()

    _pending[user_id] = PendingQualitySelection(
        user_id=user_id,
        message_id=message_id,
        qualities=available,
        future=future,
        created_at=time.monotonic(),
    )

    return future


def resolve_selection(
    user_id: int,
    message_id: int,
    quality: int | None,
) -> bool:
    item = _pending.get(user_id)

    if item is None:
        return False

    if item.message_id != message_id:
        return False

    if item.future.done():
        return False

    if quality is not None and quality not in item.qualities:
        return False

    item.future.set_result(quality)
    return True


def clear_selection(user_id: int) -> None:
    _pending.pop(user_id, None)


def cleanup_expired() -> None:
    now = time.monotonic()

    expired = [
        user_id
        for user_id, item in _pending.items()
        if now - item.created_at > PENDING_TTL_SECONDS
    ]

    for user_id in expired:
        item = _pending.pop(user_id)

        if not item.future.done():
            item.future.set_result(None)


def build_preview_text(
    info: dict,
    platform: str,
    qualities: list[int],
) -> str:
    title = html.escape(
        str(info.get("title") or "محتوای بدون عنوان")[:180]
    )

    duration = info.get("duration")
    filesize = (
        info.get("filesize")
        or info.get("filesize_approx")
    )

    if isinstance(duration, (int, float)) and duration >= 0:
        total_seconds = int(duration)
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        duration_text = (
            f"{hours}:{minutes:02d}:{seconds:02d}"
            if hours
            else f"{minutes:02d}:{seconds:02d}"
        )
    else:
        duration_text = "نامشخص"

    if isinstance(filesize, (int, float)) and filesize > 0:
        size_text = f"{filesize / (1024 * 1024):.1f} MB"
    else:
        size_text = "نامشخص"

    available_text = (
        "، ".join(f"{quality}p" for quality in qualities)
        if qualities
        else "کیفیت قابل انتخاب ویدئو شناسایی نشد"
    )

    return (
        "🔎 <b>اطلاعات محتوای لینک</b>\n\n"
        f"عنوان: <b>{title}</b>\n"
        f"پلتفرم: <b>{html.escape(platform)}</b>\n"
        f"مدت‌زمان: <b>{duration_text}</b>\n"
        f"حجم تقریبی: <b>{size_text}</b>\n"
        f"کیفیت‌های موجود: <b>{available_text}</b>\n\n"
        "فرمت فایل به‌صورت خودکار توسط ربات انتخاب می‌شود."
    )