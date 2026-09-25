from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor

from models.schemas import TeamsMessage
from db.connection import get_db_connection
from services.anonymizer import anonymize_message
from services.classifier import is_reply, classify_role
from services.classification_store import store_classification
from services.thread_router import route_known_thread, thread_has_knowledge_object
from services.thread_builder import build_thread, thread_to_text
from services.knowledge_extractor import extract_knowledge
from services.knowledge_store import store_knowledge_object, upsert_knowledge_object
from services.embedding_service import embed_knowledge_object
from services.qdrant_service import index_knowledge_object

app = FastAPI(title="conversation-knowledge")

INSERT_THREAD = """
INSERT INTO threads (id) VALUES (%s) ON CONFLICT (id) DO NOTHING;
"""

INSERT_MESSAGE = """
INSERT INTO raw_messages (thread_id, source_message_id, parent_message_id, author, timestamp, content, channel)
VALUES (%s, %s,
    (SELECT id FROM raw_messages WHERE source_message_id = %s),
    %s, %s, %s, %s)
RETURNING id;
"""


def _run_extraction(thread_id: str) -> dict:
    """Shared extraction logic — used by auto-trigger and manual endpoint."""
    messages = build_thread(thread_id)
    thread_text = thread_to_text(messages)
    knowledge = extract_knowledge(thread_id, thread_text)

    already_exists = thread_has_knowledge_object(thread_id)
    stored = (
        upsert_knowledge_object(knowledge)
        if already_exists
        else store_knowledge_object(knowledge)
    )

    vector = embed_knowledge_object(stored)
    index_knowledge_object(stored, vector)
    return stored


@app.post("/dev/reset")
def reset_db():
    """Wipes all tables. Dev only — never expose in production."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                TRUNCATE threads, raw_messages, classified_messages, knowledge_objects
                RESTART IDENTITY CASCADE;
            """)
    return {"status": "reset"}


@app.post("/ingest/teams")
def ingest_teams_message(message: TeamsMessage):

    # STEP 1 — anonymize first, everything downstream uses anon
    anon = anonymize_message(message.model_dump())

    # STEP 2 — route to correct thread via replyToId
    resolved_thread_id = message.thread_id
    if is_reply(anon):
        routed = route_known_thread(message.parent_message_id)
        if routed:
            resolved_thread_id = routed

    # STEP 3 — store anonymized message in DB
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(INSERT_THREAD, (resolved_thread_id,))
            cur.execute(
                INSERT_MESSAGE,
                (
                    resolved_thread_id,
                    message.id,
                    message.parent_message_id,
                    anon["author"],     # anonymized author
                    message.timestamp,
                    anon["content"],    # anonymized message content
                    message.channel,
                ),
            )
            row = cur.fetchone()

    raw_message_id = str(row["id"])

    # STEP 4 — classify anonymized content
    classification = classify_role(anon["content"])
    role = classification["role"]
    confidence = classification["confidence"]

    # STEP 5 — store classification
    store_classification(raw_message_id, role, confidence)

    # STEP 6 — auto-trigger extraction if confirmed
    extraction_triggered = False
    if role == "confirmation":
        try:
            _run_extraction(resolved_thread_id)
            extraction_triggered = True
        except Exception as e:
            print(f"[warn] extraction failed for {resolved_thread_id}: {e}")

    return {
        "status": "stored",
        "message_id": raw_message_id,
        "thread_id": resolved_thread_id,
        "author_stored": anon["author"],
        "role": role,
        "confidence": confidence,
        "extraction_triggered": extraction_triggered,
    }


@app.post("/extract-knowledge/{thread_id}")
def extract_knowledge_for_thread(thread_id: str):
    """Manual extraction trigger — useful for dev and testing."""
    messages = build_thread(thread_id)
    if not messages:
        raise HTTPException(
            status_code=404, detail=f"Thread '{thread_id}' not found"
        )
    try:
        stored = _run_extraction(thread_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"LLM extraction failed: {e}"
        )
    return stored