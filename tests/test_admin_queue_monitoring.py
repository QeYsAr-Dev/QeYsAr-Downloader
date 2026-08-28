import pytest

from services.queue_service import (
    UserDownloadManager,
)


@pytest.mark.asyncio
async def test_queue_monitoring() -> None:
    manager = UserDownloadManager()

    assert manager.active_user_count() == 0
    assert manager.active_user_ids() == []

    lock = manager.lock(123)

    await lock.acquire()

    try:
        assert manager.active_user_count() == 1
        assert manager.active_user_ids() == [
            123
        ]
    finally:
        lock.release()

    assert manager.active_user_count() == 0


@pytest.mark.asyncio
async def test_multiple_users_are_independent() -> None:
    manager = UserDownloadManager()

    lock_a = manager.lock(100)
    lock_b = manager.lock(200)

    await lock_a.acquire()
    await lock_b.acquire()

    try:
        assert manager.active_user_count() == 2
        assert set(
            manager.active_user_ids()
        ) == {
            100,
            200,
        }
    finally:
        lock_a.release()
        lock_b.release()
