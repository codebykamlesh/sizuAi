"""
Chat plugin — AI conversation handler for private and group chats.
Handles typing simulation, rate limiting, memory, and group mention detection.
"""
import asyncio
import random

from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import Message

from config import Config
from core.ai_engine import sizu_ai
from core.rate_limiter import rate_limiter
from database.mongo import db
from utils.helpers import get_human_delay, get_name
from utils.logger import setup_logger

log = setup_logger("sizu.chat")

# Commands to exclude from the catch-all chat handler
from core.commands import get_all_command_names
_EXCLUDED_CMDS = get_all_command_names()

RATE_LIMIT_MSGS = [
    "slow down lol, I'm one person 😭",
    "bro chill, I can't keep up 💀",
    "okay okay relax, I'm thinking 🫠",
    "you're way too fast rn, give me a sec",
    "one message at a time please 😩",
]


def _is_mentioned(message: Message, bot_username: str, bot_id: int) -> bool:
    """Check if bot is mentioned in a group message."""
    text = (message.text or message.caption or "").lower()

    # Direct @mention
    if f"@{bot_username.lower()}" in text:
        return True

    # Trigger words
    for word in Config.TRIGGER_WORDS:
        if word in text:
            return True

    # Reply to bot's message
    if (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == bot_id
    ):
        return True

    return False


# ── Private chat handler ──────────────────────────────────────────────────────

@Client.on_message(
    filters.private
    & filters.text
    & ~filters.bot
    & ~filters.command(_EXCLUDED_CMDS)
)
async def private_chat(client: Client, message: Message):
    user = message.from_user
    if not user or not message.text:
        return

    chat_id = message.chat.id
    user_id = user.id
    user_input = message.text.strip()

    # Register user
    await db.upsert_user(user_id, user.first_name or "", user.username or "")

    # Rate limiting
    if not rate_limiter.is_allowed(user_id):
        if rate_limiter.should_warn(user_id):
            wait = rate_limiter.get_wait_time(user_id)
            await message.reply(
                f"{random.choice(RATE_LIMIT_MSGS)} (wait ~{int(wait)}s)"
            )
        return

    # Typing indicator
    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
    except Exception:
        pass

    # Fetch history
    history = await db.get_chat_history(chat_id)

    # Generate AI response
    response = await sizu_ai.get_response(
        chat_id, history, user_input, user_name=user.first_name or "there"
    )

    # Save to memory
    await db.save_chat_history(chat_id, "user", user_input)
    await db.save_chat_history(chat_id, "assistant", response)

    # Humanlike delay
    delay = await get_human_delay(response)
    await asyncio.sleep(delay)

    try:
        await message.reply(response)
    except FloodWait as fw:
        log.warning(f"FloodWait {fw.value}s on private_chat")
        await asyncio.sleep(fw.value)
        await message.reply(response)
    except Exception as e:
        log.error(f"Error sending private reply: {e}")


# ── Group chat handler ────────────────────────────────────────────────────────

@Client.on_message(
    filters.group
    & filters.text
    & ~filters.bot
    & ~filters.command(_EXCLUDED_CMDS)
)
async def group_chat(client: Client, message: Message):
    user = message.from_user
    if not user or not message.text:
        return

    me = client.me
    if not _is_mentioned(message, me.username or "", me.id):
        return

    chat_id = message.chat.id
    user_id = user.id
    user_input = message.text.strip()

    # Rate limiting — shared per user across all chats
    if not rate_limiter.is_allowed(user_id):
        if rate_limiter.should_warn(user_id):
            await message.reply(random.choice(RATE_LIMIT_MSGS))
        return

    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
    except Exception:
        pass

    # Groups get lightweight memory (last 10 messages)
    history = await db.get_chat_history(chat_id)
    history = history[-10:]

    response = await sizu_ai.get_response(
        chat_id, history, user_input, user_name=user.first_name or "there"
    )

    await db.save_chat_history(chat_id, "user", user_input)
    await db.save_chat_history(chat_id, "assistant", response)

    delay = await get_human_delay(response)
    await asyncio.sleep(delay)

    try:
        await message.reply(response)
    except FloodWait as fw:
        log.warning(f"FloodWait {fw.value}s in group_chat")
        await asyncio.sleep(fw.value)
        await message.reply(response)
    except Exception as e:
        log.error(f"Error sending group reply: {e}")


from core.commands import register_command


# ── /reset and /forget — clear conversation memory ───────────────────────────

@register_command(
    name="reset",
    description="Clear AI conversation memory for this chat.",
    category="AI",
    syntax="/reset",
    examples=["/reset"],
    aliases=["forget"],
    permissions="Owner"
)
async def cmd_reset(client: Client, message: Message):
    await db.clear_chat_history(message.chat.id)
    await message.reply("memory wiped 🧹 fresh start, let's go")