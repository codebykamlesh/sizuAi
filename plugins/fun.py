"""
Fun plugin — roast, compliment, quote, ship, iq, hack, rizz.
All using curated local content pools for instant, reliable responses.
"""
import asyncio
import random

from pyrogram import Client, enums
from pyrogram.types import Message

from core.commands import register_command
from utils.helpers import (
    get_name, random_quote, random_compliment, random_roast,
    get_target_user, handle_bot_target,
)
from utils.logger import setup_logger

log = setup_logger("sizu.fun")

# ── Ship ──────────────────────────────────────────────────────────────────────

SHIP_COMMENTS = {
    (0, 20): ["not gonna happen 💀", "RIP this ship before it sailed", "the universe said no"],
    (21, 40): ["it's giving... situationship energy", "could be worse I guess", "there's hope but like... is there?"],
    (41, 60): ["not bad actually 👀", "mid ship but we don't judge", "the vibes are... okay"],
    (61, 80): ["okay this is cute ngl 🥺", "something's there fr", "lowkey rooting for them"],
    (81, 100): ["GET A ROOM 😭", "this is the one fr fr", "certified soulmates 💍✨"],
}

def ship_comment(percent: int) -> str:
    for (lo, hi), comments in SHIP_COMMENTS.items():
        if lo <= percent <= hi:
            return random.choice(comments)
    return "idk man"


