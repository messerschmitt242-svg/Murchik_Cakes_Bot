from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.products_db import get_all_products


async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_all_products()

    if not products:
        await update.message.reply_text("Каталог порожній 🍰")
        return

    for product in products:
        product_id = product["id"]
        name = product["name"]
        price = product["price"]
        description = product["description"]
        photos = product["photos"]

        caption = f"""
🍰 {name}

💰 {price:.2f} zł

📝 {description}
"""

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Додати у кошик", callback_data=f"add_{product_id}")]
        ])

        if photos:
            await update.message.reply_photo(
                photo=photos[0],
                caption=caption,
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(
                caption,
                reply_markup=keyboard
            )
