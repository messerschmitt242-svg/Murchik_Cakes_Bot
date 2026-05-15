from telegram import Update
from telegram.ext import ContextTypes

from config import is_admin
from database.maintenance_db import clear_test_data_keep_catalog_and_reviews


async def clear_test_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    clear_test_data_keep_catalog_and_reviews()

    await update.message.reply_text(
        "✅ Тестові дані очищено.\n"
        "Каталог продуктів і відгуки залишились."
    )
