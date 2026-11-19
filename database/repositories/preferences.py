from datetime import datetime, timezone

from database.database import connect


QUALITY_OPTIONS = (240, 360, 480, 720, 1080, 1440)


async def _ensure_table(db) -> None:
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id BIGINT PRIMARY KEY,
            default_quality INTEGER,
            updated_at TEXT NOT NULL
        )
        """
    )


async def get_default_quality(user_id: int) -> int | None:
    async with connect() as db:
        await _ensure_table(db)

        cursor = await db.execute(
            """
            SELECT default_quality
            FROM user_preferences
            WHERE user_id = ?
            """,
            (user_id,),
        )

        row = await cursor.fetchone()

        if row is None:
            return None

        try:
            value = row["default_quality"]
        except (TypeError, KeyError, IndexError):
            value = row[0]

        if value is None:
            return None

        quality = int(value)
        return quality if quality in QUALITY_OPTIONS else None


async def set_default_quality(
    user_id: int,
    quality: int,
) -> None:
    if quality not in QUALITY_OPTIONS:
        raise ValueError("Unsupported video quality.")

    updated_at = datetime.now(timezone.utc).isoformat()

    async with connect() as db:
        await _ensure_table(db)

        await db.execute(
            """
            INSERT INTO user_preferences (
                user_id,
                default_quality,
                updated_at
            )
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                default_quality = excluded.default_quality,
                updated_at = excluded.updated_at
            """,
            (user_id, quality, updated_at),
        )

        await db.commit()


async def clear_default_quality(user_id: int) -> None:
    async with connect() as db:
        await _ensure_table(db)

        await db.execute(
            """
            DELETE FROM user_preferences
            WHERE user_id = ?
            """,
            (user_id,),
        )

        await db.commit()