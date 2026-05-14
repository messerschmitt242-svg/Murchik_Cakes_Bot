from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from database.products import PRODUCTS


async def show_cakes(update: Update, context: ContextTypes.DEFAULT_TYPE):

    category = None

    text = update.message.text

    if text == "🍰 Торти":
        category = "cakes"

    elif text == "🍮 Тістечка":
        category = "desserts"

    if not category:
        return

    products = PRODUCTS.get(category, [])

    for p in products:

        caption = f"""
🍰 {p['name']}
💰 {p['price']}
📝 {p['desc']}
"""

        if p["photo"]:
            await update.message.reply_photo(
                photo=p["photo"],
                caption=caption
            )
        else:
            await update.message.reply_text(caption)
