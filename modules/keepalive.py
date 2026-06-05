"""
Keepalive HTTP server for Render.com free tier.
Render's free workers require an open HTTP port to stay alive.
This starts a minimal aiohttp server that responds to health checks.
"""
import asyncio
from aiohttp import web
from utils.logger import setup_logger

log = setup_logger("sizu.keepalive")


async def health_handler(request: web.Request) -> web.Response:
    return web.Response(text="✨ Sizu is alive and well!", status=200)


async def start_keepalive(port: int = 8080) -> None:
    """Start the keepalive web server on the given port."""
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_get("/ping", health_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    try:
        await site.start()
        log.info(f"Keepalive server running on http://0.0.0.0:{port}")
    except Exception as e:
        log.warning(f"Keepalive server failed to start: {e}")
