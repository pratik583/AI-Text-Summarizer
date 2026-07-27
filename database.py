import sqlite3
from contextlib import contextmanager

DB_PATH = "history.db"


def init_db():
    """Create the history table if it doesn't already exist."""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                summary_text TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def save_summary(original_text: str, summary_text: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO history (original_text, summary_text) VALUES (?, ?)",
            (original_text, summary_text),
        )
        conn.commit()


def get_recent(limit: int = 5):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return rows


def clear_history():
    with get_conn() as conn:
        conn.execute("DELETE FROM history")
        conn.commit()
