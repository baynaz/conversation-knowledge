import json
import re
import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

CLASSIFICATION_PROMPT = """You are classifying a single message from a chat thread.

Classify the message into exactly one of these roles:
- "question"      : the user is reporting a problem or asking for help
- "answer"        : someone is suggesting a solution or giving instructions
- "confirmation"  : the user confirms that a solution worked and the problem is resolved
- "noise"         : off-topic, acknowledgement without confirmation, or not relevant (e.g. "ok", "thanks", "let me check")

Return ONLY a valid JSON object with no preamble, no markdown, no explanation:
{{
  "role": "<one of: question | answer | confirmation | noise>",
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<one short sentence explaining why>"
}}

Important rules:
- "confirmation" means the problem is SOLVED. The user must clearly state it worked or is fixed.
- A vague "ok" or "thanks" alone is "noise", NOT confirmation.
- If unsure between confirmation and noise, choose noise.

Message to classify:
\"{content}\"
"""


def is_reply(message: dict) -> bool:
    """Rule-based check — no LLM needed. A message is a reply if it has a parent."""
    return message.get("parent_message_id") is not None


def _parse_classification(raw: str) -> dict:
    """Strips markdown fences and parses the JSON classification response."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in classification response: {raw!r}")
    return json.loads(match.group(0))


def classify_role(content: str) -> dict:
    """Calls Ollama (mistral) to classify the role of a single message.

    Returns a dict with keys: role, confidence, reasoning.
    Falls back to role='noise' with confidence=0.0 if the LLM call fails,
    so a transient error never blocks the ingestion pipeline.
    """
    prompt = CLASSIFICATION_PROMPT.format(content=content.replace('"', '\\"'))

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0},  # deterministic for classification
            },
            timeout=60.0,
        )
        response.raise_for_status()
        raw_output = response.json()["response"]
        return _parse_classification(raw_output)

    except Exception as e:
        # fail open: store as noise so the pipeline keeps moving
        return {
            "role": "noise",
            "confidence": 0.0,
            "reasoning": f"classification failed: {e}",
        }