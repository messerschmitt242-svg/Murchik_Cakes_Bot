import sqlite3
import json
from database.db import get_conn


def get_all_products():

    conn = get_conn()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products"
    )

    rows = cursor.fetchall()

    conn.close()

    products = []

    for row in rows:

        products.append({

            "id": row[0],
            "name": row[1],
            "price": row[2],
            "description": row[3],
            "photos": row[4]
        })

    return products
