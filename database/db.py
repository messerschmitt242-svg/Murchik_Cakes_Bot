
import os
import sqlite3
from os import makedirs
from urllib.parse import urlparse

from config import DATABASE_URL, SQLITE_DB_PATH

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:
    psycopg2 = None
    RealDictCursor = None


def is_postgres() -> bool:
    return bool(DATABASE_URL)


def _normalize_database_url(url: str) -> str:
    # Railway usually provides a valid postgres:// or postgresql:// URL.
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


def _sqlite_path() -> str:
    return SQLITE_DB_PATH or "/data/database.db"


def _translate_sql(sql: str) -> str:
    if not is_postgres():
        return sql

    # This project uses SQLite-style placeholders.
    # psycopg2 needs %s.
    return sql.replace("?", "%s")


class CursorCompat:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = None

    def execute(self, sql, params=None):
        params = params or ()
        translated_sql = _translate_sql(sql)
        self._cursor.execute(translated_sql, params)
        self.lastrowid = None
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class ConnCompat:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        if is_postgres():
            return CursorCompat(self._conn.cursor(cursor_factory=RealDictCursor))
        return self._conn.cursor()

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)


def get_conn():
    if is_postgres():
        if psycopg2 is None:
            raise RuntimeError("psycopg2-binary is not installed. Add it to requirements.txt")
        conn = psycopg2.connect(_normalize_database_url(DATABASE_URL))
        return ConnCompat(conn)

    db_path = _sqlite_path()
    makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_column_sqlite(cursor, table: str, column: str, definition: str):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _ensure_column_postgres(cursor, table: str, column: str, definition: str):
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
        """,
        (table, column),
    )
    if cursor.fetchone() is None:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _ensure_column(cursor, table: str, column: str, definition: str):
    if is_postgres():
        _ensure_column_postgres(cursor, table, column, definition)
    else:
        _ensure_column_sqlite(cursor, table, column, definition)


def _init_postgres(cursor):
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
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
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
            status TEXT DEFAULT 'Прийнято',
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            user_id BIGINT NOT NULL,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
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
            status TEXT DEFAULT 'Прийнято',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id BIGINT PRIMARY KEY,
            language TEXT DEFAULT 'ua'
        )
    """)


def _init_sqlite(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL DEFAULT 0,
            description TEXT DEFAULT '',
            photos TEXT DEFAULT '[]',
            category TEXT DEFAULT 'Торти',
            portion TEXT DEFAULT '',
            label_image TEXT DEFAULT '',
            translations TEXT DEFAULT '{}',
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
            order_date TEXT DEFAULT '',
            delivery_method TEXT DEFAULT '',
            payment_method TEXT DEFAULT '',
            comment TEXT DEFAULT '',
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
            status TEXT DEFAULT 'Прийнято',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'ua'
        )
    """)


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    if is_postgres():
        _init_postgres(cursor)
    else:
        _init_sqlite(cursor)

    # Soft migrations for existing DBs.
    if is_postgres():
        _ensure_column(cursor, "products", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        _ensure_column(cursor, "products", "category", "TEXT DEFAULT 'Торти'")
        _ensure_column(cursor, "products", "portion", "TEXT DEFAULT ''")
        _ensure_column(cursor, "products", "label_image", "TEXT DEFAULT ''")
        _ensure_column(cursor, "products", "translations", "TEXT DEFAULT '{}'")
        _ensure_column(cursor, "cart", "promo_code", "TEXT DEFAULT ''")
        _ensure_column(cursor, "cart", "discount_percent", "INTEGER DEFAULT 0")
        _ensure_column(cursor, "orders", "items", "TEXT DEFAULT ''")
        _ensure_column(cursor, "orders", "total", "REAL DEFAULT 0")
        _ensure_column(cursor, "orders", "order_date", "TEXT DEFAULT ''")
        _ensure_column(cursor, "orders", "delivery_method", "TEXT DEFAULT ''")
        _ensure_column(cursor, "orders", "payment_method", "TEXT DEFAULT ''")
        _ensure_column(cursor, "orders", "comment", "TEXT DEFAULT ''")
        _ensure_column(cursor, "orders", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        _ensure_column(cursor, "reviews", "review_type", "TEXT DEFAULT 'bakery'")
        _ensure_column(cursor, "reviews", "product_id", "INTEGER DEFAULT NULL")
        _ensure_column(cursor, "reviews", "product_name", "TEXT DEFAULT ''")
        _ensure_column(cursor, "custom_orders", "product_id", "INTEGER DEFAULT NULL")
        _ensure_column(cursor, "custom_orders", "product_name", "TEXT DEFAULT ''")
    else:
        _ensure_column(cursor, "products", "created_at", "TEXT DEFAULT CURRENT_TIMESTAMP")
        _ensure_column(cursor, "products", "category", "TEXT DEFAULT 'Торти'")
        _ensure_column(cursor, "products", "portion", "TEXT DEFAULT ''")
        _ensure_column(cursor, "products", "label_image", "TEXT DEFAULT ''")
        _ensure_column(cursor, "products", "translations", "TEXT DEFAULT '{}'")
        _ensure_column(cursor, "cart", "promo_code", "TEXT DEFAULT ''")
        _ensure_column(cursor, "cart", "discount_percent", "INTEGER DEFAULT 0")
        _ensure_column(cursor, "orders", "items", "TEXT DEFAULT ''")
        _ensure_column(cursor, "orders", "total", "REAL DEFAULT 0")
        _ensure_column(cursor, "orders", "order_date", "TEXT DEFAULT ''")
        _ensure_column(cursor, "orders", "delivery_method", "TEXT DEFAULT ''")
        _ensure_column(cursor, "orders", "payment_method", "TEXT DEFAULT ''")
        _ensure_column(cursor, "orders", "comment", "TEXT DEFAULT ''")
        _ensure_column(cursor, "orders", "created_at", "TEXT DEFAULT CURRENT_TIMESTAMP")
        _ensure_column(cursor, "reviews", "review_type", "TEXT DEFAULT 'bakery'")
        _ensure_column(cursor, "reviews", "product_id", "INTEGER DEFAULT NULL")
        _ensure_column(cursor, "reviews", "product_name", "TEXT DEFAULT ''")
        _ensure_column(cursor, "custom_orders", "product_id", "INTEGER DEFAULT NULL")
        _ensure_column(cursor, "custom_orders", "product_name", "TEXT DEFAULT ''")

    conn.commit()
    conn.close()
