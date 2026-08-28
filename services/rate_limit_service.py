import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(slots=True)
class RateLimitResult:
    allowed: bool
    retry_after: float = 0.0
    reason: str = ""


class RateLimitService:
    """
    In-memory per-user rate limiter.

    Normal request limit:
        5 requests / 10 seconds

    Temporary block after the normal rate limit:
        30 seconds

    Spam protection:
        10 requests / 30 seconds

    This service is intentionally local to one application instance.
    Production multi-instance rate limiting can later be backed by
    a shared store such as Redis or Cloudflare KV.
    """

    def __init__(
        self,
        requests_limit: int,
        window_seconds: int,
        block_seconds: int,
        spam_threshold: int,
        spam_window_seconds: int,
    ) -> None:
        self.requests_limit = max(1, requests_limit)
        self.window_seconds = max(1, window_seconds)
        self.block_seconds = max(1, block_seconds)

        self.spam_threshold = max(
            self.requests_limit,
            spam_threshold,
        )
        self.spam_window_seconds = max(
            self.window_seconds,
            spam_window_seconds,
        )

        self._requests: defaultdict[int, deque[float]] = defaultdict(
            deque
        )
        self._spam_requests: defaultdict[int, deque[float]] = defaultdict(
            deque
        )
        self._blocked_until: dict[int, float] = {}
        self._lock = asyncio.Lock()

    async def check(
        self,
        user_id: int,
    ) -> RateLimitResult:
        now = time.monotonic()

        async with self._lock:
            blocked_until = self._blocked_until.get(user_id, 0.0)

            if blocked_until > now:
                return RateLimitResult(
                    allowed=False,
                    retry_after=blocked_until - now,
                    reason="blocked",
                )

            if blocked_until:
                self._blocked_until.pop(
                    user_id,
                    None,
                )

            request_queue = self._requests[user_id]
            spam_queue = self._spam_requests[user_id]

            self._cleanup(
                request_queue,
                now,
                self.window_seconds,
            )

            self._cleanup(
                spam_queue,
                now,
                self.spam_window_seconds,
            )

            if len(spam_queue) >= self.spam_threshold:
                block_until = now + self.block_seconds
                self._blocked_until[user_id] = block_until

                return RateLimitResult(
                    allowed=False,
                    retry_after=self.block_seconds,
                    reason="spam",
                )

            if len(request_queue) >= self.requests_limit:
                block_until = now + self.block_seconds
                self._blocked_until[user_id] = block_until

                return RateLimitResult(
                    allowed=False,
                    retry_after=self.block_seconds,
                    reason="rate_limit",
                )

            request_queue.append(now)
            spam_queue.append(now)

            return RateLimitResult(
                allowed=True,
            )

    async def reset_user(
        self,
        user_id: int,
    ) -> None:
        async with self._lock:
            self._requests.pop(user_id, None)
            self._spam_requests.pop(user_id, None)
            self._blocked_until.pop(user_id, None)

    async def retry_after(
        self,
        user_id: int,
    ) -> float:
        now = time.monotonic()

        async with self._lock:
            blocked_until = self._blocked_until.get(
                user_id,
                0.0,
            )

            return max(
                blocked_until - now,
                0.0,
            )

    @staticmethod
    def _cleanup(
        queue: deque[float],
        now: float,
        window_seconds: int,
    ) -> None:
        threshold = now - window_seconds

        while queue and queue[0] <= threshold:
            queue.popleft()


def create_rate_limit_service():
    from config import settings

    return RateLimitService(
        requests_limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
        block_seconds=settings.rate_limit_block_seconds,
        spam_threshold=settings.spam_threshold,
        spam_window_seconds=settings.spam_window_seconds,
    )


rate_limit_service = create_rate_limit_service()
