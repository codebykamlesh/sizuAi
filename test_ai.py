# test_models.py

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

MODELS = [
    "openai/gpt-oss-20b:free",
    "google/gemma-3n-e4b-it:free",
    "moonshotai/kimi-k2:free",
]

TEST_PROMPT = """
Explain Python async programming in under 100 words.
"""

results = []

for model in MODELS:
    print(f"\nTesting {model}")

    start = time.time()

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": TEST_PROMPT
                    }
                ],
                "temperature": 0.7,
            },
            timeout=60,
        )

        elapsed = round(time.time() - start, 2)

        if r.status_code != 200:
            print(f"❌ {r.status_code}")
            print(r.text[:200])

            results.append({
                "model": model,
                "success": False,
                "latency": elapsed,
            })

            continue

        data = r.json()

        text = (
            data["choices"][0]["message"]["content"]
            if data.get("choices")
            else ""
        )

        print(f"✅ {elapsed}s")
        print(text[:150])

        results.append({
            "model": model,
            "success": True,
            "latency": elapsed,
            "length": len(text),
        })

    except Exception as e:
        print("ERROR:", e)

        results.append({
            "model": model,
            "success": False,
            "latency": 999,
        })

print("\n========== RESULTS ==========")

working = [x for x in results if x["success"]]

working.sort(key=lambda x: x["latency"])

for item in working:
    print(
        f"{item['model']} | "
        f"{item['latency']}s | "
        f"{item.get('length',0)} chars"
    )
