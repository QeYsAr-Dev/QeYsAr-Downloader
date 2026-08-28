from datetime import datetime, timezone

from database.database import connect


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def ensure_admin(user_id: int) -> None:
    async with connect() as db:
        await db.execute(
            """
            INSERT INTO admins (
                user_id,
                created_at
            )
            VALUES (?, ?)
            ON CONFLICT(user_id) DO NOTHING
            """,
            (
                user_id,
                utc_now(),
            ),
        )

        await db.commit()


async def is_admin(user_id: int) -> bool:
    async with connect() as db:
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
