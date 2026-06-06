"""
Sizu AI Engine — OpenRouter + DeepSeek with emotional adaptation,
response variation, context trimming, and graceful fallback.
"""
import asyncio
import random
import re
import time
from collections import defaultdict
from typing import Optional

import aiohttp

from config import Config
from utils.logger import setup_logger

log = setup_logger("sizu.ai")

# ── Fallback responses (used when API is down) ────────────────────────────────
FALLBACK_RESPONSES = [
    "ugh my brain just lagged for a sec, what were you saying",
    "wait i zoned out lol, say that again?",
    "ok internet is being weird rn, gimme a sec",
    "🫠 my thoughts just buffered... try again?",
    "ngl my vibe is off right now, ask me again in a bit",
    "lol ok that question made me freeze up",
    "brb my brain needs a reboot 💀",
]

# ── Emotion keywords for context adaptation ───────────────────────────────────
EMOTION_MAP = {
    "sad": ["sad", "cry", "crying", "depressed", "hurt", "pain", "miss", "grief", "bura", "rone", "ro raha", "ro rahi", "udaas", "udas", "broken", "dukh", "dukhi"],
    "happy": ["happy", "excited", "amazing", "great", "awesome", "love", "yay", "woah", "omg", "khush", "mast", "maza", "gazab", "badhiya", "sahi hai", "party", "cool"],
    "angry": ["angry", "mad", "furious", "rage", "hate", "annoyed", "frustrated", "pissed", "gussa", "gusse", "irritate", "irritated", "krodh"],
    "lonely": ["lonely", "alone", "akela", "akeli", "koi nahi", "tanha", "sunsan"],
    "bored": ["bored", "boring", "nothing to do", "meh", "idc", "whatever", "bore", "pakk gaya", "pak gaya"],
}

EMOTION_HINTS = {
    "sad": " The user seems sad or down. Be warm and supportive, but don't be preachy. Just be there. Example: 'Sorry yaar, ye sunke bura laga. Kya hua?'",
    "happy": " The user is hyped or happy. Match their energy! Example: 'Wahh, that's awesome 🎉'",
    "angry": " The user seems angry or frustrated. Stay calm, don't become defensive, and don't dismiss their feelings.",
    "lonely": " The user seems lonely. Be warm, friendly, and conversational.",
    "bored": " The user seems bored. Be fun and engaging, stir something up.",
}


def detect_emotion(text: str) -> Optional[str]:
    text_lower = text.lower()
    for emotion, keywords in EMOTION_MAP.items():
        if any(kw in text_lower for kw in keywords):
            return emotion
    return None


def handle_abusive_language(text: str) -> Optional[str]:
    """Detect Hindi/English gaali/abusive language and return a playful response."""
    text_lower = text.lower()

    abusive_patterns = [
        r"\bchut(i)?ya(e)?\b",
        r"\bmadarchod\b|\bmaderchod\b|\bmc\b",
        r"\bbe(h)?enchod\b",
        r"\bbc\b",
        r"\bbhadwa\b",
        r"\bbhadwe\b",
        r"\blode\b",
        r"\blauda\b",
        r"\blawda\b",
        r"\blodu\b",
        r"\bharami\b",
        r"\bkamina\b",
        r"\bkamine\b",
        r"\bchut\b",
        r"\bgandu\b",
        r"\bsala\b",
        r"\bsale\b",
    ]

    if any(re.search(pat, text_lower) for pat in abusive_patterns):
        return random.choice([
            "Kitni gaali deta hai yaar 😂",
            "Arre arre, shaant ho jao 😭",
            "Aaj mood off lag raha hai 😏",
            "Kitni gaali doge yaar, thoda shaant ho jao 🤧",
            "Aree arre, chill karo, gaali dene ki kya zaroorat hai ❤️"
        ])

    return None


def trim_history(history: list[dict], max_messages: int = None) -> list[dict]:
    """Keep only the most recent messages to reduce token usage."""
    limit = max_messages or Config.MAX_MEMORY
    return history[-limit:]


