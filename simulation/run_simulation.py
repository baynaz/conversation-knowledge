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

    with httpx.Client(timeout=120.0) as client:
        print("-> resetting database...")
        client.post(f"{FASTAPI_BASE}/dev/reset")
        print("   done\n")

        for msg in messages:
            label = f"[{msg['id']}] {msg['author']}: {msg['content'][:50]}"
            print(f"-> {label}")
            response = client.post(f"{FASTAPI_BASE}/ingest/teams", json=msg)
            response.raise_for_status()
            result = response.json()

            # show what the pipeline did with this message
            print(f"   author stored      : {result['author_stored']}")
            print(f"   role               : {result['role']} (confidence={result['confidence']:.2f})")
            if result.get("extraction_triggered"):
                print(f"   extraction         : AUTO-TRIGGERED ✓")
            print()
            time.sleep(0.3)


if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "happy_path"
    simulate(scenario)