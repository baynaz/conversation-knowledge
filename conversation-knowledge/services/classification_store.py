from psycopg2.extras import RealDictCursor
from db.connection import get_db_connection

INSERT_CLASSIFICATION = """
INSERT INTO classified_messages (raw_message_id, role, confidence)
VALUES (%s, %s, %s)
RETURNING id, raw_message_id, role, confidence;
"""


def store_classification(raw_message_id: str, role: str, confidence: float) -> dict:
    """Persists the classification result for a raw message."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                INSERT_CLASSIFICATION,
                (raw_message_id, role, confidence),
            )
            row = cur.fetchone()
    return dict(row)