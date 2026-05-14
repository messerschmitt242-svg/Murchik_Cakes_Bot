import json
from database.db import get_conn


def get_all_products():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM products")
    rows = c.fetchall()

    conn.close()

    return [
        {
            "id": r[0],
            "name": r[1],
            "price": r[2],
            "desc": r[3],
            "photos": json.loads(r[4] or "[]")
        }
        for r in rows
    ]
