from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after_seconds: int
    reset_after_seconds: int


class InMemoryRateLimiter:
    """
    Sliding-window limiter.
    Notes:
    - Memory-only (resets on process restart)
    - Per-instance (not shared across multiple replicas)
    """

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str) -> RateLimitResult:
        now = time.time()

        with self._lock:
            queue = self._hits.setdefault(key, deque())

            while queue and (now - queue[0]) >= self.window_seconds:
                queue.popleft()

            if len(queue) >= self.max_requests:
                retry_after = max(1, int(self.window_seconds - (now - queue[0])))
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    retry_after_seconds=retry_after,
                    reset_after_seconds=retry_after,
                )

            queue.append(now)
            remaining = max(self.max_requests - len(queue), 0)
            reset_after = (
                max(1, int(self.window_seconds - (now - queue[0])))
                if queue
                else self.window_seconds
            )
            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                retry_after_seconds=0,
                reset_after_seconds=reset_after,
            )
