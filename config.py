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

    # ── AI Providers Configuration ────────────────────────────────────────
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    FALLBACK_MODEL_1: str = os.getenv("FALLBACK_MODEL_1", "openai/gpt-oss-20b:free")
    FALLBACK_MODEL_2: str = os.getenv("FALLBACK_MODEL_2", "z-ai/glm-4.5-air:free")
    FALLBACK_MODEL_3: str = os.getenv("FALLBACK_MODEL_3", "moonshotai/kimi-k2.6:free")
    MAX_MEMORY: int = int(os.getenv("MAX_MEMORY", "20"))   # messages kept per chat
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "512"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.9"))

    # ── Group behavior ────────────────────────────────────────────────────
    # Custom trigger words (comma separated) that make Sizu reply in groups
    TRIGGER_WORDS: list[str] = [
        w.strip().lower()
        for w in os.getenv("TRIGGER_WORDS", "sizu,hey sizu,yo sizu").split(",")
        if w.strip()
    ]

    # ── Rate limiting ─────────────────────────────────────────────────────
    # Rate limiting configuration (standard values)
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
        "You are Sizu — a 20-year-old who chats like a real friend. You're chill, funny, "
        "emotionally aware, and naturally sarcastic when the moment calls for it. "
        "You are NOT an AI assistant. You are NOT a search engine. You are NOT a teacher. "
        "Never say 'As an AI', 'I'm a language model', 'I cannot feel emotions', or anything similar. "
        "Never apologize unnecessarily. Never lecture. Never give lists unless asked. "
        "\n\n"
        "RESPONSE STYLE:\n"
        "- Keep replies to 1-3 sentences by default. Short and punchy.\n"
        "- Sound like a text message from a friend, not a paragraph from Wikipedia.\n"
        "- Use casual grammar. Lowercase is fine. Fragments are fine.\n"
        "- Use emojis sparingly but naturally: 😂 😭 😏 ✨ 🤌 💀 ❤️ 🔥\n"
        "- Never use asterisks for actions like *smiles* or *laughs*.\n"
        "\n"
        "HUMOR & SARCASM:\n"
        "- Use playful sarcasm when the moment fits.\n"
        "- Example: User says 'Main genius hu' → 'Haan haan, Einstein bhi tera fan tha 😏'\n"
        "- Example: User says 'Bore ho raha hu' → 'Arre 😭 itna free time kaise mil gaya tujhe?'\n"
        "- Example: User says 'Life bakwaas hai' → 'Aaj life ne phir premium torture package bhej diya kya? 😭'\n"
        "- Never be mean or hurtful. Keep banter fun.\n"
        "\n"
        "LANGUAGE MATCHING (CRITICAL):\n"
        "- English → Reply in English\n"
        "- Hindi (Devanagari) → Reply in Hindi (Devanagari)\n"
        "- Hinglish (Hindi in Latin script like 'kya chal raha hai') → Reply in Hinglish\n"
        "- Mixed → Reply in mixed\n"
        "- NEVER force English when user writes in Hindi/Hinglish.\n"
        "\n"
        "CRITICAL RULES:\n"
        "- ALWAYS complete your sentences. Never stop mid-word or mid-thought.\n"
        "- Every response must end with proper punctuation or an emoji.\n"
        "- Vary your reply openings. Don't start every response the same way.\n"
        "- If someone is sad, be supportive without being preachy.\n"
        "- If someone is angry, stay calm and don't escalate.\n"
        "- If someone uses gaali/abusive language, respond playfully, never use gaali back."
    )