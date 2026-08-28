from datetime import datetime, timezone

import aiosqlite

from config import settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def ensure_admin(user_id: int) -> None:
    async with aiosqlite.connect(settings.database_file) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO admins (
                user_id,
                created_at
            )
            VALUES (?, ?)
            """,
            (
                user_id,
                utc_now(),
            ),
        )

        await db.commit()


async def is_admin(user_id: int) -> bool:
    async with aiosqlite.connect(settings.database_file) as db:
        cursor = await db.execute(
            """
            SELECT 1
            FROM admins
            WHERE user_id = ?
            LIMIT 1
            """,
            (user_id,),
        )

        row = await cursor.fetchone()

    return row is not None
