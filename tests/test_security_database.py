import pytest

from database.database import init_db


@pytest.mark.asyncio
async def test_security_columns_exist(tmp_path) -> None:
    database_file = tmp_path / "security.db"

    await init_db(database_file)

    import aiosqlite

    async with aiosqlite.connect(database_file) as db:
        cursor = await db.execute(
            "PRAGMA table_info(users)"
        )

        columns = {
            row[1]
            for row in await cursor.fetchall()
        }

    assert "is_banned" in columns
    assert "is_limited" in columns
