from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_conn
from config import ADMIN_ID


STATUSES = [
    "Прийнято",
    "Готується",
    "Готове до видачі",
    "Завершено"
]
