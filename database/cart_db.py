from database.db import get_conn
from database.products_db import get_product


def add_to_cart_db(user_id: int, product_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cart (user_id, product_id, qty)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, product_id)
        DO UPDATE SET qty = qty + 1
    """, (user_id, product_id))
    conn.commit()
    conn.close()


def change_cart_qty_db(user_id: int, product_id: int, delta: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE cart
        SET qty = qty + ?
        WHERE user_id = ? AND product_id = ?
    """, (delta, user_id, product_id))
    cursor.execute("""
        DELETE FROM cart
        WHERE user_id = ? AND product_id = ? AND qty <= 0
    """, (user_id, product_id))
    conn.commit()
    conn.close()


def remove_from_cart_db(user_id: int, product_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()


def clear_cart_db(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_cart_items_db(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.product_id, c.qty, p.name, p.price
        FROM cart c
        JOIN products p ON p.id = c.product_id
        WHERE c.user_id = ?
        ORDER BY p.name
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    items = []
    total = 0.0

    for row in rows:
        price = float(row["price"] or 0)
        qty = int(row["qty"] or 0)
        subtotal = price * qty
        total += subtotal
        items.append({
            "product_id": row["product_id"],
            "name": row["name"],
            "price": price,
            "qty": qty,
            "subtotal": subtotal,
        })

    return items, total
