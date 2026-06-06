"""
Rate limiter — per-user request throttling with flood protection.
"""
import time
from collections import defaultdict

from config import Config
from utils.logger import setup_logger

log = setup_logger("sizu.ratelimiter")


class RateLimiter:
    """
    Sliding-window rate limiter.
    Tracks message counts per user over a rolling time window.
    """

    def __init__(
        self,
        max_messages: int = Config.RATE_LIMIT_MESSAGES,
        window_seconds: int = Config.RATE_LIMIT_WINDOW,
    ):
        self.max_messages = max_messages
        self.window = window_seconds
        # user_id -> list of timestamps
        self._timestamps: dict[int, list[float]] = defaultdict(list)
        # user_id -> True if currently warned
        self._warned: dict[int, bool] = defaultdict(bool)

    def is_allowed(self, user_id: int) -> bool:
        """Returns True if user is within rate limit."""
        now = time.monotonic()
        window_start = now - self.window
        # Purge old timestamps
        self._timestamps[user_id] = [
            t for t in self._timestamps[user_id] if t > window_start
        ]
        if len(self._timestamps[user_id]) < self.max_messages:
            self._timestamps[user_id].append(now)
            self._warned[user_id] = False
            return True
        return False

    def should_warn(self, user_id: int) -> bool:
        """Returns True if we should send a rate-limit warning (only once per throttle period)."""
        if not self._warned[user_id]:
            self._warned[user_id] = True
            return True
        return False

    def reset(self, user_id: int) -> None:
        """Manually reset a user's rate limit."""
        self._timestamps.pop(user_id, None)
        self._warned.pop(user_id, None)

    def get_wait_time(self, user_id: int) -> float:
        """Returns seconds until the user can send again."""
        now = time.monotonic()
        window_start = now - self.window
        valid = [t for t in self._timestamps[user_id] if t > window_start]
        if not valid:
            return 0.0
        oldest = min(valid)
        return max(0.0, (oldest + self.window) - now)


# Global singleton
rate_limiter = RateLimiter()
