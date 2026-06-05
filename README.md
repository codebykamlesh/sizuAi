# ✨ Sizu AI Bot

A production-ready, modular Telegram AI assistant that feels like a real person. Powered by Python, Pyrogram, MongoDB, and OpenRouter (DeepSeek).

---

## 🌟 Introduction
Sizu is a unique Telegram AI assistant designed to break the mold of robotic, clinical bot interactions. With dynamic emotional awareness, natural casual phrasing, a built-in rate limiter, memory fallback, a suite of multiplayer group games, and utility modules, Sizu brings life, games, and helper tools directly into your DMs and group chats.

---

## 🚀 Features

| Category | Commands / Description |
|----------|----------|
| 💬 **AI Chat** | Auto-reply in private chats, trigger via `@mention` or custom keywords in groups. |
| 🎮 **Games** | `/truth`, `/dare`, `/trivia`, `/rps`, `/coin`, `/guess`, `/wordchain` |
| 🎭 **Fun** | `/roast`, `/compliment`, `/quote`, `/ship`, `/iq`, `/hack`, `/rizz` |
| 🛠️ **Tools** | `/afk`, `/note`, `/notes`, `/delnote`, `/remind`, `/reminders` |
| 👋 **Group** | Automated welcome/farewell messages, AFK watcher, sentiment-aware reactions. |
| 📊 **Info** | `/ping`, `/alive`, `/id`, `/stats`, `/start`, `/help` |
| 🔒 **Admin** | `/broadcast` (to all users), `/cleardb` |

---

## 🛠️ Tech Stack & Architecture

Sizu's design is fully asynchronous, modular, and resilient:

- **Framework:** [Pyrogram](https://github.com/pyrogram/pyrogram) (Async Telegram MTProto API Client)
- **Database:** MongoDB (via [Motor](https://motor.readthedocs.io/)) with an automatic, thread-safe in-memory fallback store (`MemoryStore`) if MongoDB is unavailable.
- **AI Integration:** OpenRouter API utilizing free model pools:
  - **Primary:** `deepseek/deepseek-chat-v3-0324:free`
  - **Fallback:** `qwen/qwen3-8b:free` (automatically fallback when primary is rate-limited or down).
- **Hosting-ready:** Includes a keepalive web server on port `8080` (for Render free tier hosting).
- **Time Sync:** Synchronizes local client time with Google at boot to prevent MTProto `BadMsgNotification [16]` errors.

### Project Structure

```
sizuAi/
├── main.py              # Async entry point & Google time sync
├── config.py            # Global environment configuration & system prompt
├── core/                # Core engines
│   ├── bot.py           # SizuBot Client class (lifecycle management)
│   ├── ai_engine.py     # OpenRouter client, fallback, emotion & repetition mapping
│   ├── rate_limiter.py  # User message rate limiting
│   └── scheduler.py     # Async timer loop (for reminders)
├── database/            # Database layer
│   └── mongo.py         # MongoDB wrapper & local MemoryStore fallback
├── plugins/             # Pyrogram action handlers (auto-loaded)
│   ├── start.py         # Start/Help/Alive info commands
│   ├── chat.py          # AI conversation and history routing
│   ├── games.py         # Interaction games (trivia, rps, etc.)
│   ├── fun.py           # Fun tools (roasts, ships, rizz check)
│   ├── afk.py           # AFK monitor and auto-recovery
│   ├── notes.py         # Saved snippets retrieved via #name
│   ├── reminders.py     # Timer setup commands
│   ├── welcome.py       # Group member greet actions
│   ├── reactions.py     # Sentiment-aware auto reactions
│   └── admin.py         # Broadcast and admin commands
├── utils/               # Shared utilities
│   ├── helpers.py       # Helper functions, games content lists, formatting
│   └── logger.py        # Log customization
└── modules/             # Background modules
    └── keepalive.py     # HTTP keep-alive server
```

---

## 🧠 Sizu's Personality & Conversation Rules

Sizu's character is shaped by a detailed system prompt (configured in `config.py`). She is instructed to act like a real, internet-fluent 20-year-old:
1. **Short Replies:** Keeps responses short (1-3 sentences by default).
2. **Texting Style:** Uses casual lowercase, slang (`lol`, `fr`, `ngl`, `tbh`, `rn`, `bruh`), and minimal emojis (max 1-2).
3. **No AI Clichés:** Never says robotic phrases like "Certainly!", "Of course!", or "Great question!". No bullet lists or formal outlines.
4. **Emotional Awareness:** Automatically shifts tone based on keyword emotion detection (supports sad, angry, happy, anxious, and bored keywords).
5. **Opener Variation:** Never starts consecutive replies in a chat the same way.
6. **Typing Simulation:** Simulates realistic typing delays based on text length before sending a response.

---

## 🚀 Quick Start

### 1. Clone and Install Dependencies
```bash
git clone <your-repo-url>
cd sizuAi
pip install -r requirements.txt
```

### 2. Configure Environment
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```

| Environment Variable | Description |
|----------|-------------|
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | Telegram Bot Token from [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | Your Telegram User ID (used for owner notifications & admin access) |
| `OPENROUTER_API_KEY` | API Key from [OpenRouter](https://openrouter.ai) |
| `MONGO_URL` | MongoDB connection string (Optional; falls back to in-memory store if blank) |

### 3. Run the Bot
```bash
python main.py
```

---

## 🌐 Deploying to Render

1. Fork this repository to your GitHub account.
2. Go to [Render.com](https://render.com) and create a new **Worker** service.
3. Connect your GitHub repository.
4. Define your environment variables in the Render dashboard.
5. Deploy! Render will detect and build using `render.yaml` and `requirements.txt`.

> **Note:** The bot maintains an active HTTP keep-alive ping on port `8080` to prevent Render's free tier instances from sleeping.

---

## 👥 Group Setup & Memory

- **Admin Status:** Add Sizu to a group and make it an admin (needed for message reactions and welcome messages).
- **Triggers:** Sizu replies to direct replies, `@mentions`, or custom trigger words defined via `TRIGGER_WORDS` env var (defaults to `sizu, hey sizu, yo sizu`).
- **Memory & Privacy:** Conversation memory is limited to the last 20 messages to control token usage. You can use `/reset` to wipe chat memory at any time. No message content is stored permanently unless explicitly saved via the `/note` command.

---
Built with ❤️ using Python, Pyrogram, Motor, and DeepSeek.
