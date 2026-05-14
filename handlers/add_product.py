from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler
)

import json
from database.db import get_conn
from config import ADMIN_ID


ADD_PHOTO = 100
ADD_NAME = 101


# =========================
# СТАРТ
# =========================
async def add_product_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    context.user_data["photos"] = []

    await update.message.reply_text(
        "Надішліть фото товару 🍰"
    )

    return ADD_PHOTO


# =========================
# ДОБАВЛЯЕМ ФОТО
# =========================
async def add_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message.photo:

        await update.message.reply_text(
            "❌ Надішліть саме фото"
        )

        return ADD_PHOTO

    photo = update.message.photo[-1].file_id

    context.user_data["photos"].append(photo)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Завершити додавання",
                callback_data="finish_add"
            )
        ]
    ])

    await update.message.reply_text(
        f"Фото додано ✅ ({len(context.user_data['photos'])})",
        reply_markup=keyboard
    )

    return ADD_PHOTO


# =========================
# ГОТОВО
# =========================
async def finish_add(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    print("FINISH ADD CALLED")

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        "Тепер напишіть назву товару:"
    )

    return ADD_NAME


# =========================
# СОХРАНЕНИЕ
# =========================
async def add_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    print("NAME TRIGGERED")

    name = update.message.text

    photos = context.user_data.get(
        "photos",
        []
    )

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO products
        (name, price, description, photos)

        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            0,
            "Додано через бота",
            json.dumps(photos)
        )
    )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Товар збережено:\n{name}"
    )

    context.user_data.clear()

    return ConversationHandler.END
