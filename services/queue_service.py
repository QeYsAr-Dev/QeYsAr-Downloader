import asyncio
from collections import defaultdict


class UserDownloadManager:
    """
    One active download per user.

    Different users have independent locks and may download
    concurrently.
    """

    def __init__(self) -> None:
        self._locks: defaultdict[int, asyncio.Lock] = defaultdict(
            asyncio.Lock
        )

    def lock(
        self,
        user_id: int,
    ) -> asyncio.Lock:
        return self._locks[user_id]

    def is_busy(
        self,
        user_id: int,
    ) -> bool:
        return self._locks[user_id].locked()

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
