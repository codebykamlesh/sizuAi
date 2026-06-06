"""
Sizu AI Bot — Core Bot Class
"""
import asyncio
import time

from pyrogram import Client, enums
from pyrogram.errors import FloodWait

from config import Config
from database.mongo import db
from modules.keepalive import start_keepalive
from utils.logger import setup_logger

log = setup_logger("sizu.bot")

BANNER = """
╔═══════════════════════════════════════════╗
║         ✨  S I Z U  A I  B O T  ✨       ║
║                  v{version}                    ║
╠═══════════════════════════════════════════╣
║  Telegram AI · Built with ❤️               ║
╚═══════════════════════════════════════════╝
""".format(version=Config.BOT_VERSION)


class SizuBot(Client):
    def __init__(self):
        super().__init__(
            name="SizuAI",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="plugins"),
            parse_mode=enums.ParseMode.MARKDOWN,
            sleep_threshold=30,
            max_concurrent_transmissions=5,
        )
        self.start_time: float = time.time()
        self.owner_id: int = Config.OWNER_ID

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def start(self) -> None:
        print(BANNER)

        # Database
        log.info("Connecting to database...")
        await db.connect()
        log.info(f"Database: {'✅ MongoDB' if db.is_connected else '⚠️ In-memory fallback'}")

        # Pyrogram start
        log.info("Starting Pyrogram client...")
        await super().start()
        self.me = await self.get_me()

        log.info(f"Bot: @{self.me.username} ({self.me.id})")
        log.info(f"Owner: {Config.OWNER_ID}")
        
        # AI Provider validation & startup logs
        if Config.AI_PROVIDER == "gemini":
            if not Config.GEMINI_API_KEY:
                log.warning("⚠️ GEMINI_API_KEY is not set. Falling back to OpenRouter providers.")
            log.info("AI Provider: Gemini")
            log.info(f"Model: {Config.GEMINI_MODEL}")
        else:
            log.info("AI Provider: OpenRouter")
            
        fallbacks_count = sum(1 for m in [Config.FALLBACK_MODEL_1, Config.FALLBACK_MODEL_2, Config.FALLBACK_MODEL_3] if m)
        log.info(f"Fallbacks Loaded: {fallbacks_count}")
        
        log.info(f"Plugins loaded: {self._count_plugins()} handlers")

        # Register Bot Commands
        await self.set_bot_commands_from_registry()

        # Keepalive server for free hosting
        if Config.KEEPALIVE:
            asyncio.create_task(start_keepalive(Config.PORT))
            log.info(f"Keepalive server: port {Config.PORT}")

        # Notify owner
        try:
            await self.send_message(
                Config.OWNER_ID,
                f"✨ **Sizu is Online!**\n\n"
                f"**Version:** `{Config.BOT_VERSION}`\n"
                f"**AI Engine:** `Active`\n"
                f"**DB:** `{'MongoDB ✅' if db.is_connected else 'Memory ⚠️'}`\n\n"
                f"_All systems nominal. Let's go! 🚀_",
            )
        except Exception:
            pass

        log.info("✨ Sizu is live and ready!")

    async def stop(self, *args) -> None:
        log.info("Shutting down Sizu...")
        try:
            await self.send_message(Config.OWNER_ID, "🌙 Sizu is going offline. Cya later~")
        except Exception:
            pass
        await super().stop()
        log.info("Sizu stopped. 🌙")

    # ── Helpers ───────────────────────────────────────────────────────────

    def _count_plugins(self) -> int:
        """Count registered dispatcher handlers."""
        try:
            count = 0
            for group in self.dispatcher.groups.values():
                count += len(group)
            return count
        except Exception:
            return -1

    def uptime(self) -> str:
        """Returns formatted uptime string."""
        elapsed = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)

    async def set_bot_commands_from_registry(self) -> None:
        """Register bot commands using Telegram's set_bot_commands API."""
        from core.commands import get_pyrogram_commands
        from pyrogram.types import (
            BotCommandScopeDefault,
            BotCommandScopeAllChatAdministrators,
            BotCommandScopeChat
        )
        
        try:
            # 1. Default commands for all users
            default_cmds = get_pyrogram_commands(admin=False)
            await self.set_bot_commands(default_cmds, scope=BotCommandScopeDefault())
            log.info(f"Registered {len(default_cmds)} default bot commands.")
            
            # 2. Admin commands for group/supergroup admins
            admin_cmds = get_pyrogram_commands(admin=True)
            await self.set_bot_commands(admin_cmds, scope=BotCommandScopeAllChatAdministrators())
            log.info(f"Registered {len(admin_cmds)} admin bot commands for group administrators.")
            
            # 3. Admin commands for the owner in private chat
            if self.owner_id:
                try:
                    await self.set_bot_commands(admin_cmds, scope=BotCommandScopeChat(chat_id=self.owner_id))
                    log.info(f"Registered {len(admin_cmds)} admin bot commands for owner ({self.owner_id}).")
                except Exception as e:
                    log.warning(f"Could not register commands for owner chat: {e}")
        except Exception as e:
            log.error(f"Error setting bot commands: {e}", exc_info=True)

    def run(self) -> None:
        """Compatibility wrapper — not used since main.py uses asyncio.run()."""
        import asyncio
        asyncio.run(self._run_async())

    async def _run_async(self) -> None:
        await self.start()
        try:
            await asyncio.Event().wait()
        finally:
            await self.stop()