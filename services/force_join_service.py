from typing import Any


CHANNEL_ID = "@QeYsAr_Dev"
CHANNEL_URL = "https://t.me/QeYsAr_Dev"


async def is_user_joined(bot: Any, user_id: int) -> bool:
    """
    Check whether a Telegram user is a member of the required channel.

    The bot must be an administrator of the channel for reliable
    membership checks through getChatMember.
    """
    member = await bot.get_chat_member(
        chat_id=CHANNEL_ID,
        user_id=user_id,
    )

    status = getattr(member, "status", None)
    status_value = getattr(status, "value", status)

    if status_value == "restricted":
        return bool(getattr(member, "is_member", False))

    return status_value in {
        "creator",
        "administrator",
        "member",
    }
