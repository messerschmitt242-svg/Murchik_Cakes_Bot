
from database.db import get_conn, is_postgres


def create_promo(code: str, discount_percent: int) -> bool:
    code = code.strip().upper()
    if discount_percent not in (10, 20) or not code:
        return False

    conn = get_conn()
    cursor = conn.cursor()
    if is_postgres():
        cursor.execute(
            """
            INSERT INTO promo_codes (code, discount_percent, is_active)
            VALUES (?, ?, 1)
            ON CONFLICT(code) DO UPDATE SET discount_percent = EXCLUDED.discount_percent, is_active = 1
            """,
            (code, discount_percent),
        )
    else:
        cursor.execute(
            """
            INSERT OR REPLACE INTO promo_codes (code, discount_percent, is_active)
            VALUES (?, ?, 1)
            """,
            (code, discount_percent),
        )
    conn.commit()
    conn.close()
    return True


def get_promo(code: str):
    code = code.strip().upper()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT code, discount_percent, is_active
        FROM promo_codes
        WHERE code = ? AND is_active = 1
        """,
        (code,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_promos():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT code, discount_percent, is_active, created_at
        FROM promo_codes
        ORDER BY created_at DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
