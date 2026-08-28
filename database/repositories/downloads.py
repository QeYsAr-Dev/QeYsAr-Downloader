from datetime import datetime, timezone

import aiosqlite

from config import settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def create_download(
    user_id: int,
    url: str,
    platform: str | None,
    status: str,
) -> int:
    async with aiosqlite.connect(settings.database_file) as db:
        cursor = await db.execute(
            """
            INSERT INTO downloads (
                user_id,
                url,
                platform,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                url,
                platform,
                status,
                utc_now(),
            ),
        )

        await db.commit()

        return int(cursor.lastrowid)


async def update_download(
    download_id: int,
    status: str,
    file_type: str | None = None,
    file_size: int | None = None,
    error: str | None = None,
) -> None:
    completed_at = (
        utc_now()
        if status in {
            "completed",
            "failed",
            "rejected",
        }
        else None
    )

    async with aiosqlite.connect(settings.database_file) as db:
        await db.execute(
            """
            UPDATE downloads
            SET status = ?,
                file_type = COALESCE(?, file_type),
                file_size = COALESCE(?, file_size),
                error = ?,
                completed_at =
                    COALESCE(?, completed_at)
            WHERE id = ?
            """,
            (
                status,
                file_type,
                file_size,
                error,
                completed_at,
                download_id,
            ),
        )

        await db.commit()


async def get_user_history(
    user_id: int,
    limit: int = 10,
):
    async with aiosqlite.connect(settings.database_file) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM downloads
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                user_id,
                limit,
            ),
        )

        return await cursor.fetchall()


async def find_existing_url(
    user_id: int,
    url: str,
):
    async with aiosqlite.connect(settings.database_file) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT *
            FROM downloads
            WHERE user_id = ?
              AND url = ?
              AND status = 'completed'
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                user_id,
                url,
            ),
        )

        return await cursor.fetchone()
