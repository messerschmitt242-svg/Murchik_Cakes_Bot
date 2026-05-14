from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.products_db import get_all_products
from keyboards.main_menu import main_menu


async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):

    products = get_all_products()

    if not products:
        await update.message.reply_text(
            "Каталог пустий 🍰",
            reply_markup=main_menu
        )
        return

    for p in products:

        product_id = p.get("id")
        name = p.get("name", "Без названия")
        price = p.get("price", "—")
        desc = p.get("desc", "—")
        photos = p.get("photos", [])

        caption = f"""
🍰 {name}
💰 {price}
📝 {desc}
"""

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🛒 Додати в кошик",
                    callback_data=f"add_{product_id}"
                )
            ]
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

    await update.message.reply_text(
        "📍 Оберіть товар або відкрийте кошик 🛒",
        reply_markup=main_menu
    )
