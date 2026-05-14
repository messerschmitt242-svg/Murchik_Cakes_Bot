from database.db import get_conn


def create_custom_order_db(
    user_id: int,
    name: str,
    phone: str,
    description: str,
    date: str,
    photo: str = "",
) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO custom_orders (user_id, name, phone, description, date, photo, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, phone, description, date, photo, "Прийнято"),
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id
