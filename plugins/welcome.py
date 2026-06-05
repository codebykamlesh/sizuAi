"""
Welcome plugin — handles new member joins and departures.
Supports custom welcome messages per group.
"""
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus

from database.mongo import db
from utils.helpers import get_name, mention
from utils.decorators import is_group_admin
from utils.logger import setup_logger

log = setup_logger("sizu.welcome")

DEFAULT_WELCOME = (
    "Hey {mention}, welcome to **{chat}**! 👋\n"
    "Make yourself at home~ ✨"
)

DEFAULT_FAREWELL = (
    "**{name}** just left. Take care out there 👋"
)


@Client.on_chat_member_updated()
async def on_member_update(client: Client, update: ChatMemberUpdated):
    """Handle member join and leave events."""
    if not update.chat or not update.new_chat_member:
        return

    chat = update.chat
    new = update.new_chat_member
    old = update.old_chat_member

    user = new.user

    # Member joined
    if old and old.status == ChatMemberStatus.LEFT and new.status == ChatMemberStatus.MEMBER:
        custom = await db.get_welcome(chat.id)
        template = custom or DEFAULT_WELCOME
        name = get_name(user)
        m = mention(user.id, name)
        try:
            await client.send_message(
                chat.id,
                template.format(
                    name=name,
                    mention=m,
                    chat=chat.title or "here",
                    user_id=user.id,
                ),
            )
        except Exception as e:
            log.debug(f"Welcome send error: {e}")

    # Member left
    elif new.status == ChatMemberStatus.LEFT or new.status == ChatMemberStatus.BANNED:
        name = get_name(user)
        try:
            await client.send_message(
                chat.id,
                DEFAULT_FAREWELL.format(name=name, chat=chat.title or "here"),
            )
        except Exception as e:
            log.debug(f"Farewell send error: {e}")


from core.commands import register_command


@register_command(
    name="setwelcome",
    description="Set custom welcome message for the group.",
    category="Admin",
    syntax="/setwelcome <text>",
    examples=["/setwelcome Hello {mention}, welcome to the group!"],
    permissions="Admin",
    required_args=1,
    is_hidden=True
)
async def cmd_setwelcome(client: Client, message: Message):
    """
    Set custom welcome message. Admin only.
    Variables: {name}, {mention}, {chat}, {user_id}
    Usage: /setwelcome Hello {mention}, welcome!
    """
    args = message.command[1:]
    text = " ".join(args)
    await db.set_welcome(message.chat.id, text)
    await message.reply(
        f"✅ Welcome message updated!\n\n"
        f"Preview:\n{text}"
    )
