from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor

from models.schemas import TeamsMessage
from db.connection import get_db_connection
from services.thread_builder import build_thread, thread_to_text
from services.knowledge_extractor import extract_knowledge
from services.knowledge_store import store_knowledge_object
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


@app.post("/ingest/teams")
def ingest_teams_message(message: TeamsMessage):
    """Stores a raw Teams message. parent_message_id in the payload is the
    SOURCE id of the parent (e.g. 'msg_001'); we resolve it to our internal
    UUID via source_message_id.
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(INSERT_THREAD, (message.thread_id,))
            cur.execute(
                INSERT_MESSAGE,
                (
                    message.thread_id,
                    message.id,
                    message.parent_message_id,
                    message.author,
                    message.timestamp,
                    message.content,
                    message.channel,
                ),
            )
            row = cur.fetchone()

    return {"status": "stored", "message_id": str(row["id"])}


@app.post("/extract-knowledge/{thread_id}")
def extract_knowledge_for_thread(thread_id: str):
    """Runs the full extraction pipeline for a thread: reconstruct -> extract -> store -> embed -> index."""
    messages = build_thread(thread_id)
    if not messages:
        raise HTTPException(status_code=404, detail=f"Thread '{thread_id}' not found")

    thread_text = thread_to_text(messages)

    try:
        knowledge = extract_knowledge(thread_id, thread_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM extraction failed: {e}")

    stored = store_knowledge_object(knowledge)
    vector = embed_knowledge_object(stored)
    index_knowledge_object(stored, vector)

    return stored


@app.post("/dev/reset")
def reset_db():
    """Wipes all tables. Dev only — never expose this in production."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                TRUNCATE threads, raw_messages, classified_messages, knowledge_objects
                RESTART IDENTITY CASCADE;
            """)
    return {"status": "reset"}