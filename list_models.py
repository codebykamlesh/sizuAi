import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

r = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={
        "Authorization": f"Bearer {api_key}"
    }
)

data = r.json()

free_models = []

for model in data["data"]:
    model_id = model["id"]

    if ":free" in model_id:
        free_models.append(model_id)

print(f"\nFound {len(free_models)} free models:\n")

for m in sorted(free_models):
    print(m)
