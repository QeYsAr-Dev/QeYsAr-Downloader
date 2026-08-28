from datetime import datetime, timezone

from config import settings
from database.database import connect


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def get_all_user_ids(
    include_banned: bool = False,
) -> list[int]:
    async with connect() as db:
        if include_banned:
            cursor = await db.execute(
                """
                SELECT user_id
                FROM users
                ORDER BY user_id
                """,
            )
        else:
            cursor = await db.execute(
                """
                SELECT user_id
                FROM users
                WHERE is_banned = 0
                ORDER BY user_id
                """,
            )

        rows = await cursor.fetchall()

    return [int(row[0]) for row in rows]


async def get_user_count() -> int:
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM users
            """
        )

        row = await cursor.fetchone()

    return int(row[0]) if row else 0


async def get_banned_user_count() -> int:
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM users
            WHERE is_banned = 1
            """
        )

        row = await cursor.fetchone()

    return int(row[0]) if row else 0


async def get_limited_user_count() -> int:
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM users
            WHERE is_limited = 1
            """
        )

        row = await cursor.fetchone()

    return int(row[0]) if row else 0


async def get_download_counts_by_status() -> list[tuple[str, int]]:
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT
                status,
                COUNT(*)
            FROM downloads
            GROUP BY status
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
