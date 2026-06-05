"""
Admin plugin — owner-only commands: stats, broadcast, plugin info.
"""
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from config import Config
from database.mongo import db
from core.commands import register_command, CommandValidationError
from utils.helpers import get_target_user, get_name
from utils.logger import setup_logger

log = setup_logger("sizu.admin")


@register_command(
    name="stats",
    description="Show bot statistics or user game statistics.",
    category="General",
    syntax="/stats [@user]",
    examples=["/stats", "/stats @username"],
    permissions="User"
)
async def cmd_stats(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")

    is_sudo = (message.from_user and (message.from_user.id == Config.OWNER_ID or message.from_user.id in Config.SUDO_USERS))
    has_target = (message.reply_to_message or (len(message.command) > 1))

    if is_sudo and not has_target:
        msg = await message.reply("Fetching stats... 🔄")
        try:
            user_count = await db.count_users()
            mem_count = await db.count_memories()
            db_status = "MongoDB ✅" if db.is_connected else "In-Memory ⚠️"
            await msg.edit(
                f"📊 **Sizu Stats**\n\n"
                f"👤 **Users:** `{user_count}`\n"
                f"🧠 **Memory chats:** `{mem_count}`\n"
                f"🗄️ **Database:** `{db_status}`\n"
                f"🤖 **Model:** `{Config.AI_MODEL}`\n"
                f"🌡️ **Temperature:** `{Config.AI_TEMPERATURE}`"
            )
        except Exception as e:
            await msg.edit(f"Error fetching stats: `{e}`")
    else:
        name = get_name(target)
        try:
            stats = await db.get_user_profile_stats(target.id)
            text = (
                f"📊 **Game Stats for {name}**\n\n"
                f"🏆 **Trivia Points:** `{stats.get('trivia_points', 0)}`\n"
                f"🔗 **Wordchain Points:** `{stats.get('wordchain_points', 0)}`\n"
                f"✂️ **RPS Wins:** `{stats.get('rps_wins', 0)}`\n"
                f"🔥 **Coin Streak:** `{stats.get('coin_streak', 0)}`\n"
                f"📈 **Max Coin Streak:** `{stats.get('max_coin_streak', 0)}`"
            )
            await message.reply(text)
        except Exception as e:
            await message.reply(f"❌ Error fetching stats: {e}")


@register_command(
    name="broadcast",
    description="Broadcast a message to all registered users.",
    category="Admin",
    syntax="/broadcast",
    examples=["/broadcast"],
    permissions="Owner"
)
async def cmd_broadcast(client: Client, message: Message):
    """Broadcast a message to all registered users."""
    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast it.")

    user_ids = await db.all_user_ids()
    total = len(user_ids)
    if not total:
        return await message.reply("No users to broadcast to yet!")

    msg = await message.reply(f"📡 Broadcasting to {total} users...")
    success, failed, blocked = 0, 0, 0

    for uid in user_ids:
        try:
            await message.reply_to_message.copy(uid)
            success += 1
        except (UserIsBlocked, InputUserDeactivated):
            blocked += 1
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 1)
            try:
                await message.reply_to_message.copy(uid)
                success += 1
            except Exception:
                failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # Avoid flood

    await msg.edit(
        f"✅ **Broadcast Complete**\n\n"
        f"✉️ Sent: `{success}`\n"
        f"🚫 Blocked/Deactivated: `{blocked}`\n"
        f"❌ Failed: `{failed}`"
    )


@register_command(
    name="cleardb",
    description="Clear all conversation memory for a specific chat ID.",
    category="Admin",
    syntax="/cleardb <chat_id>",
    examples=["/cleardb -100123456789"],
    permissions="Owner",
    required_args=1
)
async def cmd_cleardb(client: Client, message: Message):
    """Clear all memory for a specific chat ID."""
    chat_id_str = message.command[1]
    if not chat_id_str.lstrip("-").isdigit():
        raise CommandValidationError("Invalid chat ID. Must be a number.")
    chat_id = int(chat_id_str)
    await db.clear_chat_history(chat_id)
    await message.reply(f"✅ Cleared memory for chat `{chat_id}`")


@register_command(
    name="getid",
    description="Get the chat/user ID.",
    category="General",
    syntax="/getid",
    examples=["/getid"],
    permissions="Sudo",
    is_hidden=True
)
async def cmd_getid(client: Client, message: Message):
    """Get the chat/user ID."""
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        await message.reply(f"👤 `{u.id}` — **{u.first_name}**")
    else:
        await message.reply(
            f"💬 Chat: `{message.chat.id}`\n"
            f"👤 You: `{message.from_user.id if message.from_user else 'N/A'}`"
        )


@register_command(
    name="warn",
    description="Warn a user in the group.",
    category="Admin",
    syntax="/warn [@user]",
    examples=["/warn @username"],
    permissions="Admin"
)
async def cmd_warn(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=False)
    if not target:
        return await message.reply(
            "❌ No target user found.\n\n"
            "Usage:\nReply to a user's message:\n`/warn`\n\n"
            "Or use:\n`/warn @username`"
        )
    
    warn_count = await db.warn_user(target.id)
    target_name = get_name(target)
    
    if warn_count >= 3:
        try:
            await client.ban_chat_member(message.chat.id, target.id)
            await message.reply(f"🚫 **{target_name} has been banned** after receiving `{warn_count}/3` warnings.")
        except Exception as e:
            await message.reply(f"⚠️ **{target_name} reached {warn_count}/3 warnings**, but I failed to ban them: {e}")
    else:
        await message.reply(f"⚠️ **{target_name} has been warned ({warn_count}/3).**")


