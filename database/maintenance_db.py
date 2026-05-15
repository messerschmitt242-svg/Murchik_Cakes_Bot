from database.db import get_conn


def clear_test_data_keep_catalog_and_reviews():
    """Clear operational/test data but keep products catalog and reviews."""
    conn = get_conn()
    cursor = conn.cursor()

    tables = [
        "cart",
        "orders",
        "custom_orders",
        "favorites",
        "promo_codes",
    ]

    for table in tables:
        cursor.execute(f"DELETE FROM {table}")

    conn.commit()
    conn.close()
