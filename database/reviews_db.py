from database.db import get_conn


def add_review_db(
    user_id: int,
    name: str,
    text: str,
    rating: int,
    review_type: str = "bakery",
    product_id: int | None = None,
    product_name: str = "",
) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reviews (user_id, name, text, rating, review_type, product_id, product_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, text, rating, review_type, product_id, product_name),
    )
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()
    return review_id


def get_reviews_db(limit: int = 5):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, text, rating, review_type, product_id, product_name, created_at
        FROM reviews
        ORDER BY rating DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_bakery_reviews_db(limit: int = 5):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, text, rating, review_type, product_id, product_name, created_at
        FROM reviews
        WHERE review_type = 'bakery'
        ORDER BY rating DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_product_reviews_db(product_id: int, limit: int = 5):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, text, rating, review_type, product_id, product_name, created_at
        FROM reviews
        WHERE review_type = 'product' AND product_id = ?
        ORDER BY rating DESC, id DESC
        LIMIT ?
        """,
        (product_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_product_rating_db(product_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT AVG(rating) AS avg_rating, COUNT(*) AS count_reviews
        FROM reviews
        WHERE review_type = 'product' AND product_id = ?
        """,
        (product_id,),
    )
    row = cursor.fetchone()
    conn.close()

    count = int(row["count_reviews"] or 0)
    if count == 0:
        return None, 0

    return float(row["avg_rating"] or 0), count


def format_reviews(rows) -> str:
    if not rows:
        return "Відгуків поки немає."

    text = ""
    for r in rows:
        product_line = ""
        if r["review_type"] == "product":
            product_line = f"\nТовар: {r['product_name'] or r['product_id']}"

        text += f"""
⭐ {r['rating']}/5
{r['name']}{product_line}
{r['text']}
------------------
"""
    return text.strip()
