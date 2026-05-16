from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import is_admin
from database.products_db import get_all_products, update_product_photos
from handlers.cleanup import delete_callback_message

UPDATE_PHOTOS_PRODUCT = 900
UPDATE_PHOTOS_UPLOAD = 901


def _products_keyboard():
    keyboard = []
    for product in get_all_products():
        keyboard.append([
            InlineKeyboardButton(
                f"#{product['id']} — {product['name']}",
                callback_data=f"update_photos_product_{product['id']}",
            )
        ])
    keyboard.append([InlineKeyboardButton("❌ Скасувати", callback_data="update_photos_cancel")])
    return InlineKeyboardMarkup(keyboard)


def _finish_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Зберегти нові фото", callback_data="update_photos_finish")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="update_photos_cancel")],
    ])


async def update_photos_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        try:
            await query.message.delete()
        except Exception:
            pass

        async def send(text, reply_markup=None):
            return await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    else:
        send = update.message.reply_text

    products = get_all_products()
    if not products:
        await send("Каталог порожній 🍰")
        return ConversationHandler.END

    context.user_data["update_product_photos"] = {"photos": []}
    await send("Оберіть продукт, для якого потрібно замінити живі фото:", reply_markup=_products_keyboard())
    return UPDATE_PHOTOS_PRODUCT


async def update_photos_choose_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return ConversationHandler.END

    product_id = int(query.data.split("_")[-1])
    context.user_data.setdefault("update_product_photos", {"photos": []})["product_id"] = product_id
    await delete_callback_message(query)

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Надішліть нові фото продукту. Можна декілька фото по одному повідомленню. Після цього натисніть ✅ Зберегти нові фото.",
        reply_markup=_finish_keyboard(),
    )
    return UPDATE_PHOTOS_UPLOAD


async def update_photos_add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END

    if not update.message or not update.message.photo:
        await update.message.reply_text("❌ Надішліть саме фото.", reply_markup=_finish_keyboard())
        return UPDATE_PHOTOS_UPLOAD

    data = context.user_data.setdefault("update_product_photos", {"photos": []})
    data.setdefault("photos", []).append(update.message.photo[-1].file_id)
    await update.message.reply_text(f"Фото додано ✅ ({len(data['photos'])})", reply_markup=_finish_keyboard())
    return UPDATE_PHOTOS_UPLOAD


async def update_photos_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return ConversationHandler.END

    data = context.user_data.get("update_product_photos", {})
    product_id = data.get("product_id")
    photos = data.get("photos", [])

    if not product_id or not photos:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="❌ Оберіть продукт і надішліть хоча б одне фото.",
            reply_markup=_finish_keyboard(),
        )
        return UPDATE_PHOTOS_UPLOAD

    changed = update_product_photos(int(product_id), photos)
    context.user_data.pop("update_product_photos", None)
    await delete_callback_message(query)

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(f"✅ Фото продукту #{product_id} оновлено. Нових фото: {len(photos)}" if changed else "❌ Продукт не знайдено."),
    )
    return ConversationHandler.END


async def update_photos_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("update_product_photos", None)
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await delete_callback_message(query)
        await context.bot.send_message(chat_id=query.message.chat_id, text="Оновлення фото скасовано.")
    elif update.message:
        await update.message.reply_text("Оновлення фото скасовано.")
    return ConversationHandler.END
