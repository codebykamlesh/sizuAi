"""
Async scheduler — lightweight task scheduler for reminders.
Runs reminder checks every 30 seconds without heavy polling.
"""
import asyncio
import time
from typing import Callable, Optional

from utils.logger import setup_logger

log = setup_logger("sizu.scheduler")


class Scheduler:
    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._callbacks: list[Callable] = []

    def add_callback(self, cb: Callable) -> None:
        """Register an async callback to be called every tick."""
        self._callbacks.append(cb)

    async def _loop(self, interval: int) -> None:
        log.info(f"Scheduler started (interval={interval}s)")
        while self._running:
            await asyncio.sleep(interval)
            for cb in self._callbacks:
                try:
                    await cb()
                except Exception as e:
                    log.error(f"Scheduler callback error: {e}", exc_info=True)

    def start(self, interval: int = 30) -> None:
        self._running = True
        self._task = asyncio.create_task(self._loop(interval))

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


scheduler = Scheduler()
