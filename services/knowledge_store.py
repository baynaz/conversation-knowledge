import json
from psycopg2.extras import RealDictCursor
from db.connection import get_db_connection

INSERT_KNOWLEDGE_OBJECT = """
INSERT INTO knowledge_objects (thread_id, problem, context, symptoms, solutions_tried, confirmed_solution, technology)
VALUES (%s, %s, %s, %s, %s, %s, %s)
RETURNING id, thread_id, problem, context, symptoms, solutions_tried, confirmed_solution, technology, created_at;
"""


def store_knowledge_object(knowledge: dict) -> dict:
    """Persists a knowledge dict (as returned by extract_knowledge) into knowledge_objects."""
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