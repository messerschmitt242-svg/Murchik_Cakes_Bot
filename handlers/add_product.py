from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

import sqlite3
import json
from database.db import get_conn
from config import ADMIN_ID

PHOTO, NAME = range(2)

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return
        
    context.user_data["photos"] = []

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Завершити додавання", callback_data="finish_add")]
    ])

    await update.message.reply_text(
        "Надішліть фото товару 🍰\n\nКоли закінчиш — натисни кнопку:",
        reply_markup=keyboard
    )

    return PHOTO

async def add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1].file_id
    context.user_data["photos"].append(photo)

    await update.message.reply_text(
        f"Фото додано ✅ ({len(context.user_data['photos'])})"
    )

    return PHOTO

async def finish_add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "Теперь напиши название товара:"
    )

    print("FINISH ADD CALLED")

    return NAME

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
