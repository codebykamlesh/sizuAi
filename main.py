"""
Sizu AI Bot — Entry Point
"""
import asyncio
import sys

# Ensure an event loop exists for pyrogram imports
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Synchronize local time with Google to prevent BadMsgNotification [16] (message ID too low)
import time
import urllib.request
import email.utils
try:
    req = urllib.request.Request('https://clients3.google.com/generate_204', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as response:
        date_str = response.headers.get('Date')
        if date_str:
            actual_time = email.utils.parsedate_to_datetime(date_str).timestamp()
            local_time = time.time()
            offset = actual_time - local_time
            if abs(offset) > 10:
                _orig_time = time.time
                time.time = lambda: _orig_time() + offset
                _orig_localtime = time.localtime
                time.localtime = lambda secs=None: _orig_localtime(secs if secs is not None else time.time())
                _orig_gmtime = time.gmtime
                time.gmtime = lambda secs=None: _orig_gmtime(secs if secs is not None else time.time())
except Exception:
    pass

import logging
from core.bot import SizuBot
from utils.logger import setup_logger

log = setup_logger("sizu.main")


async def main() -> None:
    bot = SizuBot()
    await bot.start()

    # Keep running until interrupted
    log.info("Sizu is running. Press Ctrl+C to stop.")
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Sizu stopped gracefully. 🌙")
    except Exception as e:
        log.critical(f"Fatal startup error: {e}", exc_info=True)
        sys.exit(1)