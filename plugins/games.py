"""
Games plugin — Stateful, Persistent, Multiplayer Trivia, Guess, Word Chain, RPS, Coin Flip, Truth & Dare.
"""
import asyncio
import random
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from core.commands import register_command, CommandValidationError
from database.mongo import db
from utils.helpers import (
    get_name, mention, random_trivia,
    TRUTHS, DARES, get_target_user
)
from utils.logger import setup_logger

log = setup_logger("sizu.games")


# ── Expiration / Timeout Tasks ────────────────────────────────────────────────

async def trivia_timeout(client: Client, chat_id: int, start_time: float, answer: str):
    """Wait 30s and expire trivia question if still active."""
    await asyncio.sleep(30)
    state = await db.get_game_state(chat_id, "trivia")
    if state and state.get("active") and state.get("start_time") == start_time:
        state["active"] = False
        await db.save_game_state(chat_id, "trivia", state)
        try:
            await client.send_message(
                chat_id,
                f"⏰ **Time's up!** No one got it right.\n"
                f"└ The correct answer was: ||{answer}||"
            )
        except Exception as e:
            log.debug(f"Error sending trivia timeout message: {e}")


# ── Truth & Dare ──────────────────────────────────────────────────────────────

@register_command(
    name="truth",
    description="Play truth or dare (truth question). Avoids repeats.",
    category="Games",
    syntax="/truth",
    examples=["/truth"]
)
async def cmd_truth(client: Client, message: Message):
    chat_id = message.chat.id
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")
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
    if len(recent_truths) > 15:
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
    syntax="/dare",
    examples=["/dare"]
)
async def cmd_dare(client: Client, message: Message):
    chat_id = message.chat.id
    target = await get_target_user(client, message, default_to_sender=True)
    if not target:
        return await message.reply("❌ No target user found.")
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
    if len(recent_dares) > 15:
        recent_dares.pop(0)
        
    state["recent_dares"] = recent_dares
    await db.save_game_state(chat_id, "truth_dare", state)
    
    await message.reply(
        f"🔥 **Dare for {name}:**\n\n_{dare_challenge}_\n\n"
        f"└ _chicken out and you owe everyone_ 🫵"
    )


# ── Trivia Game Engine ────────────────────────────────────────────────────────

@register_command(
    name="trivia",
    description="Start a stateful trivia game round.",
    category="Games",
    syntax="/trivia",
    examples=["/trivia"]
)
async def cmd_trivia(client: Client, message: Message):
    chat_id = message.chat.id
    
    active_game = await db.get_game_state(chat_id, "trivia")
    if active_game and active_game.get("active"):
        # Check if already timed out in real time
        if time.time() - active_game.get("start_time", 0) < 30:
            return await message.reply("There is already an active trivia game in this chat!")
            
    q = random_trivia()
    start_time = time.time()
    
    state = {
        "active": True,
        "question": q["q"],
        "answer": q["a"],
        "creator": message.from_user.id if message.from_user else 0,
        "start_time": start_time,
        "points": 10,
    }
    await db.save_game_state(chat_id, "trivia", state)
    
    await message.reply(
        f"🧠 **Trivia Time!**\n\n"
        f"❓ {q['q']}\n"
        f"💡 Answer: ||{q['a']}||\n\n"
        f"└ _First correct answer wins! (Time limit: 30s)_"
    )
    
    # Schedule timeout
    asyncio.create_task(trivia_timeout(client, chat_id, start_time, q["a"]))


@register_command(
    name="trivia_top",
    description="Show the trivia leaderboard.",
    category="Games",
    syntax="/trivia_top",
    examples=["/trivia_top"]
)
async def cmd_trivia_top(client: Client, message: Message):
    top = await db.get_trivia_top(10)
    if not top:
        return await message.reply("No trivia scores recorded yet! Play with `/trivia`.")
        
    lines = ["🏆 **Trivia Leaderboard** 🏆\n"]
    for i, u in enumerate(top, 1):
        name = u["first_name"]
        username_str = f" (@{u['username']})" if u["username"] else ""
        lines.append(f"{i}. **{name}**{username_str} — `{u['trivia_points']} pts`")
        
    await message.reply("\n".join(lines))


