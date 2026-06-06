"""
Sizu Database Layer
MongoDB with automatic in-memory fallback.
Every method gracefully degrades if MongoDB is unavailable.
"""
import asyncio
import time
from collections import defaultdict
from typing import Any, Optional

from config import Config
from utils.logger import setup_logger

log = setup_logger("sizu.database")


# ── In-memory fallback store ──────────────────────────────────────────────────

class MemoryStore:
    """Thread-safe in-memory store that mirrors MongoDB operations."""

    def __init__(self):
        self._memory: dict[int, list[dict]] = defaultdict(list)       # chat_id -> messages
        self._users: dict[int, dict] = {}                              # user_id -> user data
        self._welcome: dict[int, str] = {}                             # chat_id -> welcome text
        self._game_stats: dict[int, dict] = defaultdict(dict)          # user_id -> stats
        self._game_states: dict[str, dict] = {}                        # "chat_id:game_type" -> state
        self._puzzles_points: dict[int, int] = {}
        self._rps_wins: dict[int, int] = {}
        self._coin_streak: dict[int, int] = {}
        self._max_coin_streak: dict[int, int] = {}
        self._sizu_admins: set[int] = set()

    # Chat memory
    def save_message(self, chat_id: int, role: str, content: str, max_size: int) -> None:
        self._memory[chat_id].append({"role": role, "content": content})
        if len(self._memory[chat_id]) > max_size:
            self._memory[chat_id] = self._memory[chat_id][-max_size:]

    def get_history(self, chat_id: int) -> list[dict]:
        return list(self._memory[chat_id])

    def clear_history(self, chat_id: int) -> None:
        self._memory.pop(chat_id, None)

    # Users
    def upsert_user(self, user_id: int, data: dict) -> None:
        self._users.setdefault(user_id, {}).update(data)

    def get_user(self, user_id: int) -> dict:
        return self._users.get(user_id, {})

    def count_users(self) -> int:
        return len(self._users)

    def all_user_ids(self) -> list[int]:
        return list(self._users.keys())

    # Sizu Admins
    def add_sizu_admin(self, user_id: int) -> None:
        self._sizu_admins.add(user_id)

    def remove_sizu_admin(self, user_id: int) -> bool:
        if user_id in self._sizu_admins:
            self._sizu_admins.remove(user_id)
            return True
        return False

    def is_sizu_admin(self, user_id: int) -> bool:
        return user_id in self._sizu_admins

    def get_sizu_admins(self) -> list[int]:
        return list(self._sizu_admins)

    # Welcome
    def set_welcome(self, chat_id: int, text: str) -> None:
        self._welcome[chat_id] = text

    def get_welcome(self, chat_id: int) -> Optional[str]:
        return self._welcome.get(chat_id)

    # Game stats
    def update_stats(self, user_id: int, game: str, result: str) -> None:
        stats = self._game_stats[user_id]
        stats.setdefault(game, {"wins": 0, "losses": 0, "draws": 0})
        if result in stats[game]:
            stats[game][result] += 1

    def get_stats(self, user_id: int) -> dict:
        return dict(self._game_stats[user_id])

    # Game States
    def save_game_state(self, chat_id: int, game_type: str, state: dict) -> None:
        self._game_states[f"{chat_id}:{game_type}"] = state

    def get_game_state(self, chat_id: int, game_type: str) -> Optional[dict]:
        return self._game_states.get(f"{chat_id}:{game_type}")

    def clear_game_state(self, chat_id: int, game_type: str) -> None:
        self._game_states.pop(f"{chat_id}:{game_type}", None)

    # Game Scores
    def add_puzzles_points(self, user_id: int, points: int) -> None:
        self._puzzles_points[user_id] = self._puzzles_points.get(user_id, 0) + points

    def get_puzzles_points(self, user_id: int) -> int:
        return self._puzzles_points.get(user_id, 0)

    def get_puzzles_top(self, limit: int) -> list[dict]:
        sorted_users = sorted(self._puzzles_points.items(), key=lambda x: x[1], reverse=True)[:limit]
        res = []
        for uid, pts in sorted_users:
            user_data = self.get_user(uid)
            res.append({
                "user_id": uid,
                "first_name": user_data.get("first_name", "Someone"),
                "username": user_data.get("username", ""),
                "puzzles_points": pts
            })
        return res

    def increment_rps_wins(self, user_id: int) -> None:
        self._rps_wins[user_id] = self._rps_wins.get(user_id, 0) + 1

    def update_coin_streak(self, user_id: int, correct: bool) -> int:
        if correct:
            self._coin_streak[user_id] = self._coin_streak.get(user_id, 0) + 1
            if self._coin_streak[user_id] > self._max_coin_streak.get(user_id, 0):
                self._max_coin_streak[user_id] = self._coin_streak[user_id]
        else:
            self._coin_streak[user_id] = 0
        return self._coin_streak.get(user_id, 0)


