import asyncio
import threading

from collections import defaultdict


class UserDownloadManager:
    """Manage per-user locks and active download cancellation."""

    def __init__(self) -> None:
        self._locks: defaultdict[int, asyncio.Lock] = defaultdict(
            asyncio.Lock
        )
        self._cancel_events: dict[int, tuple[threading.Event, int, int]] = {}

    def lock(self, user_id: int) -> asyncio.Lock:
        return self._locks[user_id]

    def is_busy(self, user_id: int) -> bool:
        return self._locks[user_id].locked()

    def register_cancel_event(
        self,
        user_id: int,
        event: threading.Event,
        chat_id: int,
        message_id: int,
    ) -> None:
        self._cancel_events[user_id] = (
            event,
            chat_id,
            message_id,
        )

    def cancel_download(
        self,
        user_id: int,
        chat_id: int,
        message_id: int,
    ) -> bool:
        entry = self._cancel_events.get(user_id)

        if entry is None:
            return False

        event, active_chat_id, active_message_id = entry

        if (
            active_chat_id != chat_id
            or active_message_id != message_id
        ):
            return False

        event.set()
        return True

    def clear_cancel_event(
        self,
        user_id: int,
        event: threading.Event,
    ) -> None:
        current = self._cancel_events.get(user_id)

        if current is not None and current[0] is event:
            self._cancel_events.pop(user_id, None)

    def active_user_count(self) -> int:
        return sum(
            1
            for lock in self._locks.values()
            if lock.locked()
        )

    def active_user_ids(self) -> list[int]:
        return sorted(
            user_id
            for user_id, lock in self._locks.items()
            if lock.locked()
        )


download_manager = UserDownloadManager()