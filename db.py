import os
import atexit
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Tune min/max based on expected concurrency. For a small MCP server, 1-5 is plenty.
_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=5,
    dsn=DATABASE_URL,
    connect_timeout=10,
    # If using the transaction pooler (port 6543), keepalives help detect dead conns fast
    keepalives=1,
    keepalives_idle=30,
    keepalives_interval=10,
    keepalives_count=3,
)


@contextmanager
def get_connection():
    conn = _pool.getconn()
    try:
        yield conn
    finally:
        _pool.putconn(conn)


def execute_query(query, params=None, fetch=False, fetchone=False):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)

                if fetch:
                    result = cur.fetchall()
                elif fetchone:
                    result = cur.fetchone()
                else:
                    result = None

                conn.commit()
                return result
    except psycopg2.OperationalError as e:
        # Surface something useful instead of an empty error
        raise RuntimeError(
            f"Database connection failed. Check DATABASE_URL / network / pooler settings. "
            f"Original error: {e!r}"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {e!r}") from e


@atexit.register
def _close_pool():
    if _pool:
        _pool.closeall()