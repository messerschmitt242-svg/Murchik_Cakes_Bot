from telegram import Update
from telegram.ext import ContextTypes

from database.products_db import get_all_products
from keyboards.main_menu import main_menu


async def show_products(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    products = get_all_products()

    if not products:
        await update.message.reply_text(
            "Каталог пустий 🍰",
            reply_markup=main_menu
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

            await update.message.reply_photo(
                photo=photos[0],
                caption=caption
            )

            for ph in photos[1:]:
                await update.message.reply_photo(
                    photo=ph
                )

        else:
            await update.message.reply_text(
                caption
            )

    await update.message.reply_text(
        "Главное меню 🍰",
        reply_markup=main_menu
    )
