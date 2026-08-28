import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Update

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(
        self,
        bot: Bot,
        dispatcher: Dispatcher,
    ) -> None:
        self.bot = bot
        self.dispatcher = dispatcher

    async def process_update(
        self,
        update_data: dict,
    ) -> None:
        update = Update.model_validate(
            update_data
        )

        await self.dispatcher.feed_update(
            self.bot,
            update,
        )

        logger.info(
            "Telegram update processed: %s",
            update.update_id,
        )


telegram_service: TelegramService | None = None


def configure_telegram_service(
    bot: Bot,
    dispatcher: Dispatcher,
) -> TelegramService:
    global telegram_service

    telegram_service = TelegramService(
        bot=bot,
        dispatcher=dispatcher,
    )

    return telegram_service
