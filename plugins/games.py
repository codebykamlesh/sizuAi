"""
Games plugin — Stateful, Persistent, Multiplayer Puzzles, Guess, RPS, Coin Flip, Truth & Dare.
"""
import asyncio
import random
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from core.commands import register_command, CommandValidationError
from database.mongo import db
from utils.helpers import (
    get_name, mention, random_puzzles,
    TRUTHS, DARES, get_target_user, handle_bot_target
)
from utils.logger import setup_logger

log = setup_logger("sizu.games")


# ── Expiration / Timeout Tasks ────────────────────────────────────────────────

async def puzzles_timeout(client: Client, chat_id: int, start_time: float, answer_options: list[str]):
    """Wait 30s and expire puzzles question if still active."""
    await asyncio.sleep(30)
    state = await db.get_game_state(chat_id, "puzzles")
    if state and state.get("active") and state.get("start_time") == start_time:
        state["active"] = False
        await db.save_game_state(chat_id, "puzzles", state)
        display_ans = answer_options[0].title() if answer_options else "Unknown"
        try:
            await client.send_message(
                chat_id,
                f"⏰ **Time's up!** No one got it right.\n"
                f"└ The correct answer was: ||{display_ans}||"
            )
        except Exception as e:
            log.debug(f"Error sending puzzles timeout message: {e}")


# ── Truth & Dare ──────────────────────────────────────────────────────────────

@register_command(
    name="truth",
    description="Play truth or dare (truth question). Avoids repeats.",
    category="Games",
    syntax="/truth [@user]",
    examples=["/truth", "/truth @username"]
)
async def cmd_truth(client: Client, message: Message):
    chat_id = message.chat.id
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")
        
    if await handle_bot_target(client, message, target):
        return

    name = get_name(target)
    
    # Fetch truth_dare state to track recently asked truths
    state = await db.get_game_state(chat_id, "truth_dare") or {"recent_truths": [], "recent_dares": []}
    recent_truths = state.get("recent_truths", [])
    
    available = [t for t in TRUTHS if t not in recent_truths]
    if not available:
        available = TRUTHS
        recent_truths = []
        
    question = random.choice(available)
    recent_truths.append(question)
    if len(recent_truths) > 30:
        recent_truths.pop(0)
        
    state["recent_truths"] = recent_truths
    await db.save_game_state(chat_id, "truth_dare", state)
    
    await message.reply(
        f"🎯 **Truth for {name}:**\n\n_{question}_\n\n"
        f"└ _no backing out_ 😈"
    )


@register_command(
    name="dare",
    description="Play truth or dare (dare challenge). Avoids repeats.",
    category="Games",
    syntax="/dare [@user]",
    examples=["/dare", "/dare @username"]
)
async def cmd_dare(client: Client, message: Message):
    chat_id = message.chat.id
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")
        
    if await handle_bot_target(client, message, target):
        return

    name = get_name(target)
    
    # Fetch truth_dare state to track recently asked dares
    state = await db.get_game_state(chat_id, "truth_dare") or {"recent_truths": [], "recent_dares": []}
    recent_dares = state.get("recent_dares", [])
    
    available = [d for d in DARES if d not in recent_dares]
    if not available:
        available = DARES
        recent_dares = []
        
    dare_challenge = random.choice(available)
    recent_dares.append(dare_challenge)
    if len(recent_dares) > 30:
        recent_dares.pop(0)
        
    state["recent_dares"] = recent_dares
    await db.save_game_state(chat_id, "truth_dare", state)
    
    await message.reply(
        f"🔥 **Dare for {name}:**\n\n_{dare_challenge}_\n\n"
        f"└ _chicken out and you owe everyone_ 🫵"
    )


# ── Puzzles Game Engine ────────────────────────────────────────────────────────

