import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from services.force_join_service import CHANNEL_ID, is_user_joined


def run_async(coro):
    return asyncio.run(coro)


def make_bot(status, is_member=None):
    member_data = {"status": status}
    if is_member is not None:
        member_data["is_member"] = is_member

    bot = SimpleNamespace(
        get_chat_member=AsyncMock(
            return_value=SimpleNamespace(**member_data)
        )
    )
    return bot


def test_regular_member_is_accepted():
    bot = make_bot("member")

    assert run_async(is_user_joined(bot, 123)) is True

    bot.get_chat_member.assert_awaited_once_with(
        chat_id=CHANNEL_ID,
        user_id=123,
    )


def test_administrator_is_accepted():
    bot = make_bot("administrator")

    assert run_async(is_user_joined(bot, 123)) is True


def test_channel_creator_is_accepted():
    bot = make_bot("creator")

    assert run_async(is_user_joined(bot, 123)) is True


def test_restricted_user_is_accepted_only_when_member():
    accepted_bot = make_bot("restricted", is_member=True)
    rejected_bot = make_bot("restricted", is_member=False)

    assert run_async(is_user_joined(accepted_bot, 123)) is True
    assert run_async(is_user_joined(rejected_bot, 123)) is False


def test_left_user_is_rejected():
    bot = make_bot("left")

    assert run_async(is_user_joined(bot, 123)) is False


def test_kicked_user_is_rejected():
    bot = make_bot("kicked")

    assert run_async(is_user_joined(bot, 123)) is False
