import pytest

from config import settings
from database.database import init_db
from database.repositories.users import (
    get_user,
    is_user_banned,
    is_user_limited,
    set_user_banned,
    set_user_limited,
    upsert_user,
)


@pytest.mark.asyncio
async def test_user_security_flags(
    tmp_path,
    monkeypatch,
) -> None:
    database_file = tmp_path / "users.db"

    monkeypatch.setattr(
        settings,
        "database_path",
        str(database_file),
    )

    await init_db(database_file)

    await upsert_user(
        user_id=999,
        username="test",
        first_name="Test",
    )

    assert await is_user_banned(999) is False
    assert await is_user_limited(999) is False

    await set_user_banned(999, True)
    await set_user_limited(999, True)

    assert await is_user_banned(999) is True
    assert await is_user_limited(999) is True

    user = await get_user(999)

    assert user is not None
    assert user["is_banned"] == 1
    assert user["is_limited"] == 1
