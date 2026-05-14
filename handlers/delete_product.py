from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import is_admin
from database.products_db import get_all_products, delete_product_by_id
from handlers.cleanup import delete_callback_message


async def delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
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

    if not is_admin(query.from_user.id):
        return

    product_id = int(query.data.split("_")[-1])
    deleted = delete_product_by_id(product_id)

    chat_id = query.message.chat_id
    await delete_callback_message(query)

    if deleted:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Товар ID {product_id} видалено."
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Товар ID {product_id} не знайдено."
        )