_mem = MemoryStore()


# ── MongoDB wrapper ───────────────────────────────────────────────────────────

class Database:
    """
    Async database interface.
    Uses MongoDB when available, falls back to MemoryStore silently.
    """

    def __init__(self):
        self.is_connected: bool = False
        self._client = None
        self._db = None

    async def connect(self) -> None:
        if not Config.MONGO_URL:
            log.warning("MONGO_URL not set — using in-memory storage")
            return

        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            self._client = AsyncIOMotorClient(
                Config.MONGO_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            # Verify connection
            await self._client.admin.command("ping")
            self._db = self._client[Config.DB_NAME]
            self.is_connected = True

            # Create indexes
            await self._db.memory.create_index("chat_id")
            await self._db.users.create_index("user_id", unique=True)
            await self._db.sizu_admins.create_index("user_id", unique=True)

            # Sync sizu admins to memory
            cursor = self._db.sizu_admins.find({}, {"user_id": 1})
            async for doc in cursor:
                _mem.add_sizu_admin(doc["user_id"])

            log.info("MongoDB connected successfully")
        except Exception as e:
            log.warning(f"MongoDB connection failed: {e} — using in-memory fallback")
            self.is_connected = False

    # ── Chat Memory ───────────────────────────────────────────────────────

    async def save_chat_history(self, chat_id: int, role: str, content: str) -> None:
        _mem.save_message(chat_id, role, content, Config.MAX_MEMORY)
        if not self.is_connected:
            return
        try:
            await self._db.memory.update_one(
                {"chat_id": chat_id},
                {
                    "$push": {
                        "history": {
                            "$each": [{"role": role, "content": content}],
                            "$slice": -Config.MAX_MEMORY,
                        }
                    }
                },
                upsert=True,
            )
        except Exception as e:
            log.debug(f"save_chat_history error: {e}")

    async def get_chat_history(self, chat_id: int) -> list[dict]:
        if not self.is_connected:
            return _mem.get_history(chat_id)
        try:
            doc = await self._db.memory.find_one({"chat_id": chat_id})
            return doc.get("history", []) if doc else []
        except Exception:
            return _mem.get_history(chat_id)

    async def clear_chat_history(self, chat_id: int) -> None:
        _mem.clear_history(chat_id)
        if not self.is_connected:
            return
        try:
            await self._db.memory.delete_one({"chat_id": chat_id})
        except Exception as e:
            log.debug(f"clear_chat_history error: {e}")

    async def count_memories(self) -> int:
        if not self.is_connected:
            return len(_mem._memory)
        try:
            return await self._db.memory.count_documents({})
        except Exception:
            return len(_mem._memory)

    # ── Users ─────────────────────────────────────────────────────────────

    async def upsert_user(self, user_id: int, first_name: str, username: str = "") -> None:
        data = {"user_id": user_id, "first_name": first_name, "username": username}
        _mem.upsert_user(user_id, data)
        if not self.is_connected:
            return
        try:
            await self._db.users.update_one(
                {"user_id": user_id},
                {"$set": data},
                upsert=True,
            )
        except Exception as e:
            log.debug(f"upsert_user error: {e}")

    async def warn_user(self, user_id: int) -> int:
        user_data = _mem._users.setdefault(user_id, {"user_id": user_id, "first_name": "Someone", "username": ""})
        user_data["warnings"] = user_data.get("warnings", 0) + 1
        
        if not self.is_connected:
            return user_data["warnings"]
            
        try:
            from pymongo import ReturnDocument
            doc = await self._db.users.find_one_and_update(
                {"user_id": user_id},
                {"$inc": {"warnings": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            return doc.get("warnings", 0) if doc else user_data["warnings"]
        except Exception as e:
            log.debug(f"warn_user error: {e}")
            return user_data["warnings"]

    async def get_warnings(self, user_id: int) -> int:
        if not self.is_connected:
            return _mem.get_user(user_id).get("warnings", 0)
        try:
            doc = await self._db.users.find_one({"user_id": user_id})
            return doc.get("warnings", 0) if doc else 0
        except Exception:
            return _mem.get_user(user_id).get("warnings", 0)

    async def count_users(self) -> int:
        if not self.is_connected:
            return _mem.count_users()
        try:
            return await self._db.users.count_documents({})
        except Exception:
            return _mem.count_users()

    async def all_user_ids(self) -> list[int]:
        if not self.is_connected:
            return _mem.all_user_ids()
        try:
            cursor = self._db.users.find({}, {"user_id": 1})
            return [doc["user_id"] async for doc in cursor]
        except Exception:
            return _mem.all_user_ids()

    # ── Sizu Admins ────────────────────────────────────────────────────────
    async def add_sizu_admin(self, user_id: int) -> None:
        _mem.add_sizu_admin(user_id)
        if not self.is_connected:
            return
        try:
            await self._db.sizu_admins.update_one(
                {"user_id": user_id},
                {"$set": {"user_id": user_id, "added_at": time.time()}},
                upsert=True
            )
        except Exception as e:
            log.debug(f"add_sizu_admin error: {e}")

    async def remove_sizu_admin(self, user_id: int) -> bool:
        mem_res = _mem.remove_sizu_admin(user_id)
        if not self.is_connected:
            return mem_res
        try:
            result = await self._db.sizu_admins.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            log.debug(f"remove_sizu_admin error: {e}")
            return mem_res

    async def is_sizu_admin(self, user_id: int) -> bool:
        if not self.is_connected:
            return _mem.is_sizu_admin(user_id)
        try:
            doc = await self._db.sizu_admins.find_one({"user_id": user_id})
            return doc is not None
        except Exception:
            return _mem.is_sizu_admin(user_id)

    async def get_sizu_admins(self) -> list[int]:
        if not self.is_connected:
            return _mem.get_sizu_admins()
        try:
            cursor = self._db.sizu_admins.find({}, {"user_id": 1})
            return [doc["user_id"] async for doc in cursor]
        except Exception:
            return _mem.get_sizu_admins()

    # ── Welcome ───────────────────────────────────────────────────────────

    async def set_welcome(self, chat_id: int, text: str) -> None:
        _mem.set_welcome(chat_id, text)
        if not self.is_connected:
            return
        try:
            await self._db.chats.update_one(
                {"chat_id": chat_id},
                {"$set": {"welcome": text}},
                upsert=True,
            )
        except Exception as e:
            log.debug(f"set_welcome error: {e}")

    async def get_welcome(self, chat_id: int) -> Optional[str]:
        if not self.is_connected:
            return _mem.get_welcome(chat_id)
        try:
            doc = await self._db.chats.find_one({"chat_id": chat_id})
            return doc.get("welcome") if doc else None
        except Exception:
            return _mem.get_welcome(chat_id)

    # ── Game Stats ────────────────────────────────────────────────────────

    async def update_game_stats(self, user_id: int, game: str, result: str) -> None:
        _mem.update_stats(user_id, game, result)
        if not self.is_connected:
            return
        try:
            await self._db.users.update_one(
                {"user_id": user_id},
                {"$inc": {f"game_stats.{game}.{result}": 1}},
                upsert=True,
            )
        except Exception as e:
            log.debug(f"update_game_stats error: {e}")

    async def get_game_stats(self, user_id: int) -> dict:
        if not self.is_connected:
            return _mem.get_stats(user_id)
        try:
            doc = await self._db.users.find_one({"user_id": user_id})
            return doc.get("game_stats", {}) if doc else {}
        except Exception:
            return _mem.get_stats(user_id)

    # ── Game States Persistence ───────────────────────────────────────────

    async def save_game_state(self, chat_id: int, game_type: str, state: dict) -> None:
        _mem.save_game_state(chat_id, game_type, state)
        if not self.is_connected:
            return
        try:
            await self._db.games_state.update_one(
                {"chat_id": chat_id, "game_type": game_type},
                {"$set": {"state": state}},
                upsert=True
            )
        except Exception as e:
            log.debug(f"save_game_state error: {e}")

    async def get_game_state(self, chat_id: int, game_type: str) -> Optional[dict]:
        if not self.is_connected:
            return _mem.get_game_state(chat_id, game_type)
        try:
            doc = await self._db.games_state.find_one({"chat_id": chat_id, "game_type": game_type})
            return doc.get("state") if doc else None
        except Exception:
            return _mem.get_game_state(chat_id, game_type)

    async def clear_game_state(self, chat_id: int, game_type: str) -> None:
        _mem.clear_game_state(chat_id, game_type)
        if not self.is_connected:
            return
        try:
            await self._db.games_state.delete_one({"chat_id": chat_id, "game_type": game_type})
        except Exception as e:
            log.debug(f"clear_game_state error: {e}")

    # ── Game Scores Persistence ───────────────────────────────────────────

    async def add_puzzles_points(self, user_id: int, first_name: str, username: str, points: int) -> None:
        await self.upsert_user(user_id, first_name, username)
        _mem.add_puzzles_points(user_id, points)
        if not self.is_connected:
            return
        try:
            await self._db.users.update_one(
                {"user_id": user_id},
                {"$inc": {"puzzles_points": points}}
            )
        except Exception as e:
            log.debug(f"add_puzzles_points error: {e}")

    async def get_puzzles_top(self, limit: int = 10) -> list[dict]:
        if not self.is_connected:
            return _mem.get_puzzles_top(limit)
        try:
            cursor = self._db.users.find({"puzzles_points": {"$gt": 0}}).sort("puzzles_points", -1).limit(limit)
            return [
                {
                    "user_id": doc["user_id"],
                    "first_name": doc.get("first_name", "Someone"),
                    "username": doc.get("username", ""),
                    "puzzles_points": doc.get("puzzles_points", 0)
                }
                async for doc in cursor
            ]
        except Exception:
            return _mem.get_puzzles_top(limit)

    async def increment_rps_wins(self, user_id: int, first_name: str, username: str) -> None:
        await self.upsert_user(user_id, first_name, username)
        _mem.increment_rps_wins(user_id)
        if not self.is_connected:
            return
        try:
            await self._db.users.update_one(
                {"user_id": user_id},
                {"$inc": {"rps_wins": 1}}
            )
        except Exception as e:
            log.debug(f"increment_rps_wins error: {e}")

    async def update_coin_streak(self, user_id: int, first_name: str, username: str, correct: bool) -> int:
        await self.upsert_user(user_id, first_name, username)
        streak = _mem.update_coin_streak(user_id, correct)
        if not self.is_connected:
            return streak
        try:
            if correct:
                # Increment streak, then update max_streak if current streak is higher
                await self._db.users.update_one(
                    {"user_id": user_id},
                    {"$inc": {"coin_streak": 1}}
                )
                user_doc = await self._db.users.find_one({"user_id": user_id})
                curr_streak = user_doc.get("coin_streak", 0)
                max_streak = user_doc.get("max_coin_streak", 0)
                if curr_streak > max_streak:
                    await self._db.users.update_one(
                        {"user_id": user_id},
                        {"$set": {"max_coin_streak": curr_streak}}
                    )
                return curr_streak
            else:
                await self._db.users.update_one(
                    {"user_id": user_id},
                    {"$set": {"coin_streak": 0}}
                )
                return 0
        except Exception as e:
            log.debug(f"update_coin_streak error: {e}")
            return streak

    async def get_user_profile_stats(self, user_id: int) -> dict:
        if not self.is_connected:
            return {
                "puzzles_points": _mem._puzzles_points.get(user_id, 0),
                "rps_wins": _mem._rps_wins.get(user_id, 0),
                "coin_streak": _mem._coin_streak.get(user_id, 0),
                "max_coin_streak": _mem._max_coin_streak.get(user_id, 0),
            }
        try:
            doc = await self._db.users.find_one({"user_id": user_id}) or {}
            return {
                "puzzles_points": doc.get("puzzles_points", 0),
                "rps_wins": doc.get("rps_wins", 0),
                "coin_streak": doc.get("coin_streak", 0),
                "max_coin_streak": doc.get("max_coin_streak", 0),
            }
        except Exception:
            return {
                "puzzles_points": 0,
                "rps_wins": 0,
                "coin_streak": 0,
                "max_coin_streak": 0,
            }


# ── Singletons ────────────────────────────────────────────────────────────────
db = Database()
