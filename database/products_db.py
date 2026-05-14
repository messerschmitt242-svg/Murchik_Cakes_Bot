import json
from database.db import get_conn

CATEGORIES = ["Торти", "Тістечка"]


def _decode_photos(raw):
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return []


def get_categories():
    return CATEGORIES


def get_all_products(category: str | None = None):
    conn = get_conn()
    cursor = conn.cursor()

    if category:
        cursor.execute(
            """
            SELECT id, name, price, description, photos, category
            FROM products
            WHERE category = ?
            ORDER BY id DESC
            """,
            (category,),
        )
    else:
        cursor.execute(
            """
            SELECT id, name, price, description, photos, category
            FROM products
            ORDER BY id DESC
            """
        )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "name": row["name"],
            "price": float(row["price"] or 0),
            "description": row["description"] or "",
            "photos": _decode_photos(row["photos"]),
            "category": row["category"] or "Торти",
        }
        for row in rows
    ]


def get_product(product_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, price, description, photos, category
        FROM products
        WHERE id = ?
        """,
        (product_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "name": row["name"],
        "price": float(row["price"] or 0),
        "description": row["description"] or "",
        "photos": _decode_photos(row["photos"]),
        "category": row["category"] or "Торти",
    }


def add_product(name: str, price: float, description: str, photos: list[str], category: str):
    if category not in CATEGORIES:
        category = "Торти"

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO products (name, price, description, photos, category)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            price,
            description,
            json.dumps(photos, ensure_ascii=False),
            category,
        ),
    )
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id


def delete_product_by_id(product_id: int) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
