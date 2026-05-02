import sqlite3
import time
import uuid

DB = "sessions.db"


def init_db():

    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT,
            file_id TEXT,
            name TEXT,
            size INTEGER,
            created_at REAL
        )
    """)

    conn.commit()
    conn.close()


init_db()


def create_session():

    return str(uuid.uuid4())


def add_file(session_id, file_id, name, size):

    conn = sqlite3.connect(DB)

    conn.execute(
        """
        INSERT INTO sessions
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session_id,
            file_id,
            name,
            size,
            time.time()
        )
    )

    conn.commit()
    conn.close()


def get_files(session_id):

    conn = sqlite3.connect(DB)

    cursor = conn.execute(
        """
        SELECT file_id, name, size
        FROM sessions
        WHERE session_id = ?
        """,
        (session_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "file_id": r[0],
            "name": r[1],
            "size": r[2]
        }
        for r in rows
    ]


def delete_session(session_id):

    conn = sqlite3.connect(DB)

    conn.execute(
        "DELETE FROM sessions WHERE session_id = ?",
        (session_id,)
    )

    conn.commit()
    conn.close()


def cleanup_sessions():

    cutoff = time.time() - (24 * 60 * 60)

    conn = sqlite3.connect(DB)

    conn.execute(
        """
        DELETE FROM sessions
        WHERE created_at < ?
        """,
        (cutoff,)
    )

    conn.commit()
    conn.close()