def clean_response(text: str) -> str:
    """Remove AI artifacts from response text."""
    # Strip markdown bold/italic from responses
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    # Strip action asterisks like *smiles*
    text = re.sub(r"\*[^*]+\*", "", text)
    # Remove leading whitespace/newlines
    text = text.strip()
    # Normalize multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


class SizuAI:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.AI_MODEL
        self.fallback_model = Config.AI_FALLBACK_MODEL
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self._session: Optional[aiohttp.ClientSession] = None
        # Simple in-memory response variation tracker (last 5 openers per chat)
        self._recent_openers: dict[int, list[str]] = defaultdict(list)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=False, limit=20)
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/sizuai",
                    "X-Title": "SizuBot",
                },
            )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_response(
        self,
        chat_id: int,
        history: list[dict],
        user_input: str,
        user_name: str = "there",
    ) -> str:
        """
        Generate a response from Sizu's AI engine.
        Falls back to fallback model, then to canned response on failure.
        """
        # Intercept abusive language locally first
        abusive_reply = handle_abusive_language(user_input)
        if abusive_reply:
            return abusive_reply

        emotion = detect_emotion(user_input)
        system = Config.SYSTEM_PROMPT
        if emotion and emotion in EMOTION_HINTS:
            system += EMOTION_HINTS[emotion]

        # Add variation hint if we detect repetitive openers
        recent = self._recent_openers.get(chat_id, [])
        if len(recent) >= 3:
            system += " IMPORTANT: Don't start your reply the same way you did recently. Vary your sentence openings."

        trimmed_history = trim_history(history, Config.MAX_MEMORY)
        messages = [{"role": "system", "content": system}]
        for msg in trimmed_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_input})

        # Try primary model, then fallback
        for model in [self.model, self.fallback_model]:
            response = await self._call_api(model, messages)
            if response:
                cleaned = clean_response(response)
                if cleaned:
                    # Track opener for variation
                    opener = cleaned.split()[0].lower() if cleaned else ""
                    openers = self._recent_openers[chat_id]
                    openers.append(opener)
                    if len(openers) > 6:
                        openers.pop(0)
                    return cleaned

        log.warning(f"All models failed for chat {chat_id}, using fallback response")
        return random.choice(FALLBACK_RESPONSES)

    async def _call_api(self, model: str, messages: list[dict]) -> Optional[str]:
        """Call OpenRouter API with a specific model."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": Config.AI_TEMPERATURE,
            "max_tokens": Config.MAX_TOKENS,
            "top_p": 0.95,
            "frequency_penalty": 0.4,  # Reduces repetition
            "presence_penalty": 0.3,
        }
        try:
            session = await self._get_session()
            async with session.post(self.url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                elif resp.status == 429:
                    log.warning(f"Rate limited on model {model}, backing off 5s")
                    await asyncio.sleep(5)
                    return None
                elif resp.status in (502, 503, 504):
                    log.warning(f"OpenRouter gateway error {resp.status} on model {model}")
                    return None
                else:
                    error_text = await resp.text()
                    log.error(f"API error {resp.status} on {model}: {error_text[:200]}")
                    return None
        except asyncio.TimeoutError:
            log.warning(f"Timeout calling model {model}")
            return None
        except aiohttp.ClientError as e:
            log.error(f"HTTP client error on {model}: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error calling {model}: {e}", exc_info=True)
            return None

    async def get_quick_response(self, prompt: str, max_tokens: int = 100) -> str:
        """
        Fire a one-shot prompt without history — used by games and fun commands.
        """
        # Intercept abusive language locally first
        abusive_reply = handle_abusive_language(prompt)
        if abusive_reply:
            return abusive_reply

        messages = [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        for model in [self.model, self.fallback_model]:
            response = await self._call_api(model, messages)
            if response:
                return clean_response(response)
        return random.choice(FALLBACK_RESPONSES)


# Singleton
sizu_ai = SizuAI()