@register_command(
    name="mute",
    description="Mute a user in the chat.",
    category="Admin",
    syntax="/mute [@user]",
    examples=["/mute @username"],
    permissions="Admin"
)
async def cmd_mute(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=False)
    if not target:
        return await message.reply(
            "❌ No target user found.\n\n"
            "Usage:\nReply to a user's message:\n`/mute`\n\n"
            "Or use:\n`/mute @username`"
        )
    
    try:
        await client.restrict_chat_member(
            message.chat.id,
            target.id,
            ChatPermissions(can_send_messages=False)
        )
        await message.reply(f"🔇 **{get_name(target)} has been muted.**")
    except Exception as e:
        await message.reply(f"❌ Failed to mute user: {e}")


@register_command(
    name="unmute",
    description="Unmute a user in the chat.",
    category="Admin",
    syntax="/unmute [@user]",
    examples=["/unmute @username"],
    permissions="Admin"
)
async def cmd_unmute(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=False)
    if not target:
        return await message.reply(
            "❌ No target user found.\n\n"
            "Usage:\nReply to a user's message:\n`/unmute`\n\n"
            "Or use:\n`/unmute @username`"
        )
    
    try:
        await client.restrict_chat_member(
            message.chat.id,
            target.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await message.reply(f"🔊 **{get_name(target)} has been unmuted.**")
    except Exception as e:
        await message.reply(f"❌ Failed to unmute user: {e}")


@register_command(
    name="ban",
    description="Ban a user from the chat.",
    category="Admin",
    syntax="/ban [@user]",
    examples=["/ban @username"],
    permissions="Admin"
)
async def cmd_ban(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=False)
    if not target:
        return await message.reply(
            "❌ No target user found.\n\n"
            "Usage:\nReply to a user's message:\n`/ban`\n\n"
            "Or use:\n`/ban @username`"
        )
    
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await message.reply(f"🚫 **{get_name(target)} has been banned.**")
    except Exception as e:
        await message.reply(f"❌ Failed to ban user: {e}")


@register_command(
    name="unban",
    description="Unban a user in the chat.",
    category="Admin",
    syntax="/unban [@user]",
    examples=["/unban @username"],
    permissions="Admin"
)
async def cmd_unban(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=False)
    if not target:
        return await message.reply(
            "❌ No target user found.\n\n"
            "Usage:\nReply to a user's message:\n`/unban`\n\n"
            "Or use:\n`/unban @username`"
        )
    
    try:
        await client.unban_chat_member(message.chat.id, target.id)
        await message.reply(f"✅ **{get_name(target)} has been unbanned.**")
    except Exception as e:
        await message.reply(f"❌ Failed to unban user: {e}")


@register_command(
    name="kick",
    description="Kick a user from the chat.",
    category="Admin",
    syntax="/kick [@user]",
    examples=["/kick @username"],
    permissions="Admin"
)
async def cmd_kick(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=False)
    if not target:
        return await message.reply(
            "❌ No target user found.\n\n"
            "Usage:\nReply to a user's message:\n`/kick`\n\n"
            "Or use:\n`/kick @username`"
        )
    
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        await message.reply(f"🫵 **{get_name(target)} has been kicked.**")
    except Exception as e:
        await message.reply(f"❌ Failed to kick user: {e}")


@register_command(
    name="promote",
    description="Promote a user to Admin.",
    category="Admin",
    syntax="/promote [@user]",
    examples=["/promote @username"],
    permissions="Admin"
)
async def cmd_promote(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=False)
    if not target:
        return await message.reply(
            "❌ No target user found.\n\n"
            "Usage:\nReply to a user's message:\n`/promote`\n\n"
            "Or use:\n`/promote @username`"
        )
    
    try:
        await client.promote_chat_member(
            message.chat.id,
            target.id,
            can_manage_chat=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_promote_members=False,
            can_change_info=True
        )
        await message.reply(f"👑 **{get_name(target)} has been promoted to Admin.**")
    except Exception as e:
        await message.reply(f"❌ Failed to promote user: {e}")


@register_command(
    name="demote",
    description="Demote an Admin to Member.",
    category="Admin",
    syntax="/demote [@user]",
    examples=["/demote @username"],
    permissions="Admin"
)
async def cmd_demote(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=False)
    if not target:
        return await message.reply(
            "❌ No target user found.\n\n"
            "Usage:\nReply to a user's message:\n`/demote`\n\n"
            "Or use:\n`/demote @username`"
        )
    
    try:
        await client.promote_chat_member(
            message.chat.id,
            target.id,
            can_manage_chat=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_change_info=False
        )
        await message.reply(f"👤 **{get_name(target)} has been demoted to Member.**")
    except Exception as e:
        await message.reply(f"❌ Failed to demote user: {e}")