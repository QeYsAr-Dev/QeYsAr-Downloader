from datetime import datetime, timedelta, timezone

import aiosqlite

from config import settings


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def get_total_users() -> int:
    async with aiosqlite.connect(settings.database_file) as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM users
            """
        )

        row = await cursor.fetchone()

    return int(row[0]) if row else 0


async def get_active_users(
    hours: int = 24,
) -> int:
    threshold = (
        utc_now() - timedelta(hours=hours)
    ).isoformat()

    async with aiosqlite.connect(settings.database_file) as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM users
            WHERE last_activity >= ?
            """,
            (threshold,),
        )

        row = await cursor.fetchone()

    return int(row[0]) if row else 0


async def get_total_downloads() -> int:
    async with aiosqlite.connect(settings.database_file) as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM downloads
            WHERE status = 'completed'
            """
        )

        row = await cursor.fetchone()

    return int(row[0]) if row else 0


async def get_downloads_since(
    hours: int,
) -> int:
    threshold = (
        utc_now() - timedelta(hours=hours)
    ).isoformat()

    async with aiosqlite.connect(settings.database_file) as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM downloads
            WHERE status = 'completed'
              AND created_at >= ?
            """,
            (threshold,),
        )

        row = await cursor.fetchone()

    return int(row[0]) if row else 0


async def get_platform_statistics(
) -> list[tuple[str, int]]:
    async with aiosqlite.connect(settings.database_file) as db:
        cursor = await db.execute(
            """
            SELECT
                COALESCE(platform, 'unknown'),
                COUNT(*)
            FROM downloads
            WHERE status = 'completed'
            GROUP BY platform
            ORDER BY COUNT(*) DESC
            """
        )

        rows = await cursor.fetchall()

    return [
        (
            str(row[0]),
            int(row[1]),
        )
        for row in rows
    ]
