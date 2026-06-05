"""
Reminders plugin — set, list, and fire async reminders.
Uses the scheduler for periodic due-reminder checks.
"""
import asyncio
import time
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config
from core.scheduler import scheduler
from database.mongo import db
from utils.helpers import parse_time, time_ago, get_name
from utils.logger import setup_logger

log = setup_logger("sizu.reminders")

# Will be set to the client instance when the reminder checker fires
_client_ref: Optional[Client] = None


async def fire_due_reminders() -> None:
    """Called by scheduler every 30s. Sends due reminders."""
    global _client_ref
    if not _client_ref:
        return
    try:
        due = await db.get_due_reminders()
        for reminder in due:
            chat_id = reminder.get("chat_id")
            user_id = reminder.get("user_id")
            text = reminder.get("text", "Something!")
            try:
                await _client_ref.send_message(
                    chat_id,
                    f"⏰ **Reminder for** [{user_id}](tg://user?id={user_id})!\n\n"
                    f"_{text}_",
                )
            except Exception as e:
                log.warning(f"Failed to send reminder to {chat_id}: {e}")
    except Exception as e:
        log.error(f"Reminder check error: {e}", exc_info=True)


from core.commands import register_command, CommandValidationError


@register_command(
    name="remind",
    description="Set a reminder with a time delay.",
    category="Utilities",
    syntax="/remind <time> <message>",
    examples=["/remind 10m buy milk", "/remind 2h call mom"],
    required_args=2
)
async def cmd_remind(client: Client, message: Message):
    """
    Set a reminder.
    Usage: /remind <time> <text>
    Time formats: 30s, 5m, 2h, 1d
    Example: /remind 10m Call mom
    """
    global _client_ref
    _client_ref = client

    # Start the scheduler if not already started
    if not scheduler._running:
        scheduler.add_callback(fire_due_reminders)
        scheduler.start(30)

    args = message.command[1:]
    time_str = args[0]
    reminder_text = " ".join(args[1:])

    seconds = parse_time(time_str)
    if not seconds:
        raise CommandValidationError(
            f"Invalid duration format `{time_str}`. Use formats like: `30s`, `5m`, `2h`, `1d`."
        )

    if seconds > 86400 * 7:  # Max 7 days
        raise CommandValidationError("Max reminder time is 7 days!")

    due_at = time.time() + seconds
    user = message.from_user
    user_id = user.id if user else 0

    await db.add_reminder(user_id, message.chat.id, reminder_text, due_at)

    # Human-readable duration
    if seconds < 60:
        readable = f"{seconds}s"
    elif seconds < 3600:
        readable = f"{seconds // 60}m"
    elif seconds < 86400:
        readable = f"{seconds // 3600}h {(seconds % 3600) // 60}m"
    else:
        readable = f"{seconds // 86400}d"

    await message.reply(
        f"⏰ **Reminder set!**\n\n"
        f"└ I'll remind you in **{readable}**\n"
        f"└ About: _{reminder_text}_"
    )


@register_command(
    name="reminders",
    description="List all your active upcoming reminders.",
    category="Utilities",
    syntax="/reminders",
    examples=["/reminders"]
)
async def cmd_list_reminders(client: Client, message: Message):
    """List your upcoming reminders."""
    user = message.from_user
    if not user:
        return

    reminders = await db.list_reminders(user.id)
    if not reminders:
        return await message.reply("You have no active reminders! Set one with `/remind <time> <text>`")

    lines = []
    for i, r in enumerate(reminders[:10], 1):
        remaining = max(0, r["due_at"] - time.time())
        if remaining < 60:
            when = f"{int(remaining)}s"
        elif remaining < 3600:
            when = f"{int(remaining // 60)}m"
        else:
            when = f"{int(remaining // 3600)}h"
        lines.append(f"{i}. _{r['text']}_ (in **{when}**)")

    await message.reply(
        f"⏰ **Your Reminders**\n\n" + "\n".join(lines)
    )
