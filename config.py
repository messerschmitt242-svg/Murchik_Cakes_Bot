import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip().lstrip("@")


def _parse_admin_ids(raw: str) -> list[int]:
    ids: list[int] = []
    for part in (raw or "").replace(";", ",").split(","):
        value = part.strip()
        if not value:
            continue
        try:
            ids.append(int(value))
        except ValueError:
            print(f"CONFIG WARNING: skipped invalid ADMIN_IDS value: {value!r}")
    return ids


ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# PostgreSQL / Railway
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

# Optional local SQLite fallback
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "/data/database.db")