@register_command(
    name="puzzles",
    description="Start a stateful puzzle game round.",
    category="Games",
    syntax="/puzzles",
    examples=["/puzzles"],
    aliases=["puzzle"]
)
async def cmd_puzzles(client: Client, message: Message):
    chat_id = message.chat.id
    
    active_game = await db.get_game_state(chat_id, "puzzles")
    if active_game and active_game.get("active"):
        # Check if already timed out in real time
        if time.time() - active_game.get("start_time", 0) < 30:
            return await message.reply("There is already an active puzzles game in this chat!")
    
    # Get puzzle number (auto-incrementing per chat)
    puzzle_num = (active_game or {}).get("puzzle_count", 0) + 1
    
    q = random_puzzles()
    start_time = time.time()
    
    state = {
        "active": True,
        "question": q["q"],
        "answer": q["a"],
        "hint": q.get("hint", ""),
        "creator": message.from_user.id if message.from_user else 0,
        "start_time": start_time,
        "expiration_time": start_time + 30,
        "points": 10,
        "puzzle_count": puzzle_num,
        "winner": None,
        "correct_answer": q["a"][0],
    }
    await db.save_game_state(chat_id, "puzzles", state)
    
    # Build display message
    display = f"🧩 **Puzzle #{puzzle_num}**\n\n{q['q']}\n"
    if q.get("hint"):
        display += f"\n💡 **Hint:** {q['hint']}"
    display += f"\n⏳ **Time:** 30s"
    display += "\n\n└ _First correct answer wins!_"
    
    await message.reply(display)
    
    # Schedule timeout
    asyncio.create_task(puzzles_timeout(client, chat_id, start_time, q["a"]))


@register_command(
    name="puzzles_top",
    description="Show the puzzles leaderboard.",
    category="Games",
    syntax="/puzzles_top",
    examples=["/puzzles_top"],
    aliases=["puzzlestop", "puzzle_top"]
)
async def cmd_puzzles_top(client: Client, message: Message):
    top = await db.get_puzzles_top(10)
    if not top:
        return await message.reply("No puzzle scores recorded yet! Play with `/puzzles`.")
        
    lines = ["🏆 **Puzzles Leaderboard** 🏆\n"]
    for i, u in enumerate(top, 1):
        name = u["first_name"]
        username_str = f" (@{u['username']})" if u["username"] else ""
        lines.append(f"{i}. **{name}**{username_str} — `{u['puzzles_points']} pts`")
        
    await message.reply("\n".join(lines))


@Client.on_message(filters.text & ~filters.bot, group=1)
async def puzzles_answer_check(client: Client, message: Message):
    chat_id = message.chat.id
    state = await db.get_game_state(chat_id, "puzzles")
    if not state or not state.get("active"):
        return
        
    # Check timeout manually as backup
    if time.time() - state.get("start_time", 0) >= 30:
        state["active"] = False
        await db.save_game_state(chat_id, "puzzles", state)
        return

    user_answer = (message.text or "").strip().lower()
    
    # Ignore commands
    if user_answer.startswith("/"):
        return
    
    correct_options = [ans.lower() for ans in state["answer"]]
    
    # Deterministic answer checking — exact match or close substring
    matched = False
    for opt in correct_options:
        if user_answer == opt or (len(user_answer) >= 3 and user_answer in opt) or (len(opt) >= 3 and opt in user_answer):
            matched = True
            break

    if matched:
        user = message.from_user
        if not user:
            return
            
        # Prevent race condition / duplicate winners: set inactive before doing replies
        state["active"] = False
        state["answered_by"] = user.id
        state["winner"] = user.id
        await db.save_game_state(chat_id, "puzzles", state)
        
        name = get_name(user)
        mention_str = f"@{user.username}" if user.username else mention(user.id, name)
        
        points = state.get("points", 10)
        await db.add_puzzles_points(user.id, user.first_name or "Someone", user.username or "", points)
        
        display_ans = state["answer"][0].title()
        await message.reply(
            f"🎉 **Correct!** {mention_str} got it right (+{points} pts).\n"
            f"└ The answer was: **{display_ans}**"
        )
        
        # CRITICAL: Stop message from reaching AI chat handler
        message.stop_propagation()
    # If wrong answer, don't stop propagation — let it pass through silently


# ── Guess the Number ──────────────────────────────────────────────────────────

@register_command(
    name="guess",
    description="Start a number guessing game (1-100).",
    category="Games",
    syntax="/guess",
    examples=["/guess"]
)
async def cmd_guess_start(client: Client, message: Message):
    chat_id = message.chat.id
    active_game = await db.get_game_state(chat_id, "guess")
    if active_game and active_game.get("active"):
        return await message.reply("A guess game is already running in this chat! Type `/endguess` to stop.")
        
    secret = random.randint(1, 100)
    state = {"active": True, "secret": secret, "attempts": 0}
    await db.save_game_state(chat_id, "guess", state)
    
    await message.reply(
        "🎲 **Guess the Number!**\n\n"
        "I'm thinking of a number between **1 and 100**.\n"
        "Reply with your guess!\n\n"
        "└ _Type `/endguess` to give up._"
    )


