from psycopg2.extras import RealDictCursor
from db.connection import get_db_connection

FIND_THREAD_BY_SOURCE_ID = """
SELECT thread_id
FROM raw_messages
WHERE source_message_id = %s
LIMIT 1;
"""

CHECK_KNOWLEDGE_EXISTS = """
SELECT id FROM knowledge_objects
WHERE thread_id = %s
LIMIT 1;
"""


def route_known_thread(parent_message_id: str) -> str | None:
    """Given a replyToId (source message id), returns the thread_id it belongs to.

    Returns None if the parent message is not found — caller should handle
    this as an unroutable message (out of scope until Sprint 4).
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(FIND_THREAD_BY_SOURCE_ID, (parent_message_id,))
            row = cur.fetchone()

    if row is None:
        return None
    return row["thread_id"]


def thread_has_knowledge_object(thread_id: str) -> bool:
    """Returns True if this thread already has an extracted knowledge object."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(CHECK_KNOWLEDGE_EXISTS, (thread_id,))
            row = cur.fetchone()
    return row is not None