import pytest

from config import settings
from database.database import init_db
from database.repositories.admin import (
    get_all_user_ids,
    get_banned_user_count,
    get_limited_user_count,
    get_user_count,
)
from database.repositories.users import (
    set_user_banned,
    set_user_limited,
    upsert_user,
)


@pytest.mark.asyncio
async def test_admin_repository(
    tmp_path,
    monkeypatch,
) -> None:
    database_file = (
        tmp_path / "admin.db"
    )

    monkeypatch.setattr(
        settings,
        "database_path",
        str(database_file),
    )

    await init_db(database_file)

    await upsert_user(
        100,
        "user100",
        "User 100",
    )

    await upsert_user(
        200,
        "user200",
        "User 200",
    )

    assert await get_user_count() == 2
    assert await get_all_user_ids() == [
        100,
        200,
    ]

    await set_user_banned(
        200,
        True,
    )

    assert await get_banned_user_count() == 1

    active_ids = await get_all_user_ids()

    assert active_ids == [100]

    await set_user_limited(
        100,
        True,
    )

    assert await get_limited_user_count() == 1
