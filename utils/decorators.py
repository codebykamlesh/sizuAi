"""
Custom Pyrogram filter decorators.
"""
from pyrogram import filters
from config import Config


def is_owner():
    """Filter: only the bot owner can use this command."""
    async def func(flt, client, message):
        return bool(message.from_user and message.from_user.id == Config.OWNER_ID)
    return filters.create(func)


def is_sudo():
    """Filter: owner + sudo users."""
    async def func(flt, client, message):
        if not message.from_user:
            return False
        return message.from_user.id in [Config.OWNER_ID] + Config.SUDO_USERS
    return filters.create(func)


def is_group_admin():
    """Filter: Telegram group admin or owner."""
    async def func(flt, client, message):
        if not message.from_user:
            return False
        if message.from_user.id == Config.OWNER_ID:
            return True
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        from pyrogram.enums import ChatMemberStatus
        return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
    return filters.create(func)


def not_bot():
    """Filter: exclude bot messages."""
    async def func(flt, client, message):
        return not (message.from_user and message.from_user.is_bot)
    return filters.create(func)