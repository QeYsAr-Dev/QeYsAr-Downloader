import aiosqlite
from pathlib import Path

from config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    downloads_today INTEGER NOT NULL DEFAULT 0,
    last_download_date TEXT,
    total_downloads INTEGER NOT NULL DEFAULT 0,
    last_activity TEXT NOT NULL,
    is_banned INTEGER NOT NULL DEFAULT 0,
    is_limited INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    platform TEXT,
    file_type TEXT,
    status TEXT NOT NULL,
    file_size INTEGER,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    error TEXT
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    event TEXT NOT NULL,
    user_id INTEGER,
    message TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_downloads_user_id
ON downloads(user_id);

CREATE INDEX IF NOT EXISTS idx_downloads_created_at
ON downloads(created_at);

CREATE INDEX IF NOT EXISTS idx_downloads_status
ON downloads(status);

CREATE INDEX IF NOT EXISTS idx_downloads_platform
ON downloads(platform);

CREATE INDEX IF NOT EXISTS idx_logs_created_at
ON logs(created_at);

CREATE INDEX IF NOT EXISTS idx_users_last_activity
ON users(last_activity);
"""


async def init_db(
    database_path: str | Path | None = None,
) -> None:
    database_file = (
        Path(database_path)
        if database_path
        else settings.database_file
    )

    database_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    async with aiosqlite.connect(
        database_file
    ) as db:
        await db.executescript(
            SCHEMA
        )

        columns_cursor = await db.execute(
            "PRAGMA table_info(users)"
        )

        columns = {
            row[1]
            for row in await columns_cursor.fetchall()
        }

        if "is_banned" not in columns:
            await db.execute(
                """
                ALTER TABLE users
                ADD COLUMN is_banned
                INTEGER NOT NULL DEFAULT 0
                """
            )

        if "is_limited" not in columns:
            await db.execute(
                """
                ALTER TABLE users
                ADD COLUMN is_limited
                INTEGER NOT NULL DEFAULT 0
                """
            )

        await db.commit()
