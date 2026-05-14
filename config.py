import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)
else:
    ADMIN_ID = None
