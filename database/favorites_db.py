from database.db import get_conn
from database.products_db import get_product


def is_favorite_db(user_id: int, product_id: int) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM favorites WHERE user_id = ? AND product_id = ?",
        (user_id, product_id),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def add_favorite_db(user_id: int, product_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO favorites (user_id, product_id) VALUES (?, ?)",
        (user_id, product_id),
    )
    conn.commit()
    conn.close()


def remove_favorite_db(user_id: int, product_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM favorites WHERE user_id = ? AND product_id = ?",
        (user_id, product_id),
    )
    conn.commit()
    conn.close()


def toggle_favorite_db(user_id: int, product_id: int) -> bool:
    if is_favorite_db(user_id, product_id):
        remove_favorite_db(user_id, product_id)
        return False

    if get_product(product_id):
        add_favorite_db(user_id, product_id)
        return True

    return False


def get_favorites_db(user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.id, p.name, p.price, p.description, p.photos, p.category, p.translations
        FROM favorites f
        JOIN products p ON p.id = f.product_id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    import json

    result = []
    for row in rows:
        try:
            photos = json.loads(row["photos"] or "[]")
        except Exception:
            photos = []

        result.append({
            "id": row["id"],
            "name": row["name"],
            "price": float(row["price"] or 0),
            "description": row["description"] or "",
            "photos": photos,
            "category": row["category"] or "Торти",
            "translations": json.loads(row["translations"] or "{}") if "translations" in row.keys() else {},
        })

    return result
