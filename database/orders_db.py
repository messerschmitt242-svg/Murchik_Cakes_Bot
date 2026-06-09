import json
from database.db import get_conn

STATUSES = [
    "Прийнято",
    "Готується",
    "Готове до видачі",
    "Завершено",
    "Скасовано",
]
FINAL_STATUSES = ("Завершено", "Скасовано")


def create_order(user_id: int, name: str, phone: str, items: list[dict], total: float) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO orders (user_id, name, phone, items, total, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, phone, json.dumps(items, ensure_ascii=False), total, "Прийнято"),
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id


def get_user_orders(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, items, total, status, created_at
        FROM orders
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_orders(limit: int | None = None, offset: int = 0):
    conn = get_conn()
    cursor = conn.cursor()
    sql = """
        SELECT id, user_id, name, phone, items, total, status, created_at
        FROM orders
        ORDER BY id DESC
    """
    params = []
    if limit is not None:
        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def count_all_orders() -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS cnt FROM orders")
    count = int(cursor.fetchone()["cnt"])
    conn.close()
    return count


def get_active_orders():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, phone, items, total, status, created_at
        FROM orders
        WHERE status NOT IN ('Завершено', 'Скасовано')
        ORDER BY id DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_order(order_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, phone, items, total, status, created_at
        FROM orders
        WHERE id = ?
        """,
        (order_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def update_order_status(order_id: int, status: str) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def delete_cancelled_order(order_id: int) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ? AND status = 'Скасовано'", (order_id,))
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def next_status(current_status: str):
    if current_status == "Прийнято":
        return "Готується", "👩‍🍳 Готується"
    if current_status == "Готується":
        return "Готове до видачі", "✅ Готове до видачі"
    if current_status == "Готове до видачі":
        return "Завершено", "🏁 Завершено"
    return None, None


def format_items(raw_items: str) -> str:
    try:
        items = json.loads(raw_items or "[]")
    except Exception:
        return raw_items or "—"
    if not items:
        return "—"
    result = []
    for item in items:
        line = f"• {item.get('name', 'Товар')} x{item.get('qty', 1)} — {item.get('final_subtotal', item.get('subtotal', 0)):.2f} zł"
        if item.get("promo_code"):
            line += f"\n  промо: {item.get('promo_code')} (-{item.get('discount_percent', 0)}%)"
        result.append(line)
    return "\n".join(result)
