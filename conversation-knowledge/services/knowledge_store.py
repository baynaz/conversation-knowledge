import json
from psycopg2.extras import RealDictCursor
from db.connection import get_db_connection

INSERT_KNOWLEDGE_OBJECT = """
INSERT INTO knowledge_objects (thread_id, problem, context, symptoms, solutions_tried, confirmed_solution, technology)
VALUES (%s, %s, %s, %s, %s, %s, %s)
RETURNING id, thread_id, problem, context, symptoms, solutions_tried, confirmed_solution, technology, created_at;
"""

UPSERT_KNOWLEDGE_OBJECT = """
UPDATE knowledge_objects
SET
    problem             = %s,
    context             = %s,
    symptoms            = %s,
    solutions_tried     = %s,
    confirmed_solution  = %s,
    technology          = %s
WHERE thread_id = %s
RETURNING id, thread_id, problem, context, symptoms, solutions_tried, confirmed_solution, technology, created_at;
"""


def store_knowledge_object(knowledge: dict) -> dict:
    """Inserts a new knowledge object. Use for threads with no prior extraction."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                INSERT_KNOWLEDGE_OBJECT,
                (
                    knowledge["thread_id"],
                    knowledge.get("problem"),
                    knowledge.get("context"),
                    json.dumps(knowledge.get("symptoms", [])),
                    json.dumps(knowledge.get("solutions_tried", [])),
                    knowledge.get("confirmed_solution"),
                    knowledge.get("technology"),
                ),
            )
            row = cur.fetchone()
    return dict(row)


def upsert_knowledge_object(knowledge: dict) -> dict:
    """Updates an existing knowledge object in place (for reopened threads)."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                UPSERT_KNOWLEDGE_OBJECT,
                (
                    knowledge.get("problem"),
                    knowledge.get("context"),
                    json.dumps(knowledge.get("symptoms", [])),
                    json.dumps(knowledge.get("solutions_tried", [])),
                    knowledge.get("confirmed_solution"),
                    knowledge.get("technology"),
                    knowledge["thread_id"],
                ),
            )
            row = cur.fetchone()
    return dict(row)