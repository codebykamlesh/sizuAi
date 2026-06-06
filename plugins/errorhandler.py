"""
Global error handler plugin.
Catches unhandled exceptions across all handlers.
"""
import asyncio

from pyrogram import Client
from pyrogram.errors import FloodWait

from utils.logger import setup_logger

log = setup_logger("sizu.errorhandler")


async def global_error_handler(client: Client, update, exc: Exception) -> None:
    """Called by Pyrogram when an unhandled exception occurs in a handler."""
    if isinstance(exc, FloodWait):
        log.warning(f"FloodWait: sleeping {exc.value}s")
        await asyncio.sleep(exc.value)
        return

    if isinstance(exc, asyncio.CancelledError):
        return

    log.error(f"Unhandled exception in handler: {type(exc).__name__}: {exc}", exc_info=True)
