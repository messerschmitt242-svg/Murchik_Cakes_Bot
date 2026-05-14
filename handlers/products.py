from telegram import Update
from telegram.ext import ContextTypes

from database.products_db import get_all_products


async def show_products(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    products = get_all_products()

    if not products:
        await update.message.reply_text(
            "Каталог пуст 🍰"
        )
        return

    for p in products:

        caption = f"""
🍰 {p['name']}
💰 {p['price']}
📝 {p['desc']}
"""

        photos = p.get("photos", [])

        if photos:

            # первая фотка с текстом
            await update.message.reply_photo(
                photo=photos[0],
                caption=caption
            )

            # остальные фотки
            for ph in photos[1:]:
                await update.message.reply_photo(
                    photo=ph
                )

        else:
            await update.message.reply_text(
                caption
            )
