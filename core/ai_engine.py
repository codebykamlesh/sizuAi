"""
Sizu AI Engine — Abstraction layer for native Google Gemini and OpenRouter providers
with fallback sequence, emotional adaptation, response variation, and context trimming.
"""
import asyncio
import random
import re
from collections import defaultdict
from typing import Optional

import aiohttp
import google.generativeai as genai

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

# ── Valid sentence-ending characters for completeness check ────────────────────
VALID_ENDINGS = set(".?!…")
VALID_ENDING_EMOJIS = {
    "😂", "😭", "😏", "❤️", "✨", "🤌", "💀", "🥺", "🔥", "👑", "🙏", "💯",
    "🫠", "🤝", "👀", "😮", "😍", "🥰", "🎉", "😈", "👻", "🤧", "😩", "😎",
    "🫵", "💔", "💘", "💗", "🤣", "😬", "🪨", "✂️", "📄", "🪙", "🏓", "🌸",
    "👍", "👎", "🙄", "😤", "🤡", "💅", "🫡", "🤷", "😶", "🥲", "😒", "🤔",
    "☺️", "😊", "🥹", "❤️‍🔥", "💕", "😉", "🤭", "😌", "😳", "🫣",
}


def is_response_complete(text: str) -> bool:
    """
    Check if a response appears complete (not cut off mid-word or mid-sentence).
    Returns True if the response ends with valid punctuation or emoji.
    """
    if not text or len(text.strip()) < 3:
        return False

    stripped = text.rstrip()

    # Check if ends with valid punctuation
    if stripped[-1] in VALID_ENDINGS:
        return True

    # Check if ends with a closing quote after punctuation: "something."
    if len(stripped) >= 2 and stripped[-1] in ('"', "'", "\u201d", "\u2019") and stripped[-2] in VALID_ENDINGS:
        return True

    # Check if ends with valid emoji (emojis can be multi-char)
    for emoji in VALID_ENDING_EMOJIS:
        if stripped.endswith(emoji):
            return True

    # Check if ends with a closing parenthesis after punctuation: (something.)
    if len(stripped) >= 2 and stripped[-1] == ')' and stripped[-2] in VALID_ENDINGS:
        return True

    return False


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
            "Aree arre, chill karo, gaali dene ki kya zaroorat hai ❤️",
            "Itni gaaliyan padh ke mera processor hang ho gaya 💀",
            "Bhai tu gaali likhne mein PhD kar le, scope hai 😂",
            "Tera keyboard sirf gaali ke liye hai kya? 😭",
        ])

    return None


def trim_history(history: list[dict], max_messages: int = None) -> list[dict]:
    """Keep only the most recent messages to reduce token usage."""
    limit = max_messages or Config.MAX_MEMORY
    return history[-limit:]


def clean_response(text: str) -> str:
    """Remove AI artifacts from response text and fix incomplete endings."""
    # Strip markdown bold/italic from responses
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    # Strip action asterisks like *smiles*
    text = re.sub(r"\*[^*]+\*", "", text)
    # Remove leading whitespace/newlines
    text = text.strip()
    # Normalize multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # If response ends with an incomplete word (cut off mid-word),
    # try to trim back to the last complete sentence
    if text and not is_response_complete(text):
        # Find the last sentence-ending punctuation or emoji
        last_good = -1

        # Check for last valid punctuation
        for i in range(len(text) - 1, -1, -1):
            if text[i] in VALID_ENDINGS:
                last_good = i
                break

        # Check for last valid emoji ending
        if last_good == -1:
            for emoji in VALID_ENDING_EMOJIS:
                idx = text.rfind(emoji)
                if idx != -1:
                    end_idx = idx + len(emoji) - 1
                    if end_idx > last_good:
                        last_good = end_idx

        if last_good > 0:
            # Trim back to the last complete sentence
            text = text[:last_good + 1].strip()

    return text


# ── AI Provider Abstraction Interface ────────────────────────────────────────

class AIProvider:
    """Base interface for all conversational AI model providers."""
    async def generate_response(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int
    ) -> Optional[str]:
        raise NotImplementedError


class GeminiProvider(AIProvider):
    """Google Gemini Provider called natively via Google's official SDK."""
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self._configured = False
        if api_key:
            genai.configure(api_key=api_key)
            self._configured = True

    async def generate_response(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int
    ) -> Optional[str]:
        if not self._configured:
            log.warning("GeminiProvider called but not configured (missing GEMINI_API_KEY)")
            return None

        try:
            # Map history into Gemini native format, extracting the system prompt
            system_instruction = None
            contents = []
            for msg in messages:
                if msg["role"] == "system":
                    system_instruction = msg["content"]
                    continue
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [msg["content"]]
                })

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            loop = asyncio.get_running_loop()

            def _call():
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_instruction,
                    generation_config=generation_config
                )
                response = model.generate_content(contents)
                return response.text

            # Explicit timeout to prevent hanging forever
            response_text = await asyncio.wait_for(
                loop.run_in_executor(None, _call),
                timeout=25.0
            )
            return response_text
        except asyncio.TimeoutError:
            log.warning("GeminiProvider timed out after 25s")
            return None
        except Exception as e:
            log.error(f"Error in GeminiProvider: {e}")
            return None


