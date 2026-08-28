import pytest

from config import settings
from database.database import init_db
from database.repositories.logs import (
    add_log,
    get_recent_logs,
)


@pytest.mark.asyncio
async def test_logs_repository(
    tmp_path,
    monkeypatch,
) -> None:
    database_file = (
        tmp_path / "logs.db"
    )

    monkeypatch.setattr(
        settings,
        "database_path",
        str(database_file),
    )

    await init_db(database_file)

    await add_log(
        level="INFO",
        event="test_event",
        user_id=123,
        message="hello",
    )

    rows = await get_recent_logs(
        limit=10
    )

    assert len(rows) == 1
    assert rows[0][0] == "INFO"
    assert rows[0][1] == "test_event"
    assert rows[0][2] == 123
    assert rows[0][3] == "hello"
