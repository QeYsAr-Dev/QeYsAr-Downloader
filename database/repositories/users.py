from datetime import datetime, timezone

from database.database import connect


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _value(row, key: str, index: int):
    if row is None:
        return None

    if hasattr(row, "keys") and key in row.keys():
        return row[key]

    return row[index]


async def upsert_user(
    user_id: int,
    username: str | None,
    first_name: str | None,
) -> None:
    async with connect() as db:
        await db.execute(
            """
            INSERT INTO users (
                user_id,
                username,
                first_name,
                downloads_today,
                last_download_date,
                total_downloads,
                last_activity,
                is_banned,
                is_limited
            )
            VALUES (?, ?, ?, 0, NULL, 0, ?, 0, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_activity = excluded.last_activity
            """,
            (
                user_id,
                username,
                first_name,
                utc_now(),
            ),
        )

        await db.commit()


async def get_user(user_id: int):
    async with connect() as db:
        cursor = await db.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )

        return await cursor.fetchone()


async def get_today_download_count(
    user_id: int,
) -> int:
    user = await get_user(user_id)

    if user is None:
        return 0

    last_download_date = _value(
        user,
        "last_download_date",
        4,
    )

    if str(last_download_date) != today_utc():
        return 0

    return int(
        _value(
            user,
            "downloads_today",
            3,
        )
    )


async def increment_download_count(
    user_id: int,
) -> None:
    current_day = today_utc()

    async with connect() as db:
        await db.execute(
            """
            UPDATE users
            SET downloads_today =
                    CASE
                        WHEN last_download_date = ?
                        THEN downloads_today + 1
                        ELSE 1
                    END,
                last_download_date = ?,
                total_downloads = total_downloads + 1,
                last_activity = ?
            WHERE user_id = ?
            """,
            (
                current_day,
                current_day,
                utc_now(),
                user_id,
            ),
        )

        await db.commit()


async def touch_user(user_id: int) -> None:
    async with connect() as db:
        await db.execute(
            """
            UPDATE users
            SET last_activity = ?
            WHERE user_id = ?
            """,
            (
                utc_now(),
                user_id,
            ),
        )

        await db.commit()


async def is_user_banned(user_id: int) -> bool:
    user = await get_user(user_id)

    if user is None:
        return False

    return bool(
        _value(
            user,
            "is_banned",
            7,
        )
    )


async def is_user_limited(user_id: int) -> bool:
    user = await get_user(user_id)

    if user is None:
        return False

    return bool(
        _value(
            user,
            "is_limited",
            8,
        )
    )


async def set_user_banned(
    user_id: int,
    banned: bool,
) -> None:
    async with connect() as db:
        await db.execute(
            """
            UPDATE users
            SET is_banned = ?,
                last_activity = ?
            WHERE user_id = ?
            """,
            (
                banned,
                utc_now(),
                user_id,
            ),
        )

        await db.commit()


async def set_user_limited(
    user_id: int,
    limited: bool,
) -> None:
    async with connect() as db:
        await db.execute(
            """
            UPDATE users
            SET is_limited = ?,
                last_activity = ?
            WHERE user_id = ?
            """,
            (
                limited,
                utc_now(),
                user_id,
            ),
        )

        await db.commit()