class OpenRouterProvider(AIProvider):
    """Fallback provider querying OpenRouter models."""
    def __init__(self, api_key: str, model_name: str, get_session_func):
        self.api_key = api_key
        self.model_name = model_name
        self.get_session_func = get_session_func
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate_response(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int
    ) -> Optional[str]:
        if not self.api_key:
            log.warning(f"OpenRouterProvider called for {self.model_name} but OPENROUTER_API_KEY is missing")
            return None

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.95,
            "frequency_penalty": 0.4,
            "presence_penalty": 0.3,
        }

        try:
            session = await self.get_session_func()
            async with session.post(self.url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("choices"):
                        return data["choices"][0]["message"]["content"]
                    else:
                        log.error(f"Empty choices payload from OpenRouter for {self.model_name}: {data}")
                        return None
                elif resp.status == 429:
                    log.warning(f"Rate limited on OpenRouter model {self.model_name}, backing off 5s")
                    await asyncio.sleep(5)
                    return None
                elif resp.status in (502, 503, 504):
                    log.warning(f"OpenRouter gateway error {resp.status} on model {self.model_name}")
                    return None
                else:
                    error_text = await resp.text()
                    log.error(f"OpenRouter API error {resp.status} on {self.model_name}: {error_text[:200]}")
                    return None
        except asyncio.TimeoutError:
            log.warning(f"Timeout calling OpenRouter model {self.model_name}")
            return None
        except aiohttp.ClientError as e:
            log.error(f"HTTP client error on OpenRouter model {self.model_name}: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error calling OpenRouter model {self.model_name}: {e}", exc_info=True)
            return None


class SizuAI:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        # Simple in-memory response variation tracker (last 6 openers per chat)
        self._recent_openers: dict[int, list[str]] = defaultdict(list)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=False, limit=20)
            timeout = aiohttp.ClientTimeout(total=20, connect=5)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/sizuai",
                    "X-Title": "SizuBot",
                },
            )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    def _get_providers(self) -> list[AIProvider]:
        """Dynamically build the provider sequence list based on current configs."""
        providers = []

        # 1. Native Gemini Provider (if configured as primary)
        if Config.AI_PROVIDER == "gemini":
            if Config.GEMINI_API_KEY:
                providers.append(GeminiProvider(Config.GEMINI_API_KEY, Config.GEMINI_MODEL))
            else:
                log.warning("AI_PROVIDER is set to 'gemini' but GEMINI_API_KEY is missing. Skipping primary Gemini.")

        # 2. OpenRouter Fallbacks
        if Config.OPENROUTER_API_KEY:
            for fallback_model in [Config.FALLBACK_MODEL_1, Config.FALLBACK_MODEL_2, Config.FALLBACK_MODEL_3]:
                if fallback_model:
                    providers.append(OpenRouterProvider(Config.OPENROUTER_API_KEY, fallback_model, self._get_session))
        else:
            log.warning("OPENROUTER_API_KEY is missing. OpenRouter fallbacks are unavailable.")

        return providers

    async def _try_generate(
        self,
        provider: AIProvider,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> Optional[str]:
        """Try generating a response from a single provider with retry on incomplete output."""
        for attempt in range(2):  # Try up to 2 times per provider
            response = await provider.generate_response(messages, temperature, max_tokens)
            if not response:
                break  # Provider failed entirely, move to next

            cleaned = clean_response(response)
            if not cleaned:
                break  # Empty after cleaning

            if is_response_complete(cleaned):
                return cleaned

            # Response is incomplete — retry once
            if attempt == 0:
                log.warning(f"Incomplete response detected (attempt 1), retrying: '{cleaned[-50:]}'")
                continue
            else:
                # Second attempt also incomplete — reject this provider
                log.warning(f"Response still incomplete after retry, rejecting provider.")
                break

        return None

    async def get_response(
        self,
        chat_id: int,
        history: list[dict],
        user_input: str,
        user_name: str = "there",
    ) -> str:
        """
        Generate a response from Sizu's AI engine.
        Sequentially tries Gemini, then fallback OpenRouter models.
        Validates response completeness and retries if needed.
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

        providers = self._get_providers()
        for provider in providers:
            result = await self._try_generate(
                provider, messages,
                temperature=Config.AI_TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
            if result:
                # Track opener for variation
                opener = result.split()[0].lower() if result else ""
                openers = self._recent_openers[chat_id]
                openers.append(opener)
                if len(openers) > 6:
                    openers.pop(0)
                return result

        log.warning(f"All providers failed for chat {chat_id}, using fallback response")
        return random.choice(FALLBACK_RESPONSES)

    async def get_quick_response(self, prompt: str, max_tokens: int = 150) -> str:
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

        providers = self._get_providers()
        for provider in providers:
            result = await self._try_generate(
                provider, messages,
                temperature=Config.AI_TEMPERATURE,
                max_tokens=max_tokens
            )
            if result:
                return result

        return random.choice(FALLBACK_RESPONSES)


# Singleton
sizu_ai = SizuAI()
