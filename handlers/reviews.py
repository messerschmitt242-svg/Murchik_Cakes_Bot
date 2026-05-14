from telegram import Update
from telegram.ext import ContextTypes

async def review_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💬 Напишіть ваш відгук про замовлення"
    )
