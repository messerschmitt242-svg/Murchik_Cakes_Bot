import sqlite3

DB_PATH = "/data/data.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

ddef init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price TEXT,
        description TEXT,
        photos TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        user_id INTEGER,
        product_id INTEGER,
        qty INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        phone TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()
