from database.db import get_conn

CUSTOM_STATUSES = [
    "Прийнято",
    "Готується",
    "Готове до видачі",
    "Завершено",
    "Скасовано",
]


def create_custom_order_db(
    user_id: int,
    name: str,
    phone: str,
    product_id: int | None,
    product_name: str,
    description: str,
    date: str,
    photo: str = "",
) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO custom_orders (
            user_id, name, phone, product_id, product_name, description, date, photo, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, phone, product_id, product_name, description, date, photo, "Прийнято"),
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id


def get_active_custom_orders():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, phone, product_id, product_name, description, date, photo, status, created_at
        FROM custom_orders
        WHERE status NOT IN ('Завершено', 'Скасовано')
        ORDER BY id DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_custom_order(order_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, phone, product_id, product_name, description, date, photo, status, created_at
        FROM custom_orders
        WHERE id = ?
        """,
        (order_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def update_custom_order_status(order_id: int, status: str) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE custom_orders SET status = ? WHERE id = ?", (status, order_id))
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def delete_cancelled_custom_order(order_id: int) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM custom_orders WHERE id = ? AND status = 'Скасовано'", (order_id,))
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def next_custom_status(current_status: str):
    if current_status == "Прийнято":
        return "Готується", "👩‍🍳 Готується"
    if current_status == "Готується":
        return "Готове до видачі", "✅ Готове до видачі"
    if current_status == "Готове до видачі":
        return "Завершено", "🏁 Завершено"
    return None, None


def get_user_custom_orders(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, phone, product_id, product_name, description, date, photo, status, created_at
        FROM custom_orders
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
