import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip().lstrip("@")

ADMIN_IDS = [
    int(admin_id)
    for admin_id in os.getenv("ADMIN_IDS", "").split(",")
    if admin_id.strip()
]


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# PostgreSQL / Railway
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

# Optional local SQLite fallback
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "/data/database.db")
