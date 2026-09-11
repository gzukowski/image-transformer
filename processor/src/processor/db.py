import os
from collections.abc import Generator
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


@contextmanager
def _connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """A short-lived connection per call, so a stale/dropped connection between
    messages (this worker polls SQS and may sit idle for long stretches) never
    breaks the next update.
    """
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME
    )
    try:
        yield conn
    finally:
        conn.close()


def mark_processing(upload_id: str) -> None:
    with _connection() as conn, conn.cursor() as cur:
        cur.execute("UPDATE uploads SET status = 'processing' WHERE id = %s", (upload_id,))
        conn.commit()


def mark_done(upload_id: str, thumbnail_key: str) -> None:
    with _connection() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE uploads SET status = 'done', thumbnail_url = %s WHERE id = %s",
            (thumbnail_key, upload_id),
        )
        conn.commit()


def mark_failed(upload_id: str) -> None:
    with _connection() as conn, conn.cursor() as cur:
        cur.execute("UPDATE uploads SET status = 'failed' WHERE id = %s", (upload_id,))
        conn.commit()
