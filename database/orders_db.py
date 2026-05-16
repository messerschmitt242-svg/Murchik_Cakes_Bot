
import json
from database.db import get_conn, is_postgres

STATUSES = [
    "Прийнято",
    "Готується",
    "Готове до видачі",
    "Завершено",
    "Скасовано",
]


def create_order(
    user_id: int,
    name: str,
    phone: str,
    items: list[dict],
    total: float,
    order_date: str = "",
    delivery_method: str = "",
    payment_method: str = "",
    comment: str = "",
) -> int:
    conn = get_conn()
    cursor = conn.cursor()

    if is_postgres():
        cursor.execute(
            """
            INSERT INTO orders (user_id, name, phone, items, total, status, order_date, delivery_method, payment_method, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
            """,
            (
                user_id,
                name,
                phone,
                json.dumps(items, ensure_ascii=False),
                total,
                "Прийнято",
                order_date,
                delivery_method,
                payment_method,
                comment,
            ),
        )
        order_id = cursor.fetchone()["id"]
    else:
        cursor.execute(
            """
            INSERT INTO orders (user_id, name, phone, items, total, status, order_date, delivery_method, payment_method, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                name,
                phone,
                json.dumps(items, ensure_ascii=False),
                total,
                "Прийнято",
                order_date,
                delivery_method,
                payment_method,
                comment,
            ),
        )
        order_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return order_id


def get_user_orders(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, phone, items, total, status, order_date, delivery_method, payment_method, comment, created_at
        FROM orders
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_orders():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, phone, items, total, status, order_date, delivery_method, payment_method, comment, created_at
        FROM orders
        ORDER BY id DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_active_orders():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, phone, items, total, status, order_date, delivery_method, payment_method, comment, created_at
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
        SELECT id, user_id, name, phone, items, total, status, order_date, delivery_method, payment_method, comment, created_at
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


def next_status(current_status: str):
    if current_status == "Прийнято":
        return "Готується", "👩‍🍳 Готується"
    if current_status == "Готується":
        return "Готове до видачі", "✅ Готове до видачі"
    if current_status == "Готове до видачі":
        return "Завершено", "🏁 Завершено"
    return None, None


def can_cancel_order(status: str) -> bool:
    return status == "Прийнято"


def cancel_order(order_id: int) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET status = ? WHERE id = ? AND status = ?",
        ("Скасовано", order_id, "Прийнято"),
    )
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

    result = []
    for item in items:
        line = f"• {item.get('name', 'Товар')} ×{item.get('qty', 1)} — {item.get('final_subtotal', item.get('subtotal', 0)):.2f} zł"
        result.append(line)
    return "\n".join(result)


def _row_value(row, key: str, default=""):
    try:
        return row[key]
    except Exception:
        if isinstance(row, dict):
            return row.get(key, default)
        return default




def format_created_date(order) -> str:
    created_at = str(_row_value(order, "created_at") or "").strip()
    if not created_at:
        return ""
    if len(created_at) >= 10 and created_at[4:5] == "-" and created_at[7:8] == "-":
        return created_at[:10]
    return created_at


def format_order_meta(order) -> str:
    lines = []
    status = _row_value(order, "status")
    created_date = format_created_date(order)
    order_date = _row_value(order, "order_date")
    delivery_method = _row_value(order, "delivery_method")
    payment_method = _row_value(order, "payment_method")
    total = float(_row_value(order, "total", 0) or 0)
    comment = _row_value(order, "comment")

    if status:
        lines.append(f"📊 Статус: {status}")
    if created_date:
        lines.append(f"📅 Дата замовлення: {created_date}")
    if order_date:
        lines.append("")
        lines.append(f"📅 На коли: {order_date}")
    if delivery_method:
        lines.append(f"🚚 Спосіб доставки: {delivery_method}")
    if payment_method:
        lines.append(f"💳 Оплата: {payment_method}")
    lines.append(f"💰 Разом: {total:.2f} zł")
    if comment:
        lines.append(f"💬 Коментар: {comment}")
    return "\n".join(lines)


def format_items_section(raw_items: str) -> str:
    return "────────────\n" + format_items(raw_items)

def format_order_details(order) -> str:
    lines = []
    order_date = _row_value(order, "order_date")
    delivery_method = _row_value(order, "delivery_method")
    payment_method = _row_value(order, "payment_method")
    comment = _row_value(order, "comment")

    if order_date:
        lines.append(f"📅 На коли: {order_date}")
    if delivery_method:
        lines.append(f"🚚 Спосіб доставки: {delivery_method}")
    if payment_method:
        lines.append(f"💳 Оплата: {payment_method}")
    if comment:
        lines.append(f"💬 Коментар: {comment}")
    return "\n".join(lines)
