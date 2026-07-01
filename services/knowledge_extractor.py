import json
import re
import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

EXTRACTION_PROMPT = """You are analyzing an IT conversation thread. Extract structured knowledge from it.

Return ONLY a valid JSON object, with no preamble, no markdown formatting, no explanation. The JSON must have exactly these fields:

{{
  "problem": "one sentence describing the core problem reported",
  "context": "relevant context like software, OS, or environment mentioned",
  "symptoms": ["list", "of", "observed", "symptoms"],
  "solutions_tried": ["list", "of", "things", "that", "were", "tried"],
  "confirmed_solution": "the specific action that actually fixed the problem, or null if not resolved",
  "technology": "the main technology/product involved, e.g. VPN, AnyConnect, Outlook"
}}

If the thread does not contain a clear confirmed resolution, set "confirmed_solution" to null. Do not invent information that isn't in the conversation.

Conversation thread:
{thread_text}
"""


def _extract_json(raw_text: str) -> dict:
    """Ollama sometimes wraps JSON in markdown fences or adds stray text. Strip that."""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    # If there's still leading/trailing noise, grab the outermost {...}
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model output: {raw_text!r}")
    return json.loads(match.group(0))


def extract_knowledge(thread_id: str, thread_text: str) -> dict:
    """Calls Ollama (mistral) with the thread text and returns a structured knowledge dict."""
    prompt = EXTRACTION_PROMPT.format(thread_text=thread_text)

    response = httpx.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        },
        timeout=120.0,
    )
    response.raise_for_status()
    raw_output = response.json()["response"]

    parsed = _extract_json(raw_output)
    parsed["thread_id"] = thread_id
    return parsed