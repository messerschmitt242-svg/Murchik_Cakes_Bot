from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.favorites_db import toggle_favorite_db, get_favorites_db
from locales import tr
from utils_translation import translate_product_name


def _favorites_keyboard(products, user_id: int):
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                translate_product_name(product["name"], user_id, product.get("translations")),
                callback_data=f"catalog_product_{product['id']}"
            )
        ])
    return InlineKeyboardMarkup(keyboard)


async def toggle_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    product_id = int(query.data.split("_")[-1])
    added = toggle_favorite_db(user_id, product_id)

    if added:
        await query.message.reply_text(tr(user_id, "fav_added"))
    else:
        await query.message.reply_text(tr(user_id, "fav_removed"))


async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    products = get_favorites_db(user_id)

    if not products:
        await update.message.reply_text(tr(user_id, "fav_empty"))
        return

    await update.message.reply_text(
        tr(user_id, "fav_title"),
        reply_markup=_favorites_keyboard(products, user_id),
    )
