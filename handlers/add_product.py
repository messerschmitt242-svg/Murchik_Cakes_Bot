from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

import sqlite3
import json
from database.db import get_conn

PHOTO, NAME = range(2)

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["photos"] = []

    await update.message.reply_text(
        "Надсилайте фото товару 🍰\n\nКоли закінчите — напишіть: ГОТОВО"
    )

    return PHOTO

async def add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # если админ закончил
    if update.message.text and update.message.text.strip().upper() == "ГОТОВО":
        await update.message.reply_text(
            "Теперь напиши название товара:"
        )
        return NAME

    # если фото
    if update.message.photo:

        photo = update.message.photo[-1].file_id

        context.user_data["photos"].append(photo)

        await update.message.reply_text(
            f"Фото додано ✅ ({len(context.user_data['photos'])})\n"
            "Можеш надіслати ще або написати ГОТОВО"
        )

    return PHOTO

async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    name = update.message.text
    photos = context.user_data.get("photos", [])

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, price, description, photos)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        "—",
        "Додано через бота",
        json.dumps(photos)
    ))

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Товар збережено у базі:\n{name}"
    )

    return ConversationHandler.END

    return ConversationHandler.END
