"""
Auto reactions plugin — reacts to messages with relevant emojis.
Lightweight: fires for ~20% of messages in groups to stay non-spammy.
"""
import random

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    ReactionInvalid,
    ChatWriteForbidden,
    UserNotParticipant,
    FloodWait,
    BadRequest,
)

from utils.logger import setup_logger

log = setup_logger("sizu.reactions")

# Emoji pools by rough sentiment/keyword
POSITIVE_EMOJIS = ["❤️", "🔥", "👏", "💯", "✨", "🥰", "😍", "🎉"]
FUNNY_EMOJIS = ["😂", "💀", "🤣", "😭", "🫠"]
NEUTRAL_EMOJIS = ["👀", "🤔", "😮", "🫡", "👍"]
ALL_REACT = POSITIVE_EMOJIS + FUNNY_EMOJIS + NEUTRAL_EMOJIS

POSITIVE_WORDS = {"love", "wow", "amazing", "great", "awesome", "nice", "beautiful", "perfect", "yes"}
FUNNY_WORDS = {"lol", "lmao", "haha", "funny", "bruh", "💀", "dead", "crying"}


def pick_emoji(text: str) -> str:
    text_lower = (text or "").lower()
    if any(w in text_lower for w in POSITIVE_WORDS):
        return random.choice(POSITIVE_EMOJIS)
    if any(w in text_lower for w in FUNNY_WORDS):
        return random.choice(FUNNY_EMOJIS)
    return random.choice(ALL_REACT)


@Client.on_message(filters.group & ~filters.bot, group=2)
async def auto_react(client: Client, message: Message):
    """React to ~15% of group messages."""
    if not message.text or not message.from_user:
        return
    # Only react 15% of the time
    if random.random() > 0.15:
        return
    emoji = pick_emoji(message.text)
    try:
        await message.react(emoji)
    except (ReactionInvalid, ChatWriteForbidden, UserNotParticipant, BadRequest):
        pass  # Reactions not enabled or invalid in this chat
    except FloodWait:
        pass  # Skip this reaction rather than sleeping
    except Exception:
        pass
