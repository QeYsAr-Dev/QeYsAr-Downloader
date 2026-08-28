import pytest

from database.database import init_db


@pytest.mark.asyncio
async def test_database_initialization(tmp_path) -> None:
    database_file = tmp_path / "test.db"

    await init_db(database_file)

    assert database_file.exists()

    import aiosqlite

    async with aiosqlite.connect(database_file) as db:
        cursor = await db.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        )

        tables = {row[0] for row in await cursor.fetchall()}

    expected_tables = {
        "users",
        "downloads",
        "logs",
        "settings",
        "admins",
    }

    assert expected_tables.issubset(tables)
