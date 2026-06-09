import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
BOT_USERNAME = os.getenv("BOT_USERNAME", "").strip().lstrip("@")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip().lstrip("@")
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def _parse_int_list(raw: str) -> list[int]:
    result: list[int] = []
    for part in (raw or "").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            result.append(int(part))
        except ValueError:
            print(f"CONFIG WARNING: ignored non-numeric id: {part}")
    return result


ADMIN_IDS = _parse_int_list(os.getenv("ADMIN_IDS", ""))
# No separate Railway variable is required. Kept only as an internal optional list
# for compatibility with API code that imports ADMIN_CHAT_IDS.
ADMIN_CHAT_IDS: list[int] = []


def is_admin(user_id: int | str | None) -> bool:
    try:
        return int(user_id) in ADMIN_IDS
    except (TypeError, ValueError):
        return False
