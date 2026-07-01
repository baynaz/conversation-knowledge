import json
import sys
import time
from pathlib import Path

import httpx

FASTAPI_BASE = "http://localhost:8000"
SCENARIOS_DIR = Path(__file__).parent / "scenarios"


def load_scenario(name: str) -> list[dict]:
    path = SCENARIOS_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"No scenario file at {path}")
    return json.loads(path.read_text())


def simulate(scenario_name: str) -> None:
    messages = load_scenario(scenario_name)
    thread_ids_seen = set()

    with httpx.Client(timeout=120.0) as client:
        # wipe before each simulation run so we always start clean
        print(" resetting database...")
        client.post(f"{FASTAPI_BASE}/dev/reset")
        print(" done\n")

        for msg in messages:
            print(f"-> sending [{msg['id']}] {msg['author']}: {msg['content'][:60]}")
            response = client.post(f"{FASTAPI_BASE}/ingest/teams", json=msg)
            response.raise_for_status()
            print(f"   {response.status_code} {response.json()}")
            thread_ids_seen.add(msg["thread_id"])
            time.sleep(0.3)

        print("\n--- triggering extraction for each thread seen ---")
        for thread_id in thread_ids_seen:
            print(f"-> extracting knowledge for thread '{thread_id}'")
            response = client.post(f"{FASTAPI_BASE}/extract-knowledge/{thread_id}")
            if response.status_code != 200:
                print(f"   FAILED [{response.status_code}]: {response.text}")
                continue
            print(f"   {json.dumps(response.json(), indent=2, default=str)}")


if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "happy_path"
    simulate(scenario)