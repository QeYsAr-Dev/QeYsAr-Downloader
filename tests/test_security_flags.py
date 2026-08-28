import pytest

from config import settings
from database.database import init_db
from database.repositories.users import (
    is_user_banned,
    is_user_limited,
    set_user_banned,
    set_user_limited,
    upsert_user,
)


@pytest.mark.asyncio
async def test_ban_and_limit_flags(
    tmp_path,
    monkeypatch,
) -> None:
    database_file = tmp_path / "security_flags.db"

    monkeypatch.setattr(
        settings,
        "database_path",
        str(database_file),
    )

    await init_db(database_file)

    await upsert_user(
        user_id=777,
        username="security_test",
        first_name="Security",
    )

    assert await is_user_banned(777) is False
    assert await is_user_limited(777) is False

    await set_user_banned(
        777,
        True,
    )

    await set_user_limited(
        777,
        True,
    )

    assert await is_user_banned(777) is True
    assert await is_user_limited(777) is True

    await set_user_banned(
        777,
        False,
    )

    await set_user_limited(
        777,
        False,
    )

    assert await is_user_banned(777) is False
    assert await is_user_limited(777) is False
