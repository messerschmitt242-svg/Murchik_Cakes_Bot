from database.db import get_conn, is_postgres
from database.promo_db import get_promo


def add_to_cart_db(user_id: int, product_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    if is_postgres():
        cursor.execute(
            """
            INSERT INTO cart (user_id, product_id, qty)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, product_id) DO UPDATE SET qty = cart.qty + 1
            """,
            (user_id, product_id),
        )
    else:
        cursor.execute(
            """
            INSERT INTO cart (user_id, product_id, qty)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, product_id) DO UPDATE SET qty = qty + 1
            """,
            (user_id, product_id),
        )
    conn.commit()
    conn.close()


def change_cart_qty_db(user_id: int, product_id: int, delta: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cart SET qty = qty + ? WHERE user_id = ? AND product_id = ?",
        (delta, user_id, product_id),
    )
    cursor.execute(
        "DELETE FROM cart WHERE user_id = ? AND product_id = ? AND qty <= 0",
        (user_id, product_id),
    )
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


def apply_promo_to_cart_item(user_id: int, product_id: int, code: str):
    promo = get_promo(code, product_id=product_id)
    if not promo:
        return False, None
    normalized_code = promo["code"]
    discount = int(promo["discount_percent"])
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE cart
        SET promo_code = ?, discount_percent = ?
        WHERE user_id = ? AND product_id = ?
        """,
        (normalized_code, discount, user_id, product_id),
    )
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed, discount


def apply_promo_to_cart(user_id: int, code: str):
    """Apply a promo to all eligible cart items. Product-specific promo touches only its product."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id FROM cart WHERE user_id = ?", (user_id,))
    product_ids = [int(row["product_id"]) for row in cursor.fetchall()]
    conn.close()

    applied = 0
    last_discount = None
    for product_id in product_ids:
        ok, discount = apply_promo_to_cart_item(user_id, product_id, code)
        if ok:
            applied += 1
            last_discount = discount
    return applied > 0, applied, last_discount


def get_cart_items_db(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.product_id, c.qty, c.promo_code, c.discount_percent,
               p.name, p.price
        FROM cart c
        JOIN products p ON p.id = c.product_id
        WHERE c.user_id = ?
        ORDER BY p.name
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    items = []
    total_before_discount = 0.0
    total_discount = 0.0
    total = 0.0
    for row in rows:
        price = float(row["price"] or 0)
        qty = int(row["qty"] or 0)
        discount_percent = int(row["discount_percent"] or 0)
        subtotal = price * qty
        discount_amount = subtotal * discount_percent / 100
        final_subtotal = subtotal - discount_amount
        total_before_discount += subtotal
        total_discount += discount_amount
        total += final_subtotal
        items.append(
            {
                "product_id": row["product_id"],
                "name": row["name"],
                "price": price,
                "qty": qty,
                "subtotal": subtotal,
                "promo_code": row["promo_code"] or "",
                "discount_percent": discount_percent,
                "discount_amount": discount_amount,
                "final_subtotal": final_subtotal,
            }
        )
    return items, total, total_before_discount, total_discount
