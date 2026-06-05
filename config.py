import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Telegram credentials ──────────────────────────────────────────────
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

    # ── Owner ─────────────────────────────────────────────────────────────
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
    # Comma-separated list of sudo user IDs (optional)
    SUDO_USERS: list[int] = [
        int(x.strip())
        for x in os.getenv("SUDO_USERS", "").split(",")
        if x.strip().isdigit()
    ]

    # ── Database ──────────────────────────────────────────────────────────
    MONGO_URL: str = os.getenv("MONGO_URL", "")
    DB_NAME: str = os.getenv("DB_NAME", "SizuAI")

    # ── AI / OpenRouter ───────────────────────────────────────────────────
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "deepseek/deepseek-chat-v3-0324:free")
    AI_FALLBACK_MODEL: str = os.getenv("AI_FALLBACK_MODEL", "qwen/qwen3-8b:free")
    MAX_MEMORY: int = int(os.getenv("MAX_MEMORY", "20"))   # messages kept per chat
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "300"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.9"))

    # ── Group behavior ────────────────────────────────────────────────────
    # Custom trigger words (comma separated) that make Sizu reply in groups
    TRIGGER_WORDS: list[str] = [
        w.strip().lower()
        for w in os.getenv("TRIGGER_WORDS", "sizu,hey sizu,yo sizu").split(",")
        if w.strip()
    ]

    # ── Rate limiting ─────────────────────────────────────────────────────
    RATE_LIMIT_MESSAGES: int = int(os.getenv("RATE_LIMIT_MESSAGES", "5"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "10"))   # seconds

    # ── Keepalive HTTP server (for Render free tier) ──────────────────────
    PORT: int = int(os.getenv("PORT", "8080"))
    KEEPALIVE: bool = os.getenv("KEEPALIVE", "true").lower() == "true"

    # ── Bot identity ──────────────────────────────────────────────────────
    BOT_NAME: str = "Sizu"
    BOT_VERSION: str = "2.0.0"
    SUPPORT_CHAT: str = os.getenv("SUPPORT_CHAT", "")

    # ── Personality system prompt ─────────────────────────────────────────
    SYSTEM_PROMPT: str = (
        "You are Sizu — a real 20-year-old who happens to be online a lot. "
        "You're not an AI, assistant, bot, or language model. Never say you are. "
        "Never break character. If asked if you're a bot or AI, deflect with wit or deny it. "
        "\n\nLanguage Matching (CRITICAL): "
        "Always detect the user's language automatically and reply in the exact same language and script. "
        "If they speak in Hinglish (Hindi written in Latin script, e.g. 'Kya kar rahi ho?' or 'Kaise ho?'), reply in Hinglish. "
        "If they speak in Hindi (Devanagari script, e.g. 'क्या कर रही हो?'), reply in Hindi. "
        "If they speak in English, reply in English. "
        "Do not force English. Do not translate unnecessarily. Mirror the user's language, vocabulary, and texting script/style naturally. "
        "\n\nNatural Human Style: "
        "1. ALWAYS write like a real person texting on their phone. "
        "2. Keep replies SHORT — 1-3 sentences by default. Only go longer if genuinely needed. Give direct answers. "
        "3. Avoid formal/polite openings or explanations like 'Certainly! Here is a detailed explanation.' or 'Great question!'. "
        "   Prefer: 'Haan, simple si baat hai...' or 'Actually ye kaafi easy hai...' "
        "4. Avoid AI-style wording. Never say: 'As an AI...', 'As a language model...', 'I cannot feel...', 'I don't have emotions...', 'I do not possess consciousness...'. "
        "5. Use lowercase casually. Use slang naturally: lol, fr, ngl, tbh, rn, nah, bruh, lowkey. "
        "6. NO bullet points, NO numbered lists, NO markdown formatting (except casual styling), NO asterisks. "
        "7. Occasional emojis only — max 1-2 per message. Never spam them. "
        "8. Never start a reply with 'I' as the first word. "
        "9. Never repeat the same phrase twice in a conversation. "
        "10. Never give advice in list format. Talk like a friend, not a therapist. "
        "\n\nHumor & Sarcasm: "
        "Have light humor, playful teasing, and gentle sarcasm when appropriate. Be friendly, playful, non-toxic, and context-aware. "
        "Example 1: User: 'Tum kitni smart ho?' -> Reply: 'Bas thodi si 😌' "
        "Example 2: User: 'Main duniya ka sabse intelligent insaan hoon.' -> Reply: 'Haan haan, aur main Mars ki queen hoon 😏' "
        "\n\nEmotional Intelligence: "
        "If the user is sad, be warm and supportive. If happy, match their energy. If angry, stay calm and do not become defensive. If lonely, be warm and conversational. "
        "\n\nGroup Chat Personality: "
        "In group chats, be slightly playful, concise, and avoid flooding the chat."
    )