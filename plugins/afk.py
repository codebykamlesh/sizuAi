"""
AFK plugin — full AFK system with timestamp, reason, and group notifications.
"""
import time

from pyrogram import Client, filters
from pyrogram.types import Message

from database.mongo import db
from utils.helpers import get_name, time_ago, get_target_user
from utils.logger import setup_logger
from core.commands import register_command

log = setup_logger("sizu.afk")


@register_command(
    name="afk",
    description="Set yourself or a user as AFK.",
    category="Utilities",
    syntax="/afk [reason] or reply to a user",
    examples=["/afk studying", "/afk asleep"]
)
async def cmd_afk(client: Client, message: Message):
    """Set AFK status with optional reason for target user."""
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")

    reason_parts = message.command[1:]
    if reason_parts and (reason_parts[0].lstrip("@").lower() == str(target.username or "").lower() or reason_parts[0] == str(target.id)):
        reason_parts = reason_parts[1:]

    reason = " ".join(reason_parts) if reason_parts else "just chilling somewhere"

    await db.set_afk(target.id, reason)
    name = get_name(target)
    await message.reply(
        f"💤 **{name} is now AFK**\n"
        f"└ Reason: _{reason}_"
    )


@Client.on_message(filters.group & ~filters.bot, group=1)
async def afk_watcher(client: Client, message: Message):
    """
    Group-only AFK watcher:
    - Removes AFK when user sends a message
    - Notifies when someone pings an AFK user
    """
    if not message.from_user:
        return

    sender_id = message.from_user.id
    sender_name = get_name(message.from_user)

    # 1. If the sender is AFK, remove their status
    sender_afk = await db.check_afk(sender_id)
    if sender_afk:
        await db.remove_afk(sender_id)
        afk_since = sender_afk.get("afk_time") or sender_afk.get("time")
        duration = time_ago(afk_since) if afk_since else "a while"
        try:
            await message.reply(
                f"✨ Welcome back, **{sender_name}**!\n"
                f"└ You were AFK for {duration}"
            )
        except Exception:
            pass

    # 2. If someone replies to / mentions an AFK user, notify
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        if target.id == sender_id:
            return  # Don't notify yourself
        target_afk = await db.check_afk(target.id)
        if target_afk:
            target_name = get_name(target)
            reason = target_afk.get("afk_reason") or target_afk.get("reason", "no reason given")
            afk_since = target_afk.get("afk_time") or target_afk.get("time")
            duration = time_ago(afk_since) if afk_since else "some time"
            try:
                await message.reply(
                    f"💤 **{target_name}** is AFK right now\n"
                    f"├ Reason: _{reason}_\n"
                    f"└ Since: {duration}"
                )
            except Exception:
                pass
