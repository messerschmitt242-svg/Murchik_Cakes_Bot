
from telegram import Update
from telegram.ext import ContextTypes

from config import is_admin
from database.products_db import get_all_products, regenerate_product_translations

async def regenerate_translations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    products = get_all_products()
    count = 0
    for product in products:
        if regenerate_product_translations(product["id"]):
            count += 1

    await update.message.reply_text(
        f"✅ Переклади оновлено для товарів: {count}"
    )
