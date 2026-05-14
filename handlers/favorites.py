from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

from database.favorites_db import toggle_favorite_db, get_favorites_db
from handlers.cleanup import delete_callback_message


def _favorites_keyboard(products):
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                product["name"],
                callback_data=f"catalog_product_{product['id']}"
            )
        ])
    return InlineKeyboardMarkup(keyboard)


async def toggle_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[-1])
    added = toggle_favorite_db(query.from_user.id, product_id)

    if added:
        await query.message.reply_text("❤️ Додано в обране")
    else:
        await query.message.reply_text("💔 Видалено з обраного")


async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    products = get_favorites_db(user_id)

    if not products:
        await update.message.reply_text("❤️ У вас поки немає обраних товарів.")
        return

    await update.message.reply_text(
        "❤️ Ваші обрані товари:",
        reply_markup=_favorites_keyboard(products),
    )