@register_command(
    name="endguess",
    description="End the active guessing game.",
    category="Games",
    syntax="/endguess",
    examples=["/endguess"],
    is_hidden=True
)
async def cmd_guess_end(client: Client, message: Message):
    chat_id = message.chat.id
    state = await db.get_game_state(chat_id, "guess")
    if state and state.get("active"):
        secret = state["secret"]
        await db.clear_game_state(chat_id, "guess")
        await message.reply(f"Game over! The number was **{secret}** 💀")
    else:
        await message.reply("No active guess game in this chat. Start one with `/guess`!")


@Client.on_message(filters.text & ~filters.bot, group=2)
async def guess_check(client: Client, message: Message):
    chat_id = message.chat.id
    state = await db.get_game_state(chat_id, "guess")
    if not state or not state.get("active"):
        return
        
    # Check if text is a number
    text = (message.text or "").strip()
    if not text.isdigit():
        return
        
    guess = int(text)
    secret = state["secret"]
    state["attempts"] += 1
    await db.save_game_state(chat_id, "guess", state)
    
    user = message.from_user
    name = get_name(user) if user else "You"
    
    if guess == secret:
        await db.clear_game_state(chat_id, "guess")
        await message.reply(
            f"🎉 **{name} got it!** The number was **{secret}**!\n"
            f"└ Attempts: `{state['attempts']}`"
        )
    elif guess < secret:
        await message.reply(f"📈 Higher! (guess: {guess}, attempts: {state['attempts']})")
    else:
        await message.reply(f"📉 Lower! (guess: {guess}, attempts: {state['attempts']})")
    
    # CRITICAL: Stop message from reaching AI chat handler
    message.stop_propagation()


# ── Rock Paper Scissors ───────────────────────────────────────────────────────

@register_command(
    name="rps",
    description="Play Rock Paper Scissors against the bot.",
    category="Games",
    syntax="/rps <rock|paper|scissors>",
    examples=["/rps rock"],
    required_args=1
)
async def cmd_rps(client: Client, message: Message):
    choice = message.command[1].lower()
    choices = ["rock", "paper", "scissors"]
    if choice not in choices:
        raise CommandValidationError("Invalid choice. Must be rock, paper, or scissors.")
        
    bot_choice = random.choice(choices)
    user = message.from_user
    
    # Win logic
    wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    
    if choice == bot_choice:
        result = "It's a draw! 🤝"
    elif wins[choice] == bot_choice:
        result = "You win! 🎉"
        if user:
            await db.increment_rps_wins(user.id, user.first_name or "Someone", user.username or "")
    else:
        result = "I win! 😎"
        
    emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    await message.reply(
        f"You: **{emojis[choice]} {choice.title()}**\n"
        f"Me: **{emojis[bot_choice]} {bot_choice.title()}**\n\n"
        f"**{result}**"
    )


# ── Coin Flip ─────────────────────────────────────────────────────────────────

@register_command(
    name="flip",
    description="Flip a coin.",
    category="Games",
    syntax="/flip",
    examples=["/flip"]
)
async def cmd_flip(client: Client, message: Message):
    sides = ["Heads", "Tails"]
    result = random.choice(sides)
    
    msg = await message.reply("Flipping a coin... 🪙")
    await asyncio.sleep(1.0)
    
    # 50% chance to append a fun message
    fun_text = ""
    if random.random() < 0.5:
        if result == "Heads":
            fun_text = "\n" + random.choice([
                "Looks like luck is on your side 😏",
                "Heads up! You got it ✨",
                "Lucky day today, huh? ❤️",
                "Heads wins! You're on fire 🔥"
            ])
        else:
            fun_text = "\n" + random.choice([
                "Better luck next time 😭",
                "Tails... oof, not this time 💀",
                "Sad vibes only, it's Tails 🤧",
                "Tails it is. Unlucky! 🤌"
            ])
            
    await msg.edit(f"🪙 **{result}**{fun_text}")