import sqlite3
import json
from database.db import get_conn


def get_all_products():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, price, description, photos FROM products")
    rows = cursor.fetchall()

    conn.close()

    products = []

    for r in rows:
        products.append({
            "id": r[0],
            "name": r[1],
            "price": r[2],
            "desc": r[3],
            "photos": json.loads(r[4]) if r[4] else []
        })

    return products
