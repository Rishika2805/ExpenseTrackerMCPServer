import os
from dotenv import load_dotenv
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

_pool = None


def get_pool():
    global _pool

    if _pool is None:
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL
        )

    return _pool


def get_connection():
    return get_pool().getconn()


def release_connection(conn):
    get_pool().putconn(conn)


def execute_query(query, params=None, fetch=False, fetchone=False):
    conn = get_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)

            result = None

            if fetch:
                result = cur.fetchall()
            elif fetchone:
                result = cur.fetchone()

            conn.commit()
            return result

    except Exception:
        conn.rollback()
        raise

    finally:
        release_connection(conn)