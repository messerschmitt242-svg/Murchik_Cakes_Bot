from database.db import get_conn

def add_to_cart_db(user_id, product_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO cart (user_id, product_id, qty)
        VALUES (?, ?, 1)
    """, (user_id, product_id))

    conn.commit()
    conn.close()
