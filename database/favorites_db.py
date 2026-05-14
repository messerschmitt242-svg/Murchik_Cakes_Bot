from database.db import get_conn

def add_favorite_db(user_id, product_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "INSERT INTO favorites (user_id, product_id) VALUES (?, ?)",
        (user_id, product_id)
    )

    conn.commit()
    conn.close()
