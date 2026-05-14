from database.db import get_conn


def add_review_db(user_id: int, name: str, text: str, rating: int) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reviews (user_id, name, text, rating)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, name, text, rating),
    )
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()
    return review_id


def get_reviews_db(limit: int = 10):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, name, text, rating, created_at
        FROM reviews
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