@register_command(
    name="ship",
    description="Calculate love compatibility with a user you reply to or mention.",
    category="Fun",
    syntax="/ship <@user>",
    examples=["/ship @username"]
)
async def cmd_ship(client: Client, message: Message):
    user1 = message.from_user
    user2 = await get_target_user(client, message, default_to_sender=False)

    if not user1 or not user2:
        return await message.reply(
            "❌ No target user found.\n\n"
            "Usage:\nReply to a user's message:\n`/ship`\n\n"
            "Or use:\n`/ship @username`"
        )

    if await handle_bot_target(client, message, user2):
        return

    name1 = get_name(user1)
    name2 = get_name(user2)
    percent = random.randint(0, 100)
    comment = ship_comment(percent)

    bar_filled = "💗" * (percent // 10)
    bar_empty = "🤍" * (10 - percent // 10)
    bar = bar_filled + bar_empty

    await message.reply(
        f"🚢 **Ship Report**\n\n"
        f"**{name1}** × **{name2}**\n\n"
        f"{bar}\n"
        f"**{percent}%** — _{comment}_"
    )


# ── IQ Rating ────────────────────────────────────────────────────────────────

IQ_COMMENTS = {
    (0, 60): ["bro is cooked 💀", "there's no help for this one", "the lights are on but nobody's home"],
    (61, 85): ["average... painfully average", "not dumb but not exactly big brain either", "C student energy"],
    (86, 110): ["actually kinda smart ngl", "solid — not showing off but holding it down", "above average let's gooo"],
    (111, 140): ["okay you're scary smart 😳", "big brain activated fr", "certified galaxy brain"],
    (141, 200): ["what are you doing on Telegram, go cure cancer", "this can't be real", "genius level unlocked 🔓"],
}

def iq_comment(iq: int) -> str:
    for (lo, hi), comments in IQ_COMMENTS.items():
        if lo <= iq <= hi:
            return random.choice(comments)
    return "unmeasurable"


@register_command(
    name="iq",
    description="Measure a user's IQ (for fun).",
    category="Fun",
    syntax="/iq [@user]",
    examples=["/iq", "/iq @username"]
)
async def cmd_iq(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")

    if await handle_bot_target(client, message, target):
        return

    name = get_name(target)
    iq = random.randint(40, 200)
    comment = iq_comment(iq)
    bar = "▓" * min(20, iq // 10) + "░" * max(0, 20 - iq // 10)
    await message.reply(
        f"🧠 **IQ Test Result**\n\n"
        f"**{name}**\n"
        f"`{bar}`\n"
        f"**IQ: {iq}** — _{comment}_"
    )


# ── Hack ──────────────────────────────────────────────────────────────────────

HACK_LINES = [
    "Accessing mainframe... 🔓",
    "Bypassing firewall... ✅",
    "Decrypting password hash... 🔐",
    "Spoofing MAC address... 📡",
    "Injecting payload... 💉",
    "Escalating privileges... ⬆️",
    "Extracting data... 📦",
    "Covering tracks... 🧹",
]


@register_command(
    name="hack",
    description="Simulate a fun mock-hack on a user.",
    category="Fun",
    syntax="/hack [@user]",
    examples=["/hack @username"]
)
async def cmd_hack(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")

    if await handle_bot_target(client, message, target):
        return

    name = get_name(target)
    msg = await message.reply(f"💻 **Hacking {name}...**\n\n```\nInitializing...```")
    await asyncio.sleep(1)

    log_lines = []
    for line in random.sample(HACK_LINES, k=5):
        log_lines.append(line)
        try:
            await msg.edit(
                f"💻 **Hacking {name}...**\n\n```\n" + "\n".join(log_lines) + "```"
            )
        except Exception:
            pass
        await asyncio.sleep(0.8)

    results = [
        f"📧 Email: {name.lower().replace(' ', '.')}@gmail.com",
        f"🔑 Password: ************",
        f"📍 Location: Your imagination",
        f"💰 Bank balance: Less than expected",
        f"😭 Crush: Still doesn't know you exist",
    ]
    await msg.edit(
        f"Base64 Decrypted... ✅\n"
        f"✅ **{name} has been hacked!**\n\n"
        + "\n".join(results)
        + "\n\n_jk this is just a bot command lol_ 😂"
    )


# ── Roast (Local Pool — Instant, No AI) ──────────────────────────────────────

@register_command(
    name="roast",
    description="Roast a user or yourself.",
    category="Fun",
    syntax="/roast [@user]",
    examples=["/roast", "/roast @username"]
)
async def cmd_roast(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")

    if await handle_bot_target(client, message, target):
        return

    roast = random_roast(get_name(target))
    await message.reply(f"🔥 {roast}")


# ── Compliment (Local Pool — Instant, No AI) ─────────────────────────────────

@register_command(
    name="compliment",
    description="Send a sweet compliment to a user.",
    category="Fun",
    syntax="/compliment [@user]",
    examples=["/compliment", "/compliment @username"]
)
async def cmd_compliment(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")

    if await handle_bot_target(client, message, target):
        return

    comp = random_compliment(get_name(target))
    await message.reply(f"🌸 {comp}")


# ── Quote ──────────────────────────────────────────────────────────────────────

@register_command(
    name="quote",
    description="Get a random quote.",
    category="Fun",
    syntax="/quote",
    examples=["/quote"]
)
async def cmd_quote(client: Client, message: Message):
    q = random_quote()
    await message.reply(f"💭 _\"{q}\"_")


# ── Rizz ──────────────────────────────────────────────────────────────────────

RIZZ_SCORES = {
    (0, 20): "💔 Negative rizz. Return to start.",
    (21, 40): "😬 You tried. Nobody saw.",
    (41, 60): "😶 Mid rizz. Room for improvement.",
    (61, 80): "😏 Not bad. You've got something.",
    (81, 95): "🔥 High rizz detected. Dangerous.",
    (96, 100): "👑 GOD TIER RIZZ. Statistically impossible.",
}


@register_command(
    name="rizz",
    description="Check rizz rating of a user.",
    category="Fun",
    syntax="/rizz [@user]",
    examples=["/rizz", "/rizz @username"]
)
async def cmd_rizz(client: Client, message: Message):
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")

    if await handle_bot_target(client, message, target):
        return

    name = get_name(target)
    score = random.randint(0, 100)
    comment = "unknown rizz"
    for (lo, hi), msg_text in RIZZ_SCORES.items():
        if lo <= score <= hi:
            comment = msg_text
            break
    bar = "🌶️" * (score // 10) + "⬜" * (10 - score // 10)
    await message.reply(
        f"💘 **Rizz Check**\n\n"
        f"**{name}**\n"
        f"`{bar}`\n"
        f"**Score: {score}/100**\n"
        f"_{comment}_"
    )
