from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from database.temp_storage import PRODUCTS

PHOTO, NAME = range(2)


async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Отправь фото товара 🍰"
    )

    return PHOTO


async def add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1].file_id

    context.user_data["photo"] = photo

    await update.message.reply_text(
        "Теперь напиши название товара:"
    )

    return NAME


async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    name = update.message.text
    photo = context.user_data.get("photo")

    if "cakes" not in PRODUCTS:
        PRODUCTS["cakes"] = []

    PRODUCTS["cakes"].append({
        "name": name,
        "price": "—",
        "desc": "Добавлено через бота",
        "photo": photo
    })

    await update.message.reply_text(
        f"✅ Товар добавлен:\n{name}"
    )

    return ConversationHandler.END
