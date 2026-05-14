from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import is_admin
from database.products_db import get_all_products, delete_product_by_id


async def delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    products = get_all_products()

    if not products:
        await update.message.reply_text("Каталог порожній 🍰")
        return

    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                f"🗑 ID {product['id']} | {product['name']}",
                callback_data=f"delete_product_{product['id']}"
            )
        ])

    await update.message.reply_text(
        "Оберіть товар для видалення:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def delete_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != is_admin():
        return

    product_id = int(query.data.split("_")[-1])
    deleted = delete_product_by_id(product_id)

    if deleted:
        await query.message.edit_text(f"✅ Товар ID {product_id} видалено.")
    else:
        await query.message.edit_text(f"❌ Товар ID {product_id} не знайдено.")
