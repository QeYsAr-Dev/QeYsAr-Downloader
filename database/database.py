from __future__ import annotations

import re
from pathlib import Path
from typing import Any


import aiosqlite
import asyncpg

from config import settings


SQLITE_SCHEMA = """
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


POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    downloads_today INTEGER NOT NULL DEFAULT 0,
    last_download_date DATE,
    total_downloads INTEGER NOT NULL DEFAULT 0,
    last_activity TIMESTAMPTZ NOT NULL,
    is_banned BOOLEAN NOT NULL DEFAULT FALSE,
    is_limited BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS downloads (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    url TEXT NOT NULL,
    platform TEXT,
    file_type TEXT,
    status TEXT NOT NULL,
    file_size BIGINT,
    created_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    error TEXT
);

CREATE TABLE IF NOT EXISTS logs (
    id BIGSERIAL PRIMARY KEY,
    level TEXT NOT NULL,
    event TEXT NOT NULL,
    user_id BIGINT,
    message TEXT,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    user_id BIGINT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL
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


def database_url() -> str:
    return getattr(settings, "database_url", "").strip()


def use_postgres() -> bool:
    return bool(database_url())


def translate_query(query: str) -> str:
    index = 0

    def replace(_: re.Match[str]) -> str:
        nonlocal index
        index += 1
        return f"${index}"

    return re.sub(r"\?", replace, query)


class DatabaseCursor:
    def __init__(
        self,
        backend: str,
        cursor: Any = None,
        rows: list[Any] | None = None,
    ) -> None:
        self.backend = backend
        self.cursor = cursor
        self.rows = rows or []
        self._position = 0
        self.lastrowid: int | None = None

        if backend == "postgres" and self.rows:
            first = self.rows[0]
            if hasattr(first, "keys") and "id" in first.keys():
                value = first["id"]
                if value is not None:
                    self.lastrowid = int(value)

    async def fetchone(self) -> Any:
        if self.backend == "sqlite":
            return await self.cursor.fetchone()

        if self._position >= len(self.rows):
            return None

        row = self.rows[self._position]
        self._position += 1
        return row

    async def fetchall(self) -> list[Any]:
        if self.backend == "sqlite":
            return await self.cursor.fetchall()

        if self._position == 0:
            self._position = len(self.rows)
            return self.rows

        remaining = self.rows[self._position:]
        self._position = len(self.rows)
        return remaining


class DatabaseConnection:
    def __init__(
        self,
        backend: str,
        connection: Any,
    ) -> None:
        self.backend = backend
        self.connection = connection
        self.row_factory = None

    async def execute(
        self,
        query: str,
        params: Any = (),
    ) -> DatabaseCursor:
        if self.backend == "sqlite":
            cursor = await self.connection.execute(
                query,
                params,
            )
            return DatabaseCursor(
                "sqlite",
                cursor=cursor,
            )

        normalized = query.strip().lower()
        pg_query = translate_query(query)

        values = tuple(params)

        is_returning = (
            " returning " in f" {normalized} "
            or normalized.startswith("select ")
            or normalized.startswith("with ")
        )

        if is_returning:
            rows = await self.connection.fetch(
                pg_query,
                *values,
            )
            return DatabaseCursor(
                "postgres",
                rows=rows,
            )

        await self.connection.execute(
            pg_query,
            *values,
        )

        return DatabaseCursor(
            "postgres"
        )

    async def commit(self) -> None:
        if self.backend == "sqlite":
            await self.connection.commit()

    async def close(self) -> None:
        if self.backend == "sqlite":
            await self.connection.close()


class _ConnectionContext:
    def __init__(
        self,
        database_path: str | Path | None = None,
    ) -> None:
        self.database_path = database_path
        self.connection: DatabaseConnection | None = None

    async def __aenter__(self) -> DatabaseConnection:
        if self.database_path is not None or not use_postgres():
            path = (
                Path(self.database_path)
                if self.database_path is not None
                else settings.database_file
            )

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            sqlite_connection = await aiosqlite.connect(path)
            sqlite_connection.row_factory = aiosqlite.Row

            self.connection = DatabaseConnection(
                "sqlite",
                sqlite_connection,
            )

            return self.connection

        postgres_connection = await asyncpg.connect(
            database_url()
        )

        self.connection = DatabaseConnection(
            "postgres",
            postgres_connection,
        )

        return self.connection

    async def __aexit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        if self.connection is None:
            return

        if self.connection.backend == "postgres":
            await self.connection.connection.close()
        else:
            await self.connection.close()


def connect(
    database_path: str | Path | None = None,
) -> _ConnectionContext:
    return _ConnectionContext(
        database_path
    )


async def init_db(
    database_path: str | Path | None = None,
) -> None:
    if database_path is not None or not use_postgres():
        path = (
            Path(database_path)
            if database_path is not None
            else settings.database_file
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        async with aiosqlite.connect(path) as db:
            await db.executescript(
                SQLITE_SCHEMA
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

        return

    connection = await asyncpg.connect(
        database_url()
    )

    try:
        await connection.execute(
            POSTGRES_SCHEMA
        )
    finally:
        await connection.close()


__all__ = [
    "connect",
    "init_db",
    "database_url",
    "use_postgres",
]

