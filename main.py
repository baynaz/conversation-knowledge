from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from datetime import datetime
import uuid
from uuid import uuid4
from psycopg2 import connect
import json

from models.schemas import TeamsMessage
from services.thread_builder import build_thread
from services.knowledge_extractor import extract_knowledge


app = FastAPI()


# DB connection
conn = psycopg2.connect(
    dbname="knowledge_db",
    user="admin",
    password="admin",
    host="localhost",
    port="5432"
)


@app.get("/")
def root():
    return {"status": "running"}

@app.post("/ingest/teams")
def ingest_message(msg: TeamsMessage):
    cur = conn.cursor()

    query = """
    INSERT INTO raw_messages
    (id, thread_id, parent_message_id, author, timestamp, content, channel)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    cur.execute(query, (
        str(uuid.uuid4()),
        msg.thread_id,
        msg.parent_message_id,
        msg.author,
        msg.timestamp,
        msg.content,
        msg.channel
    ))

    conn.commit()
    cur.close()

    return {"status": "stored"}
 

@app.post("/extract-knowledge/{thread_id}")
def extract_thread_knowledge(thread_id: str):

    # Build thread
    thread_text = build_thread(conn, thread_id)

    if not thread_text:
        return {
            "error": "Thread not found"
        }

    # LLM extraction
    knowledge = extract_knowledge(thread_text)

    if "error" in knowledge:
        return knowledge

    # Store result
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO knowledge_objects (
            id,
            thread_id,
            problem,
            context,
            symptoms,
            solutions_tried,
            confirmed_solution,
            technology
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        str(uuid4()),
        thread_id,
        knowledge.get("problem"),
        knowledge.get("context"),
        json.dumps(knowledge.get("symptoms", [])),
        json.dumps(knowledge.get("solutions_tried", [])),
        knowledge.get("confirmed_solution"),
        knowledge.get("technology")
    ))

    conn.commit()
    cur.close()

    return knowledge
