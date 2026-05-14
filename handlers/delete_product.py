from telegram import Update
from telegram.ext import ContextTypes

from database.products_db import get_all_products
from database.db import get_conn
from config import ADMIN_ID

async def delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return
        
    products = get_all_products()

    if not products:
        await update.message.reply_text("Каталог пуст 🍰")
        return

    text = "🗑 Введи ID товара для удаления:\n\n"

    for p in products:
        text += f"ID: {p['id']} | {p['name']}\n"

    await update.message.reply_text(text)
    context.user_data["await_delete"] = True
  
async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.user_data.get("await_delete"):
        return

    product_id = update.message.text

    if not product_id.isdigit():
        await update.message.reply_text("Введите корректный ID")
        return

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    context.user_data["await_delete"] = False

    await update.message.reply_text("🗑 Товар удалён")
