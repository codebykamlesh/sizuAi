"""
Utility helpers for Sizu.
"""
import random
import re
import time
from datetime import datetime, timezone
from typing import Optional


# ── Human-like typing delay ───────────────────────────────────────────────────

async def get_human_delay(text: str) -> float:
    """
    Simulate realistic typing delay based on response length.
    Shorter texts feel snappier, longer ones have a small natural lag.
    """
    base = len(text) * 0.03          # 30ms per character base
    variance = random.uniform(0.2, 0.9)
    return min(max(base + variance, 1.0), 4.5)


# ── Elapsed time ──────────────────────────────────────────────────────────────

def time_ago(timestamp: float) -> str:
    """Human-readable time ago string."""
    diff = time.time() - timestamp
    if diff < 60:
        return f"{int(diff)}s ago"
    elif diff < 3600:
        return f"{int(diff / 60)}m ago"
    elif diff < 86400:
        return f"{int(diff / 3600)}h ago"
    else:
        return f"{int(diff / 86400)}d ago"


def parse_time(text: str) -> Optional[int]:
    """
    Parse human time strings into seconds.
    Supports: 30s, 5m, 2h, 1d
    """
    text = text.strip().lower()
    match = re.fullmatch(r"(\d+)\s*([smhd]?)", text)
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2) or "m"
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    return value * multipliers.get(unit, 60)


# ── Name utilities ────────────────────────────────────────────────────────────

def mention(user_id: int, name: str) -> str:
    """Create a Telegram mention string."""
    return f"[{name}](tg://user?id={user_id})"


def get_name(user) -> str:
    """Get the best display name from a Pyrogram User object."""
    if not user:
        return "Someone"
    full = (user.first_name or "").strip()
    if user.last_name:
        full += f" {user.last_name.strip()}"
    return full or user.username or "Someone"


# ── Menu formatting ───────────────────────────────────────────────────────────

def box(title: str, content: str, width: int = 30) -> str:
    """Draw a pretty box around menu content."""
    line = "─" * width
    return f"╭{line}╮\n│  **{title}**\n├{line}┤\n{content}\n╰{line}╯"


# ── Escape ────────────────────────────────────────────────────────────────────

def escape_md(text: str) -> str:
    """Escape MarkdownV2 special characters."""
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


# ── Random generators ─────────────────────────────────────────────────────────

TRUTHS = [
    "What's the most embarrassing thing you've done in public? 😬",
    "Have you ever ghosted someone? If yes, why?",
    "What's a habit you have that you'd be embarrassed if people found out?",
    "Who was your first real crush?",
    "What's the biggest lie you've ever told someone you care about?",
    "Have you ever read someone else's messages without permission?",
    "What's something you've done that you'd never admit to your parents?",
    "What's your most cringe memory from 3 years ago?",
    "Who do you think about before falling asleep most nights?",
    "What's one thing you pretend to like but actually hate?",
    "Have you ever faked being sick to avoid something?",
    "What's the pettiest reason you've ever unfollowed/blocked someone?",
    "If you could erase one thing you've said this week, what would it be?",
    "Do you secretly judge people by their music taste?",
    "What's a totally irrational fear you have?",
    "What's the most childish thing you still do?",
    "Have you ever lied about your age?",
    "What's the worst advice you've ever given someone?",
    "Have you ever had a crush on a friend's sibling?",
    "What's the most expensive thing you've ever stolen or broken?",
    "What's the weirdest food combination you secretly enjoy?",
    "Have you ever stalked an ex on social media? How recently?",
    "What's your biggest insecurity?",
    "Have you ever practiced kissing in front of a mirror or on a pillow?",
    "What's the longest you've gone without showering?",
    "If you had to marry someone in this chat, who would it be?",
    "What's the most embarrassing text you've sent to the wrong person?",
    "Have you ever cheated on a test or exam?",
    "What's a secret you've never told anyone in this group?",
    "What's the absolute worst date you've ever been on?",
    "If you could trade lives with someone in this chat, who would it be?",
    "Have you ever cried during a movie? Which one?",
    "What's the most useless talent you have?",
    "Have you ever snooped through someone's room or belongings?",
    "What's the biggest misconception people have about you?",
    "What's the most trouble you've ever gotten into at school or work?",
    "Have you ever regretted saying 'I love you' to someone?",
    "What is your guilty pleasure TV show or movie?",
    "Have you ever used a fake ID or lied to get into a venue?",
    "What's the most embarrassing nickname you've ever had?",
    "Have you ever pretended to not see someone in public to avoid talking to them?",
    "What's the weirdest dream you've ever had that you can remember?",
    "What's the one thing you would change about your appearance if you could?"
]

