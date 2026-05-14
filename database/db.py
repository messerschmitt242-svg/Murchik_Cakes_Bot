import os
import sqlite3


def _default_db_path() -> str:
    """
    Railway: если подключен Volume на /data — база будет храниться там.
    Локально/GitHub: база будет в папке data/data.db.
    """
    if os.path.isdir("/data"):
        return "/data/data.db"
    return os.path.join("data", "data.db")


DB_PATH = os.getenv("DB_PATH", _default_db_path())


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_column(cursor, table: str, column: str, definition: str):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL DEFAULT 0,
            description TEXT DEFAULT '',
            photos TEXT DEFAULT '[]',
            category TEXT DEFAULT 'Торти',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            qty INTEGER NOT NULL DEFAULT 1,
            promo_code TEXT DEFAULT '',
            discount_percent INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, product_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            items TEXT NOT NULL,
            total REAL DEFAULT 0,
            status TEXT DEFAULT 'Прийнято',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            code TEXT PRIMARY KEY,
            discount_percent INTEGER NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, product_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT DEFAULT '',
            text TEXT NOT NULL,
            rating INTEGER DEFAULT 5,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT DEFAULT '',
            photo TEXT DEFAULT '',
            status TEXT DEFAULT 'Прийнято',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Мягкая миграция старых БД, если таблицы уже были созданы иначе.
    _ensure_column(cursor, "products", "created_at", "TEXT DEFAULT CURRENT_TIMESTAMP")
    _ensure_column(cursor, "products", "category", "TEXT DEFAULT 'Торти'")
    _ensure_column(cursor, "cart", "promo_code", "TEXT DEFAULT ''")
    _ensure_column(cursor, "cart", "discount_percent", "INTEGER DEFAULT 0")
    _ensure_column(cursor, "orders", "items", "TEXT DEFAULT ''")
    _ensure_column(cursor, "orders", "total", "REAL DEFAULT 0")
    _ensure_column(cursor, "orders", "created_at", "TEXT DEFAULT CURRENT_TIMESTAMP")

    conn.commit()
    conn.close()
