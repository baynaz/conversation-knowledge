# thread_id --> messages PostgreSQL --> texte complet du thread

def build_thread(conn, thread_id: str) -> str:
    """
    Reconstruct a conversation thread from PostgreSQL.
    """

    cur = conn.cursor()

    cur.execute("""
        SELECT author, content
        FROM raw_messages
        WHERE thread_id = %s
        ORDER BY timestamp
    """, (thread_id,))

    messages = cur.fetchall()

    cur.close()

    if not messages:
        return ""

    thread_text = ""

    for author, content in messages:
        thread_text += f"{author}: {content}\n"

    return thread_text
