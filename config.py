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

# Optional: use this if you want order notifications in a private admin group/channel too.
# Example: ADMIN_CHAT_IDS=-1001234567890,123456789
ADMIN_CHAT_IDS = [
    int(chat_id)
    for chat_id in os.getenv("ADMIN_CHAT_IDS", "").split(",")
    if chat_id.strip()
]


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS
