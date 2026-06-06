# ✨ Sizu AI Bot

A production-ready, modular Telegram AI assistant that feels like a real person. Powered by Python, Pyrogram, MongoDB, and OpenRouter (DeepSeek).

---

## 🌟 Introduction
Sizu is a unique Telegram AI assistant designed to break the mold of robotic, clinical bot interactions. With dynamic emotional awareness, natural casual phrasing, a built-in rate limiter, memory fallback, a suite of multiplayer group games, and utility modules, Sizu brings life, games, and helper tools directly into your DMs and group chats.

---

## 🚀 Features

| Category | Commands / Description |
|----------|----------|
| 💬 **AI Chat** | Auto-reply in private chats, trigger via `@mention` or custom trigger words in groups. |
| 🎮 **Games** | `/truth`, `/dare`, `/puzzles`, `/puzzles_top`, `/rps`, `/coin`, `/guess` |
| 🎭 **Fun** | `/roast`, `/compliment`, `/quote`, `/ship`, `/iq`, `/hack`, `/rizz` |
| 👋 **Group** | Automated welcome/farewell messages, sentiment-aware reactions. |
| 📊 **Info** | `/ping`, `/alive`, `/id`, `/stats`, `/start`, `/help` |
| 🔒 **Admin** | `/broadcast` (to all users), `/cleardb` |

---

## 🛠️ Tech Stack & Architecture

Sizu's design is fully asynchronous, modular, and resilient:

- **Framework:** [Pyrogram](https://github.com/pyrogram/pyrogram) (Async Telegram MTProto API Client)
- **Database:** MongoDB (via [Motor](https://motor.readthedocs.io/)) with an automatic, thread-safe in-memory fallback store (`MemoryStore`) if MongoDB is unavailable.
- **AI Integration:** Direct native connection to the official Google Gemini SDK as the primary provider, with sequential fallbacks to OpenRouter free models if Gemini is offline or unconfigured:
  - **Primary:** Google Gemini (native `gemini-2.5-flash` or custom via SDK)
  - **Fallback 1:** `openai/gpt-oss-20b:free` (OpenRouter)
  - **Fallback 2:** `z-ai/glm-4.5-air:free` (OpenRouter)
  - **Fallback 3:** `moonshotai/kimi-k2.6:free` (OpenRouter)
- **Hosting-ready:** Includes a keepalive web server on port `8080` (for Render free tier hosting).
- **Time Sync:** Synchronizes local client time with Google at boot to prevent MTProto `BadMsgNotification [16]` errors.

### Project Structure

```
sizuAi/
├── main.py              # Async entry point & Google time sync
├── config.py            # Global environment configuration & system prompt
├── core/                # Core engines
│   ├── bot.py           # SizuBot Client class (lifecycle management)
│   ├── ai_engine.py     # OpenRouter client, fallbacks, emotion & repetition mapping
│   └── rate_limiter.py  # User message rate limiting
├── database/            # Database layer
│   └── mongo.py         # MongoDB wrapper & local MemoryStore fallback
├── plugins/             # Pyrogram action handlers (auto-loaded)
│   ├── start.py         # Start/Help/Alive info commands
│   ├── chat.py          # AI conversation and history routing
│   ├── games.py         # Interaction games (puzzles, rps, etc.)
│   ├── fun.py           # Fun tools (roasts, ships, rizz check)
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
3. **No AI Clichés:** Never says robotic phrases like "Certainly!", "Of course!", or "Great question!". No bullet lists or formal outlines. Never says "As an AI..." or "As a language model...".
4. **Emoji Style:** Natural emojis like 😂 😭 😏 ✨ 🤌 💀 ❤️.
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
| `GEMINI_API_KEY` | API Key from Google AI Studio (needed for native primary Gemini). |
| `AI_PROVIDER` | `gemini` (uses native Google Gemini) or `openrouter` (uses OpenRouter fallback directly). |
| `GEMINI_MODEL` | Native Gemini model name (default: `gemini-2.5-flash`). |
| `OPENROUTER_API_KEY` | API Key from [OpenRouter](https://openrouter.ai) (used for fallbacks). |
| `FALLBACK_MODEL_1 / 2 / 3` | Fallback OpenRouter models tried in sequence (defaults: `gpt-oss`, `glm`, `kimi`). |
| `MONGO_URL` | MongoDB connection string (Optional; falls back to in-memory store if blank) |

### 3. Run the Bot
```bash
python main.py
```

---

## 🧠 Native Gemini Integration & Failover

Sizu uses a provider-abstracted AI engine supporting direct, native Google Gemini API access and OpenRouter failover pools.

### How to obtain a Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Log in with your Google account.
3. Click on **Create API Key** and generate a new key.
4. Copy the key and assign it to `GEMINI_API_KEY` in your `.env` configuration file.

### How Failover Works
When a message is received:
1. Sizu attempts to generate a response via the **native Google Gemini API** (using the model defined in `GEMINI_MODEL`).
2. If the Gemini API key is missing or the call fails (due to rate limits, network errors, or timeouts), Sizu logs the warning/error internally and instantly tries the **OpenRouter fallback model sequence** in order:
   - Fallback 1: `openai/gpt-oss-20b:free`
   - Fallback 2: `z-ai/glm-4.5-air:free`
   - Fallback 3: `moonshotai/kimi-k2.6:free`
3. If all API requests fail, Sizu replies with a friendly, casual human-like fallback response.
4. **Important:** Under no circumstances are the model names, providers, or failover errors exposed to Telegram users.

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
- **Memory & Privacy:** Conversation memory is limited to the last 20 messages to control token usage. You can use `/reset` to wipe chat memory at any time.

---
Built with ❤️ using Python, Pyrogram, Motor, and Gemini.
