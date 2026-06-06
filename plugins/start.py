"""
/start and /help plugin — premium UI with categorized command listing.
"""
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import get_name, get_target_user

from config import Config
from database.mongo import db

START_TIME = time.time()

from pyrogram.enums import ChatMemberStatus, ChatType
from core.commands import get_help_text, register_command

async def check_is_admin(client: Client, message: Message) -> bool:
    """Check if the sender is owner, sudo, or chat administrator."""
    if not message.from_user:
        return False
    user_id = message.from_user.id
    if user_id == Config.OWNER_ID or user_id in Config.SUDO_USERS:
        return True
    if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
        except Exception:
            return False
    return False

START_TEXT = """
Hey {name}! ✨

I'm **Sizu** — your chat companion who's always around.

Talk to me like a real person. I'll keep up 😌

Use /help to see everything I can do.
""".strip()


@register_command(
    name="start",
    description="Start the bot and get a warm welcome.",
    category="General",
    syntax="/start",
    examples=["/start"]
)
async def cmd_start(client: Client, message: Message):
    user = message.from_user
    if user:
        await db.upsert_user(
            user.id,
            user.first_name or "",
            user.username or "",
        )
    name = (user.first_name or "there") if user else "there"
    await message.reply(START_TEXT.format(name=name))


@register_command(
    name="help",
    description="Show all commands or details of a specific command.",
    category="General",
    syntax="/help [command]",
    examples=["/help", "/help note"]
)
async def cmd_help(client: Client, message: Message):
    args = message.command[1:]
    is_admin = await check_is_admin(client, message)
    if args:
        await message.reply(get_help_text(command_name=args[0], is_admin=is_admin))
    else:
        await message.reply(get_help_text(is_admin=is_admin))


@register_command(
    name="alive",
    description="Check bot status and uptime.",
    category="General",
    syntax="/alive",
    examples=["/alive"]
)
async def cmd_alive(client: Client, message: Message):
    from database.mongo import db as _db
    elapsed = int(time.time() - START_TIME)
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    uptime = ""
    if days:
        uptime += f"{days}d "
    if hours:
        uptime += f"{hours}h "
    uptime += f"{minutes}m {seconds}s"

    user_count = await _db.count_users()
    mem_count = await _db.count_memories()

    text = (
        f"💅 **Sizu is Alive!**\n\n"
        f"**Version:** `{Config.BOT_VERSION}`\n"
        f"**Uptime:** `{uptime}`\n"
        f"**Model:** `{Config.AI_MODEL}`\n"
        f"**Database:** `{'MongoDB ✅' if _db.is_connected else 'Memory ⚠️'}`\n"
        f"**Users:** `{user_count}`\n"
        f"**Memories:** `{mem_count}`\n\n"
        f"_vibing at {Config.AI_TEMPERATURE} temperature_ 🔥"
    )
    await message.reply(text)


@register_command(
    name="ping",
    description="Check bot latency.",
    category="General",
    syntax="/ping",
    examples=["/ping"]
)
async def cmd_ping(client: Client, message: Message):
    start_t = time.time()
    msg = await message.reply("pinging... 🏓")
    latency = round((time.time() - start_t) * 1000)
    bar = "█" * (latency // 20) + "░" * max(0, 5 - latency // 20)
    await msg.edit(
        f"🏓 **Pong!**\n"
        f"└ Latency: `{latency}ms` {bar}"
    )


@register_command(
    name="id",
    description="Get target user or chat ID.",
    category="General",
    syntax="/id [@user]",
    examples=["/id", "/id @username"]
)
async def cmd_id(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")
    
    name = get_name(target)
    await message.reply(
        f"👤 Name: {name}\n"
        f"🆔 ID: {target.id}"
    )


@register_command(
    name="info",
    description="Show profile information of a user.",
    category="General",
    syntax="/info [@user]",
    examples=["/info", "/info @username"],
    aliases=["whois", "profile"]
)
async def cmd_info(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply(
            "❌ No target user found.\n\n"
            "Usage:\nReply to a user's message:\n`/info`\n\n"
            "Or use:\n`/info @username`"
        )

    # Fetch the full user object to ensure all fields (dc_id, premium, phone) are populated
    try:
        target = await client.get_users(target.id)
    except Exception:
        pass

    name = get_name(target)
    username = f"@{target.username}" if target.username else "None"
    user_id = target.id
    mention_link = f"[Click Here](tg://user?id={target.id})"
    
    if target.is_bot:
        bot_status = "Bot 🤖"
    elif target.id == Config.OWNER_ID:
        bot_status = "Bot Owner 👑"
    elif await db.is_sizu_admin(target.id):
        bot_status = "Sizu Admin 🛡️"
    elif target.id in Config.SUDO_USERS:
        bot_status = "Sudo User 🔑"
    else:
        bot_status = "User 👤"

    premium_status = "Premium Status: Yes ✨" if target.is_premium else "Premium Status: No"
    dc_id = f"DC ID: {target.dc_id}" if target.dc_id else "DC ID: Not Available"
    phone_number = f"Phone Number: {target.phone_number}" if target.phone_number else "Phone Number: Not Available"

    text = (
        f"👤 **User Information**\n\n"
        f"• **Name:** {name}\n"
        f"• **Username:** {username}\n"
        f"• **User ID:** `{user_id}`\n"
        f"• **Mention Link:** {mention_link}\n"
        f"• **Bot Status:** {bot_status}\n"
        f"• **Premium:** {premium_status}\n"
        f"• **{dc_id}**\n"
        f"• **{phone_number}**"
    )
    await message.reply(text)
