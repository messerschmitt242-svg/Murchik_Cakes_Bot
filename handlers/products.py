from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from database.products import PRODUCTS


async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):

    product = {
        "name": "Сникерс",
        "photos": ["file_id1", "file_id2"]
    }

    caption = f"🍰 {product['name']}"

    photos = product.get("photos", [])

    # отправляем первую с текстом
    if photos:
        await update.message.reply_photo(
            photo=photos[0],
            caption=caption
        )

        # остальные просто как фото
        for p in photos[1:]:
            await update.message.reply_photo(photo=p)
    else:
        await update.message.reply_text(caption)
