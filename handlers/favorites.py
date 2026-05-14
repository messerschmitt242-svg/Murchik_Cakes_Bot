from telegram import Update
from telegram.ext import ContextTypes

async def add_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("❤️ Додано в обране")

async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❤️ Тут будуть ваші обрані товари")
