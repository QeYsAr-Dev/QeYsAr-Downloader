import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from services.admin_service import admin_service
from services.health_service import health_service
from services.resource_service import resource_service

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("health"))
async def health_handler(
    message: Message,
) -> None:
    user = message.from_user

    if user is None:
        return

    if not await admin_service.is_authorized(user.id):
        await message.answer(
            "⛔ <b>دسترسی غیرمجاز.</b>"
        )
        return

    health = health_service.check()

    resource = resource_service.snapshot(
        str(settings.download_directory)
    )

    disk_gb = (
        health.disk_free_bytes
        / (1024 ** 3)
    )

    download_mb = (
        resource.download_directory_size_bytes
        / (1024 ** 2)
    )

    status_text = (
        "🟢 HEALTHY"
        if health.healthy
        else "🔴 UNHEALTHY"
    )

    await message.answer(
        "🩺 <b>System Health</b>\n\n"
        f"Status: <b>{status_text}</b>\n"
        f"Database: <b>{'OK' if health.database_exists else 'ERROR'}</b>\n"
        f"Downloads: <b>{'OK' if health.download_directory_exists else 'ERROR'}</b>\n"
        f"Logs: <b>{'OK' if health.log_directory_exists else 'ERROR'}</b>\n"
        f"Free disk: <b>{disk_gb:.2f} GB</b>\n"
        f"Active downloads: <b>{health.active_downloads}</b>\n"
        f"Temporary files: <b>{download_mb:.2f} MB</b>\n"
        f"Process ID: <b>{health.process_id}</b>"
    )
