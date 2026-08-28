import time

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message


class ProgressService:
    """
    Updates one Telegram message during a download.

    Telegram messages are not edited more often than every
    1.5 seconds to avoid unnecessary API calls.
    """

    def __init__(
        self,
        message: Message,
    ) -> None:
        self.message = message
        self._last_update = 0.0
        self.current_text = ""

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
            await self.message.edit_text(text)
            self.current_text = text
            self._last_update = now
        except TelegramBadRequest:
            # Ignore Telegram errors caused by editing the
            # message with the same text or a race condition.
            pass
