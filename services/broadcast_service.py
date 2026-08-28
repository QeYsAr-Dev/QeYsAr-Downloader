import asyncio
import logging
from dataclasses import dataclass

from aiogram import Bot

from database.repositories.logs import add_log
from services.admin_service import admin_service


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BroadcastResult:
    total: int
    sent: int
    failed: int


class BroadcastService:
    async def send(
        self,
        bot: Bot,
        text: str,
        admin_user_id: int,
    ) -> BroadcastResult:
        targets = (
            await admin_service.get_broadcast_targets()
        )

        sent = 0
        failed = 0

        for user_id in targets:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=text,
                )

                sent += 1

            except Exception as exc:
                failed += 1

                logger.warning(
                    "Broadcast failed for user=%s: %s",
                    user_id,
                    str(exc)[:300],
                )

            await asyncio.sleep(0.05)

        await add_log(
            level="INFO",
            event="admin_broadcast",
            user_id=admin_user_id,
            message=(
                f"total={len(targets)} "
                f"sent={sent} "
                f"failed={failed}"
            ),
        )

        return BroadcastResult(
            total=len(targets),
            sent=sent,
            failed=failed,
        )


broadcast_service = BroadcastService()
