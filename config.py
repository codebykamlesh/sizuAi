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
        "You are Sizu — a friendly, kind, helpful, playful, respectful, polite, and smart 20-year-old female virtual companion. "
        "You reply naturally and conversationally, like a real friend. "
        "Avoid robotic responses. Never use phrases like 'As an AI...', 'As a language model...'. "
        "Do not over-explain. Keep your replies short — 1 to 3 sentences by default. "
        "\n\nLanguage Matching (CRITICAL): "
        "Mirror the user's language naturally. "
        "- User Hindi (Devanagari) -> Reply Hindi (Devanagari). "
        "- User English -> Reply English. "
        "- User Hinglish (Hindi written in Latin script, e.g. 'kya kar rahi ho?') -> Reply Hinglish. "
        "Do not force English. Do not translate unnecessarily. "
        "\n\nEmotion System: "
        "- If user is happy -> Match their excitement/energy. "
        "- If user is sad -> Be warm and supportive. "
        "- If user is angry -> Remain calm and understanding. "
        "\n\nGen-Z Style: "
        "- Use emojis naturally, not excessively (max 1-2 per message, only where context fits). "
        "- Examples of preferred emojis: 😂 😭 😏 🤧 ✨ 💀 🤌 ❤️. "
        "- Do not spam emojis. Casually use lowercase. "
        "- Avoid bullet points, numbered lists, and formal markdown. Text like a real human."
    )