@Client.on_message(filters.text & ~filters.bot, group=1)
async def trivia_answer_check(client: Client, message: Message):
    chat_id = message.chat.id
    state = await db.get_game_state(chat_id, "trivia")
    if not state or not state.get("active"):
        return
        
    # Check timeout manually as backup
    if time.time() - state.get("start_time", 0) >= 30:
        state["active"] = False
        await db.save_game_state(chat_id, "trivia", state)
        return

    user_answer = (message.text or "").strip().lower()
    correct_answer = state["answer"].lower()
    
    # Match exact or close match (e.g. Vatican City -> vatican city or vatican)
    if user_answer == correct_answer or (len(user_answer) >= 3 and user_answer in correct_answer):
        user = message.from_user
        if not user:
            return
            
        # Prevent race condition / duplicate winners: set inactive before doing replies
        state["active"] = False
        state["answered_by"] = user.id
        await db.save_game_state(chat_id, "trivia", state)
        
        name = get_name(user)
        mention_str = f"@{user.username}" if user.username else mention(user.id, name)
        
        points = state.get("points", 10)
        await db.add_trivia_points(user.id, user.first_name or "Someone", user.username or "", points)
        
        await message.reply(
            f"🎉 **Correct!** {mention_str} got it right (+{points} pts).\n"
            f"└ The answer was: **{state['answer']}**"
        )


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


# ── Word Chain ────────────────────────────────────────────────────────────────

@register_command(
    name="wordchain",
    description="Start a wordchain game.",
    category="Games",
    syntax="/wordchain",
    examples=["/wordchain"]
)
async def cmd_wordchain_start(client: Client, message: Message):
    chat_id = message.chat.id
    active_game = await db.get_game_state(chat_id, "wordchain")
    if active_game and active_game.get("active"):
        return await message.reply("A wordchain game is already active in this chat! Type `/stopchain` to stop.")
        
    starter = "apple"
    state = {
        "active": True,
        "last_word": starter,
        "last_player_id": 0,
        "used_words": [starter]
    }
    await db.save_game_state(chat_id, "wordchain", state)
    
    await message.reply(
        f"🔗 **Word Chain started!**\n\n"
        f"I'll start: **{starter}**\n\n"
        f"Your word must start with **'{starter[-1].upper()}'**.\n"
        f"└ _Type `/stopchain` to end. Players must alternate turns!_"
    )


@register_command(
    name="stopchain",
    description="Stop the active wordchain game.",
    category="Games",
    syntax="/stopchain",
    examples=["/stopchain"],
    is_hidden=True
)
async def cmd_wordchain_stop(client: Client, message: Message):
    chat_id = message.chat.id
    state = await db.get_game_state(chat_id, "wordchain")
    if state and state.get("active"):
        await db.clear_game_state(chat_id, "wordchain")
        await message.reply("Word chain ended! 🛑")
    else:
        await message.reply("No active wordchain game in this chat.")


@Client.on_message(filters.text & ~filters.bot, group=3)
async def wordchain_check(client: Client, message: Message):
    chat_id = message.chat.id
    state = await db.get_game_state(chat_id, "wordchain")
    if not state or not state.get("active"):
        return
        
    word = (message.text or "").strip().lower()
    
    # Check if single word, only alphabetical, length >= 2
    if " " in word or not word.isalpha() or len(word) < 2:
        return
        
    user = message.from_user
    if not user:
        return
        
    # Track player turns (alternate turns)
    if state.get("last_player_id") == user.id:
        await message.reply("❌ It's not your turn! Let someone else play next.")
        return
        
    # Validate starting letter
    last_word = state["last_word"]
    required_letter = last_word[-1]
    if not word.startswith(required_letter):
        await message.reply(
            f"❌ Invalid letter! Your word must start with **'{required_letter.upper()}'**.\n"
            f"└ Last word: _{last_word}_"
        )
        return
        
    # Reject already used words
    used_words = state.get("used_words", [])
    if word in used_words:
        await message.reply(f"❌ **{word}** has already been used in this game!")
        return
        
    # Valid word!
    used_words.append(word)
    state["last_word"] = word
    state["last_player_id"] = user.id
    state["used_words"] = used_words
    
    await db.save_game_state(chat_id, "wordchain", state)
    
    # Score user
    await db.add_wordchain_points(user.id, user.first_name or "Someone", user.username or "", 5)
    
    await message.reply(
        f"✅ **{word}** (+5 pts) — now your turn! Start with **'{word[-1].upper()}'** 🔗"
    )


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