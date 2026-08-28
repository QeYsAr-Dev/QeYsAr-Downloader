import pytest

from services.rate_limit_service import RateLimitService


@pytest.mark.asyncio
async def test_rate_limit_allows_initial_requests() -> None:
    service = RateLimitService(
        requests_limit=3,
        window_seconds=10,
        block_seconds=5,
        spam_threshold=10,
        spam_window_seconds=30,
    )

    assert (
        await service.check(100)
    ).allowed is True

    assert (
        await service.check(100)
    ).allowed is True

    assert (
        await service.check(100)
    ).allowed is True


@pytest.mark.asyncio
async def test_rate_limit_blocks_excess_requests() -> None:
    service = RateLimitService(
        requests_limit=2,
        window_seconds=10,
        block_seconds=5,
        spam_threshold=10,
        spam_window_seconds=30,
    )

    assert (
        await service.check(100)
    ).allowed is True

    assert (
        await service.check(100)
    ).allowed is True

    result = await service.check(100)

    assert result.allowed is False
    assert result.reason == "rate_limit"
    assert result.retry_after > 0


@pytest.mark.asyncio
async def test_rate_limit_is_per_user() -> None:
    service = RateLimitService(
        requests_limit=1,
        window_seconds=10,
        block_seconds=5,
        spam_threshold=10,
        spam_window_seconds=30,
    )

    assert (
        await service.check(100)
    ).allowed is True

    assert (
        await service.check(100)
    ).allowed is False

    assert (
        await service.check(200)
    ).allowed is True


@pytest.mark.asyncio
async def test_reset_user_removes_block() -> None:
    service = RateLimitService(
        requests_limit=1,
        window_seconds=10,
        block_seconds=5,
        spam_threshold=10,
        spam_window_seconds=30,
    )

    await service.check(100)
    result = await service.check(100)

    assert result.allowed is False

    await service.reset_user(100)

    result = await service.check(100)

    assert result.allowed is True
