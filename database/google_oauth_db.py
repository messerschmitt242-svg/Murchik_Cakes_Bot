from __future__ import annotations

from database.db import get_conn, is_postgres

SERVICE_TASKS = "google_tasks"


def save_google_refresh_token(refresh_token: str, account_email: str = "") -> None:
    conn = get_conn()
    cur = conn.cursor()
    if is_postgres():
        cur.execute(
            """
            INSERT INTO google_oauth_tokens (service, refresh_token, account_email, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (service) DO UPDATE SET
                refresh_token = EXCLUDED.refresh_token,
                account_email = EXCLUDED.account_email,
                updated_at = CURRENT_TIMESTAMP
            """,
            (SERVICE_TASKS, refresh_token, account_email or ""),
        )
    else:
        cur.execute(
            """
            INSERT OR REPLACE INTO google_oauth_tokens (service, refresh_token, account_email, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (SERVICE_TASKS, refresh_token, account_email or ""),
        )
    conn.commit()
    conn.close()


def get_google_refresh_token() -> str:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT refresh_token FROM google_oauth_tokens WHERE service = ?", (SERVICE_TASKS,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return ""
    try:
        return row["refresh_token"] or ""
    except Exception:
        return row[0] or ""


def get_google_tasks_status() -> dict:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT refresh_token, account_email, updated_at FROM google_oauth_tokens WHERE service = ?", (SERVICE_TASKS,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"connected": False, "account_email": "", "updated_at": ""}
    def val(key, idx):
        try:
            return row[key] or ""
        except Exception:
            return row[idx] or ""
    return {
        "connected": bool(val("refresh_token", 0)),
        "account_email": val("account_email", 1),
        "updated_at": str(val("updated_at", 2)),
    }
