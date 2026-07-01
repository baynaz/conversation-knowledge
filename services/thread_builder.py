from psycopg2.extras import RealDictCursor
from db.connection import get_db_connection

RECURSIVE_THREAD_QUERY = """
WITH RECURSIVE thread_tree AS (
    SELECT id, author, content, parent_message_id, timestamp, 0 AS depth
    FROM raw_messages
    WHERE thread_id = %s AND parent_message_id IS NULL

    UNION ALL

    SELECT m.id, m.author, m.content, m.parent_message_id, m.timestamp, t.depth + 1
    FROM raw_messages m
    JOIN thread_tree t ON m.parent_message_id = t.id
)
SELECT * FROM thread_tree ORDER BY depth, timestamp;
"""


def build_thread(thread_id: str) -> list[dict]:
    """Reconstructs the full message tree for a thread, ordered root-first."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(RECURSIVE_THREAD_QUERY, (thread_id,))
            rows = cur.fetchall()
    return [dict(row) for row in rows]


def thread_to_text(messages: list[dict]) -> str:
    """Flattens a reconstructed thread into plain text for the LLM prompt."""
    lines = []
    for msg in messages:
        lines.append(f"{msg['author']}: {msg['content']}")
    return "\n".join(lines)