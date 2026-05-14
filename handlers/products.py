from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ContextTypes

from database.products_db import get_all_products

import json


async def show_products(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    products = get_all_products()

    if not products:

        await update.message.reply_text(
            "Каталог порожній 🍰"
        )

        return

    for p in products:

        try:
            photos = json.loads(
                p["photos"]
            )

        except:
            photos = []

        caption = f"""
🍰 {p['name']}

💰 {p['price']} zł

📝 {p['description']}
"""

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🛒 Додати у кошик",
                    callback_data=f"add_{p['id']}"
                )
            ]
        ])

        if photos:

            await update.message.reply_photo(
                photo=photos[0],
                caption=caption,
                reply_markup=keyboard
            )

            for ph in photos[1:]:

                await update.message.reply_photo(
                    photo=ph
                )

        else:

            await update.message.reply_text(
                caption,
                reply_markup=keyboard
            )
