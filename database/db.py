import os
import sqlite3
from typing import Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:  # local sqlite-only mode
    psycopg2 = None
    RealDictCursor = None

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def _default_db_path() -> str:
    if os.path.isdir("/data"):
        return "/data/data.db"
    return os.path.join("data", "data.db")


DB_PATH = os.getenv("DB_PATH", _default_db_path())


def is_postgres() -> bool:
    return DATABASE_URL.startswith(("postgres://", "postgresql://"))


def _pg_sql(sql: str) -> str:
    # The project uses sqlite-style ? placeholders everywhere.
    # psycopg2 needs %s, so we translate centrally here.
    return sql.replace("?", "%s")


class PgCursor:
    def __init__(self, cur):
        self.cur = cur

    def execute(self, sql: str, params: Any = None):
        self.cur.execute(_pg_sql(sql), params or ())
        return self

    def fetchone(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()

    @property
    def rowcount(self):
        return self.cur.rowcount

    @property
    def lastrowid(self):
        return None

    def close(self):
        return self.cur.close()


class PgConn:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return PgCursor(self.conn.cursor(cursor_factory=RealDictCursor))

    def commit(self):
        return self.conn.commit()

    def close(self):
        return self.conn.close()


def get_conn():
    if is_postgres():
        if psycopg2 is None:
            raise RuntimeError("DATABASE_URL is set, but psycopg2 is not installed")
        return PgConn(psycopg2.connect(DATABASE_URL))

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_column(cursor, table: str, column: str, definition: str):
    if is_postgres():
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = ? AND column_name = ?
            """,
            (table, column),
        )
        if cursor.fetchone() is None:
            pg_definition = definition
            if "DEFAULT CURRENT_TIMESTAMP" in pg_definition:
                pg_definition = pg_definition.replace("TEXT DEFAULT CURRENT_TIMESTAMP", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            if column.endswith("user_id") or column == "user_id":
                pg_definition = pg_definition.replace("INTEGER", "BIGINT")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {pg_definition}")
        return

    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    if is_postgres():
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL DEFAULT 0,
                description TEXT DEFAULT '',
                photos TEXT DEFAULT '[]',
                category TEXT DEFAULT 'Торти',
                portion TEXT DEFAULT '',
                label_image TEXT DEFAULT '',
                translations TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                user_id BIGINT NOT NULL,
                product_id INTEGER NOT NULL,
                qty INTEGER NOT NULL DEFAULT 1,
                promo_code TEXT DEFAULT '',
                discount_percent INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, product_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                items TEXT NOT NULL,
                total REAL DEFAULT 0,
                status TEXT DEFAULT 'Створено',
                order_date TEXT DEFAULT '',
                delivery_method TEXT DEFAULT '',
                payment_method TEXT DEFAULT '',
                comment TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promo_codes (
                code TEXT PRIMARY KEY,
                discount_percent INTEGER NOT NULL,
                is_active INTEGER DEFAULT 1,
                product_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                user_id BIGINT NOT NULL,
                product_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, product_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name TEXT DEFAULT '',
                text TEXT NOT NULL,
                rating INTEGER DEFAULT 5,
                review_type TEXT DEFAULT 'bakery',
                product_id INTEGER DEFAULT NULL,
                product_name TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                product_id INTEGER DEFAULT NULL,
                product_name TEXT DEFAULT '',
                description TEXT NOT NULL,
                date TEXT DEFAULT '',
                photo TEXT DEFAULT '',
                status TEXT DEFAULT 'Створено',
                order_date TEXT DEFAULT '',
                delivery_method TEXT DEFAULT '',
                payment_method TEXT DEFAULT '',
                comment TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS google_oauth_tokens (
                service TEXT PRIMARY KEY,
                refresh_token TEXT NOT NULL,
                account_email TEXT DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
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
                status TEXT DEFAULT 'Створено',
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
                review_type TEXT DEFAULT 'bakery',
                product_id INTEGER DEFAULT NULL,
                product_name TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                product_id INTEGER DEFAULT NULL,
                product_name TEXT DEFAULT '',
                description TEXT NOT NULL,
                date TEXT DEFAULT '',
                photo TEXT DEFAULT '',
                status TEXT DEFAULT 'Створено',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS google_oauth_tokens (
                service TEXT PRIMARY KEY,
                refresh_token TEXT NOT NULL,
                account_email TEXT DEFAULT '',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    # Soft migrations for old databases.
    _ensure_column(cursor, "products", "created_at", "TEXT DEFAULT CURRENT_TIMESTAMP")
    _ensure_column(cursor, "products", "category", "TEXT DEFAULT 'Торти'")
    _ensure_column(cursor, "products", "portion", "TEXT DEFAULT ''")
    _ensure_column(cursor, "products", "label_image", "TEXT DEFAULT ''")
    _ensure_column(cursor, "products", "translations", "TEXT DEFAULT '{}'")
    _ensure_column(cursor, "cart", "promo_code", "TEXT DEFAULT ''")
    _ensure_column(cursor, "cart", "discount_percent", "INTEGER DEFAULT 0")
    _ensure_column(cursor, "orders", "items", "TEXT DEFAULT ''")
    _ensure_column(cursor, "orders", "total", "REAL DEFAULT 0")
    _ensure_column(cursor, "orders", "created_at", "TEXT DEFAULT CURRENT_TIMESTAMP")
    _ensure_column(cursor, "orders", "order_date", "TEXT DEFAULT ''")
    _ensure_column(cursor, "orders", "delivery_method", "TEXT DEFAULT ''")
    _ensure_column(cursor, "orders", "payment_method", "TEXT DEFAULT ''")
    _ensure_column(cursor, "orders", "comment", "TEXT DEFAULT ''")
    _ensure_column(cursor, "promo_codes", "product_id", "INTEGER DEFAULT NULL")
    _ensure_column(cursor, "reviews", "review_type", "TEXT DEFAULT 'bakery'")
    _ensure_column(cursor, "reviews", "product_id", "INTEGER DEFAULT NULL")
    _ensure_column(cursor, "reviews", "product_name", "TEXT DEFAULT ''")
    _ensure_column(cursor, "custom_orders", "product_id", "INTEGER DEFAULT NULL")
    _ensure_column(cursor, "custom_orders", "product_name", "TEXT DEFAULT ''")
    _ensure_column(cursor, "custom_orders", "order_date", "TEXT DEFAULT ''")
    _ensure_column(cursor, "custom_orders", "delivery_method", "TEXT DEFAULT ''")
    _ensure_column(cursor, "custom_orders", "payment_method", "TEXT DEFAULT ''")
    _ensure_column(cursor, "custom_orders", "comment", "TEXT DEFAULT ''")

    # Normalize old grammatically incorrect status values.
    cursor.execute("UPDATE orders SET status = ? WHERE status = ?", ("Створено", "Створений"))
    cursor.execute("UPDATE custom_orders SET status = ? WHERE status = ?", ("Створено", "Створений"))

    conn.commit()
    conn.close()
