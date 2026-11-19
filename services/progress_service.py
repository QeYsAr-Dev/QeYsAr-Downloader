from __future__ import annotations

import asyncio
import html
import threading
import time

from pathlib import Path
from typing import Any, Callable

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)


ProgressCallback = Callable[[dict[str, Any]], None]


class ProgressService:
    """Thread-safe Telegram download progress reporting."""

    def __init__(
        self,
        message: Message,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        self.message = message
        self.reply_markup = reply_markup
        self._last_update = 0.0
        self._last_callback_dispatch = 0.0
        self._callback_lock = threading.Lock()
        self.current_text = ""

    @staticmethod
    def cancel_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="لغو دانلود",
                        callback_data="download_cancel",
                        style="danger",
                    )
                ]
            ]
        )

    def disable_cancel(self) -> None:
        self.reply_markup = None

    @staticmethod
    def format_size(value: int | float | None) -> str:
        if value is None or value < 0:
            return "نامشخص"

        size = float(value)

        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{size:.1f} GB"

    @staticmethod
    def format_duration(seconds: int | float | None) -> str:
        if seconds is None or seconds < 0:
            return "نامشخص"

        total = int(seconds)
        minutes, seconds_left = divmod(total, 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            return f"{hours}:{minutes:02d}:{seconds_left:02d}"

        return f"{minutes:02d}:{seconds_left:02d}"

    def make_callback(
        self,
        loop: asyncio.AbstractEventLoop,
    ) -> ProgressCallback:
        """Create a callback safe to invoke from yt-dlp worker threads."""

        def callback(data: dict[str, Any]) -> None:
            status = data.get("status")

            if status not in ("downloading", "finished"):
                return

            now = time.monotonic()

            with self._callback_lock:
                if (
                    status != "finished"
                    and now - self._last_callback_dispatch < 1.5
                ):
                    return

                self._last_callback_dispatch = now

            text = self.format_progress(data)

            try:
                loop.call_soon_threadsafe(
                    self._schedule_update,
                    text,
                )
            except RuntimeError:
                pass

        return callback

    def _schedule_update(self, text: str) -> None:
        asyncio.create_task(self.update(text))

    @classmethod
    def format_progress(
        cls,
        data: dict[str, Any],
    ) -> str:
        downloaded = int(data.get("downloaded_bytes") or 0)

        total = int(
            data.get("total_bytes")
            or data.get("total_bytes_estimate")
            or 0
        )

        speed = data.get("speed")
        eta = data.get("eta")

        if total > 0:
            percentage = min(
                100.0,
                downloaded / total * 100,
            )
            percentage_text = f"{percentage:.1f}%"
        else:
            percentage_text = "نامشخص"

        filename = (
            data.get("filename")
            or data.get("info_dict", {}).get("title")
            or ""
        )

        filename = html.escape(
            Path(str(filename)).name[:100]
        )

        speed_text = (
            f"{cls.format_size(speed)}/s"
            if isinstance(speed, (int, float))
            else "نامشخص"
        )

        total_text = (
            cls.format_size(total)
            if total
            else "نامشخص"
        )

        return (
            "⬇️ <b>در حال دانلود...</b>\n\n"
            f"پیشرفت: <b>{percentage_text}</b>\n"
            f"حجم دریافت‌شده: <b>{cls.format_size(downloaded)}</b>\n"
            f"حجم کل: <b>{total_text}</b>\n"
            f"سرعت: <b>{speed_text}</b>\n"
            f"زمان باقی‌مانده: <b>{cls.format_duration(eta)}</b>\n"
            + (
                f"\nفایل: <code>{filename}</code>"
                if filename
                else ""
            )
        )

    async def update(
        self,
        text: str,
        *,
        force: bool = False,
    ) -> None:
        now = time.monotonic()

        if (
            not force
            and now - self._last_update < 1.5
        ):
            return

        if text == self.current_text:
            return

        try:
            if self.message.photo:
                await self.message.edit_caption(
                    caption=text,
                    reply_markup=self.reply_markup,
                )
            else:
                await self.message.edit_text(
                    text,
                    reply_markup=self.reply_markup,
                )

            self.current_text = text
            self._last_update = now

        except TelegramBadRequest:
            pass