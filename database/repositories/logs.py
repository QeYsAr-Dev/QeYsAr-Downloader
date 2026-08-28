from datetime import datetime, timezone

from config import settings
from database.database import connect


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def add_log(
    level: str,
    event: str,
    user_id: int | None = None,
    message: str | None = None,
) -> None:
    async with connect() as db:
        await db.execute(
            """
            INSERT INTO logs (
                level,
                event,
                user_id,
                message,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                level,
                event,
                user_id,
                message,
                utc_now(),
            ),
        )

        await db.commit()


async def get_recent_logs(
    limit: int = 20,
) -> list[tuple]:
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT
                level,
                event,
                user_id,
                message,
                created_at
            FROM logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = await cursor.fetchall()

    return rows
