from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

from database.temp_storage import PRODUCTS

PHOTO, NAME = range(2)

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["photos"] = []

    await update.message.reply_text(
        "Отправляй фото товара 🍰\n\nКогда закончишь — напиши: ГОТОВО"
    )

    return PHOTO

async def add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # если админ закончил
    if text and text.upper() == "ГОТОВО":
        await update.message.reply_text(
            "Теперь напиши название товара:"
        )
        return NAME

    # если фото
    if update.message.photo:

        photo = update.message.photo[-1].file_id

        context.user_data["photos"].append(photo)

        await update.message.reply_text(
            f"Фото добавлено ✅ ({len(context.user_data['photos'])})\n"
            "Можешь отправить ещё или написать ГОТОВО"
        )

    return PHOTO

async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    name = update.message.text
    photos = context.user_data.get("photos", [])

    if "cakes" not in PRODUCTS:
        PRODUCTS["cakes"] = []

    PRODUCTS["cakes"].append({
        "name": name,
        "price": "—",
        "desc": "Добавлено через бота",
        "photos": photos
    })

    await update.message.reply_text(
        f"✅ Товар добавлен:\n{name}\nФото: {len(photos)} шт."
    )

    return ConversationHandler.END
