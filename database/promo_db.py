from database.db import get_conn, is_postgres

ALLOWED_DISCOUNTS = (10, 20)


def create_promo(code: str, discount_percent: int, product_id: int | None = None) -> bool:
    code = (code or "").strip().upper()
    if discount_percent not in ALLOWED_DISCOUNTS or not code:
        return False
    conn = get_conn()
    cursor = conn.cursor()
    if is_postgres():
        cursor.execute(
            """
            INSERT INTO promo_codes (code, discount_percent, is_active, product_id)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(code) DO UPDATE SET
                discount_percent = EXCLUDED.discount_percent,
                is_active = 1,
                product_id = EXCLUDED.product_id
            """,
            (code, discount_percent, product_id),
        )
    else:
        cursor.execute(
            """
            INSERT OR REPLACE INTO promo_codes (code, discount_percent, is_active, product_id)
            VALUES (?, ?, 1, ?)
            """,
            (code, discount_percent, product_id),
        )
    conn.commit()
    conn.close()
    return True


def get_promo(code: str, product_id: int | None = None):
    code = (code or "").strip().upper()
    conn = get_conn()
    cursor = conn.cursor()
    if product_id is None:
        cursor.execute(
            """
            SELECT code, discount_percent, is_active, product_id
            FROM promo_codes
            WHERE code = ? AND is_active = 1 AND product_id IS NULL
            """,
            (code,),
        )
    else:
        cursor.execute(
            """
            SELECT code, discount_percent, is_active, product_id
            FROM promo_codes
            WHERE code = ? AND is_active = 1 AND (product_id IS NULL OR product_id = ?)
            ORDER BY CASE WHEN product_id = ? THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (code, product_id, product_id),
        )
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_promos():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT pc.code, pc.discount_percent, pc.is_active, pc.created_at,
               pc.product_id, p.name AS product_name
        FROM promo_codes pc
        LEFT JOIN products p ON p.id = pc.product_id
        ORDER BY pc.created_at DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
