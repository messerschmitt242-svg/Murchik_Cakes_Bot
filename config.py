import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [
    int(admin_id)
    for admin_id in os.getenv("ADMIN_IDS", "").split(",")
    if admin_id.strip()
]


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS
