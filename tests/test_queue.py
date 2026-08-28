import asyncio

import pytest

from services.queue_service import UserDownloadManager


@pytest.mark.asyncio
async def test_user_lock_blocks_same_user() -> None:
    manager = UserDownloadManager()

    lock = manager.lock(100)

    assert manager.is_busy(100) is False

    await lock.acquire()

    try:
        assert manager.is_busy(100) is True
    finally:
        lock.release()

    assert manager.is_busy(100) is False


@pytest.mark.asyncio
async def test_different_users_are_independent() -> None:
    manager = UserDownloadManager()

    lock_a = manager.lock(100)
    lock_b = manager.lock(200)

    await lock_a.acquire()

    try:
        assert manager.is_busy(100) is True
        assert manager.is_busy(200) is False

        await asyncio.wait_for(
            lock_b.acquire(),
            timeout=0.2,
        )

        lock_b.release()

    finally:
        lock_a.release()
