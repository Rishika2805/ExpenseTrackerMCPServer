import os
from dotenv import load_dotenv
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL
)


def get_connection():
    return pool.getconn()


def release_connection(conn):
    pool.putconn(conn)


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