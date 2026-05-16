
import json
from database.db import get_conn, is_postgres
from utils_translation import generate_product_translations

CATEGORIES = ["Торти", "Тістечка"]


def _decode_json(raw, default):
    if not raw:
        return default
    if isinstance(raw, (list, dict)):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return default


def _decode_photos(raw):
    return _decode_json(raw, [])


def _decode_translations(raw):
    return _decode_json(raw, {})


def get_categories():
    return CATEGORIES


def _row_has(row, key: str) -> bool:
    try:
        return key in row.keys()
    except Exception:
        return False


def _row_to_product(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "price": float(row["price"] or 0),
        "description": row["description"] or "",
        "photos": _decode_photos(row["photos"]),
        "category": row["category"] or "Торти",
        "portion": row["portion"] if _row_has(row, "portion") else "",
        "label_image": row["label_image"] if _row_has(row, "label_image") else "",
        "translations": _decode_translations(row["translations"] if _row_has(row, "translations") else "{}"),
    }


def get_all_products(category: str | None = None):
    conn = get_conn()
    cursor = conn.cursor()

    if category:
        cursor.execute(
            """
            SELECT id, name, price, description, photos, category, portion, label_image, translations
            FROM products
            WHERE category = ?
            ORDER BY id DESC
            """,
            (category,),
        )
    else:
        cursor.execute(
            """
            SELECT id, name, price, description, photos, category, portion, label_image, translations
            FROM products
            ORDER BY id DESC
            """
        )

    rows = cursor.fetchall()
    conn.close()

    return [_row_to_product(row) for row in rows]


def get_product(product_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, price, description, photos, category, portion, label_image, translations
        FROM products
        WHERE id = ?
        """,
        (product_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return _row_to_product(row)


def add_product(
    name: str,
    price: float,
    description: str,
    photos: list[str],
    category: str,
    portion: str = "",
    label_image: str = "",
):
    if category not in CATEGORIES:
        category = "Торти"

    translations = generate_product_translations(name, description)

    conn = get_conn()
    cursor = conn.cursor()

    if is_postgres():
        cursor.execute(
            """
            INSERT INTO products (name, price, description, photos, category, portion, label_image, translations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
            """,
            (
                name,
                price,
                description,
                json.dumps(photos, ensure_ascii=False),
                category,
                portion,
                label_image,
                json.dumps(translations, ensure_ascii=False),
            ),
        )
        product_id = cursor.fetchone()["id"]
    else:
        cursor.execute(
            """
            INSERT INTO products (name, price, description, photos, category, portion, label_image, translations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                price,
                description,
                json.dumps(photos, ensure_ascii=False),
                category,
                portion,
                label_image,
                json.dumps(translations, ensure_ascii=False),
            ),
        )
        product_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return product_id


def update_product_translations(product_id: int, translations: dict):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET translations = ? WHERE id = ?",
        (json.dumps(translations, ensure_ascii=False), product_id),
    )
    conn.commit()
    conn.close()


def update_product_photos(product_id: int, photos: list[str]) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET photos = ? WHERE id = ?",
        (json.dumps(photos, ensure_ascii=False), product_id),
    )
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def update_product_label(product_id: int, label_image: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET label_image = ? WHERE id = ?",
        (label_image, product_id),
    )
    conn.commit()
    conn.close()


def update_product_portion(product_id: int, portion: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET portion = ? WHERE id = ?",
        (portion, product_id),
    )
    conn.commit()
    conn.close()


def regenerate_product_translations(product_id: int):
    product = get_product(product_id)
    if not product:
        return False
    translations = generate_product_translations(product["name"], product["description"])
    update_product_translations(product_id, translations)
    return True


def delete_product_by_id(product_id: int) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM favorites WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