DARES = [
    "Send the most recent photo in your gallery right now, no questions asked.",
    "Do your best celebrity impression on voice note.",
    "Change your bio to something embarrassing for 10 minutes.",
    "Send a 'I miss you' text to the 5th person in your contacts.",
    "Do 15 pushups and screenshot proof.",
    "Text someone you haven't spoken to in 6 months.",
    "Write a 3-line poem about the person above you. Right now.",
    "Send a voice note of you singing the first song that comes to mind.",
    "Type with your nose for the next message.",
    "Say something genuinely nice to every person in this chat.",
    "Post a story saying 'I just lost a bet' with no context.",
    "Confess something you've never said out loud.",
    "Go offline for 5 minutes. Trust the process.",
    "Send a thumbs up to 10 people in your DMs. No explanation.",
    "Send a screenshot of your screen time usage for today.",
    "Change your Telegram profile picture to a funny meme for 30 minutes.",
    "Send a voice note of you laughing like a supervillain.",
    "Send a text to a friend saying 'I know what you did' and screenshot their reply.",
    "Send a message using only emojis for the next 10 minutes.",
    "Tell the group your most embarrassing dating story.",
    "Send a photo of the messiest corner of your room right now.",
    "Whisper a secret in a 5-second voice note.",
    "Send a screenshot of your most recent search history.",
    "Rank the people in this chat from most to least likely to survive a zombie apocalypse.",
    "Draw a quick sketch of a cat on paper, take a photo, and send it.",
    "Text a parent or sibling 'I got arrested' and immediately follow up with 'jk bet lost' after they reply.",
    "Send a voice note repeating 'I am the master of word chain' 5 times in a funny accent.",
    "For the next 5 minutes, agree with everything anyone says in this chat.",
    "Send the funniest meme you have saved on your phone.",
    "Confess which member of this chat you think has the best style.",
    "Record a 10-second voice note of you beatboxing.",
    "Type the next three messages in all uppercase.",
    "Draft an email to a random address from your contact list saying 'The eagle has landed' and send screenshot.",
    "Send a picture of your shoes right now.",
    "Give a dramatic reading of a random spam message in your spam folder.",
    "Text a coworker/classmate 'I think I love you' and then say 'oops wrong person' 2 seconds later.",
    "Recite a tongue twister in a voice note without making a mistake.",
    "Send a voice note of you making animal noises for 10 seconds.",
    "For the next 5 minutes, end every message with '...according to the prophecy.'",
    "Describe the person below you in this chat using only food adjectives.",
    "Send a voice note explaining why pineapple does or does not belong on pizza.",
    "Send a screenshot of your last music playlist."
]

TRIVIA_QS = [
    {"q": "What's the smallest country in the world?", "a": "Vatican City"},
    {"q": "How many bones does an adult human body have?", "a": "206"},
    {"q": "Which planet has the most moons?", "a": "Saturn"},
    {"q": "What language has the most words?", "a": "English"},
    {"q": "What year did the Titanic sink?", "a": "1912"},
    {"q": "How many sides does a dodecagon have?", "a": "12"},
    {"q": "What's the fastest land animal?", "a": "Cheetah"},
    {"q": "Who painted the Mona Lisa?", "a": "Leonardo da Vinci"},
    {"q": "What element is represented by the symbol Au?", "a": "Gold"},
    {"q": "How many continents are there on Earth?", "a": "7"},
    {"q": "What's the longest river in the world?", "a": "Nile"},
    {"q": "In what year did World War 2 end?", "a": "1945"},
    {"q": "What is the hardest natural substance on Earth?", "a": "Diamond"},
    {"q": "How many strings does a standard guitar have?", "a": "6"},
    {"q": "What's the capital of Japan?", "a": "Tokyo"},
]

QUOTES = [
    "the only person you should try to be better than is who you were yesterday.",
    "not everyone has to like you. not everyone has good taste.",
    "healing isn't linear. some days you slide backwards. that's still healing.",
    "you don't need closure from people who don't deserve your attention.",
    "growth is uncomfortable. so is staying the same. choose your uncomfortable.",
    "you're allowed to outgrow people, places, and even older versions of yourself.",
    "rest is productive. your body is not a machine.",
    "the right people will find their way to you. stop chasing the wrong ones.",
    "your feelings are valid even when nobody validates them.",
    "being misunderstood by people who don't know you is a compliment.",
]

ROAST_PROMPTS = [
    "Give a brutal but funny 1-2 sentence roast for someone named {name}. Make it clever, not mean-spirited. No asterisks, no formatting.",
    "Roast {name} in 1-2 sentences. Be witty and playful, like a friend who knows them too well. Keep it short.",
    "Write a short savage roast for {name}. Funny, punchy, nothing hateful. Just vibe-check energy.",
]

COMPLIMENT_PROMPTS = [
    "Give {name} a genuinely warm, specific compliment in 1-2 sentences. Sound real, not like a greeting card.",
    "Say something really sweet and real to {name}. 1-2 sentences max. No formatting.",
    "Compliment {name} in a way that actually feels personal and sincere. Short and punchy.",
]


def random_truth() -> str:
    return random.choice(TRUTHS)


def random_dare() -> str:
    return random.choice(DARES)


def random_trivia() -> dict:
    return random.choice(TRIVIA_QS)


def random_quote() -> str:
    return random.choice(QUOTES)


def random_roast_prompt(name: str) -> str:
    return random.choice(ROAST_PROMPTS).format(name=name)


def random_compliment_prompt(name: str) -> str:
    return random.choice(COMPLIMENT_PROMPTS).format(name=name)


async def get_target_user(client, message, default_to_sender: bool = True):
    """
    Centralized helper to resolve target user for commands.
    Resolution order:
    1. message.reply_to_message.from_user
    2. Mentioned user (via text_mention or mention entity)
    3. Username/ID argument in the message
    4. Sender (only if default_to_sender is True)
    """
    from pyrogram import enums

    # 1. Reply to another message
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    # 2. Check entities for mentions
    if message.entities:
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.TEXT_MENTION:
                return entity.user
            elif entity.type == enums.MessageEntityType.MENTION:
                mention_text = (message.text or message.caption or "")[entity.offset:entity.offset + entity.length]
                username = mention_text.lstrip("@")
                try:
                    return await client.get_users(username)
                except Exception:
                    pass

    # 3. Check command arguments
    if hasattr(message, "command") and len(message.command) > 1:
        arg = message.command[1].strip()
        if arg.startswith("@"):
            arg = arg[1:]

        # Try resolving as user ID or username
        try:
            if arg.isdigit() or (arg.startswith("-") and arg[1:].isdigit()):
                return await client.get_users(int(arg))
            else:
                return await client.get_users(arg)
        except Exception:
            pass

    # 4. Fallback to sender
    if default_to_sender:
        return message.from_user

    return None