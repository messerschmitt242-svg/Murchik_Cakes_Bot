
from database.db import get_conn, is_postgres


def _ensure():
    conn = get_conn()
    c = conn.cursor()
    if is_postgres():
        c.execute("""
        CREATE TABLE IF NOT EXISTS user_settings(
            user_id BIGINT PRIMARY KEY,
            language TEXT DEFAULT 'ua'
        )
        """)
    else:
        c.execute("""
        CREATE TABLE IF NOT EXISTS user_settings(
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'ua'
        )
        """)
    conn.commit()
    conn.close()


def get_user_language(user_id):
    _ensure()
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT language FROM user_settings WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row["language"] if row else "ua"


def set_user_language(user_id, language):
    _ensure()
    conn = get_conn()
    c = conn.cursor()
    if is_postgres():
        c.execute("""
        INSERT INTO user_settings(user_id, language)
        VALUES(?, ?)
        ON CONFLICT(user_id) DO UPDATE SET language = EXCLUDED.language
        """, (user_id, language))
    else:
        c.execute("""
        INSERT INTO user_settings(user_id, language)
        VALUES(?, ?)
        ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
        """, (user_id, language))
    conn.commit()
    conn.close()
