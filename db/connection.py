import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DB_DSN = os.environ.get(
    "DATABASE_URL",
    # Default to the Postgres service defined in docker-compose.yml
    # (user: admin, password: admin, db: knowledge_db)
    "postgresql://admin:admin@localhost:5432/knowledge_db",
)


@contextmanager
def get_db_connection():
    """Yields a psycopg2 connection, committing on success and rolling back on error.

    Usage:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(...)
    """
    conn = psycopg2.connect(DB_DSN)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()