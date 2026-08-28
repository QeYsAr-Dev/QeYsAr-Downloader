from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings


def create_bot() -> Bot:
    if not settings.bot_token:
        raise RuntimeError(
            "BOT_TOKEN is not configured. "
            "Set BOT_TOKEN in the .env file."
        )

    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )


def create_dispatcher() -> Dispatcher:
    return Dispatcher()
