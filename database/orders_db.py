import json
from database.db import get_conn


def create_order(user_id: int, name: str, phone: str, items: list[dict], total: float) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (user_id, name, phone, items, total, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        name,
        phone,
        json.dumps(items, ensure_ascii=False),
        total,
        "Прийнято",
    ))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id


def get_user_orders(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, items, total, status, created_at
        FROM orders
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_orders():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, name, phone, items, total, status, created_at
        FROM orders
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_order_status(order_id: int, status: str) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def format_items(raw_items: str) -> str:
    try:
        items = json.loads(raw_items or "[]")
    except Exception:
        return raw_items or "—"

    if not items:
        return "—"

    return "\n".join(
        f"• {item.get('name', 'Товар')} x{item.get('qty', 1)} — {item.get('subtotal', 0):.2f} zł"
        for item in items
    )
