"""Quick import test for all Sizu modules — runs inside asyncio context."""
import sys
import asyncio
sys.path.insert(0, ".")


async def run_tests():
    errors = []

    tests = [
        ("config", "from config import Config; assert Config.GEMINI_MODEL"),
        ("utils.logger", "from utils.logger import setup_logger; setup_logger('test')"),
        ("utils.helpers", "from utils.helpers import get_human_delay, parse_time, random_truth"),
        ("utils.decorators", "from utils.decorators import is_owner, is_sudo, is_group_admin"),
        ("database.mongo", "from database.mongo import db, MemoryStore; assert not db.is_connected"),
        ("core.rate_limiter", "from core.rate_limiter import rate_limiter; assert rate_limiter.is_allowed(12345)"),
        ("modules.keepalive", "from modules.keepalive import start_keepalive"),
        ("core.ai_engine", "from core.ai_engine import sizu_ai, detect_emotion, clean_response"),
        ("core.bot", "from core.bot import SizuBot"),
        ("plugins.start", "import plugins.start"),
        ("plugins.chat", "import plugins.chat"),
        ("plugins.games", "import plugins.games"),
        ("plugins.fun", "import plugins.fun"),
        ("plugins.welcome", "import plugins.welcome"),
        ("plugins.reactions", "import plugins.reactions"),
        ("plugins.admin", "import plugins.admin"),
    ]

    for name, code in tests:
        try:
            exec(code)
            print(f"  OK  {name}")
        except Exception as e:
            print(f"  ERR {name}: {e}")
            errors.append((name, str(e)))

    print()
    if errors:
        print(f"FAILED: {len(errors)} import(s) had errors")
        for n, e in errors:
            print(f"  - {n}: {e}")
        return False
    else:
        print("All modules imported successfully! Bot is ready. [PASS]")
        return True


if __name__ == "__main__":
    ok = asyncio.run(run_tests())
    sys.exit(0 if ok else 1)
