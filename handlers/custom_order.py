from telegram import Update
from telegram.ext import ContextTypes

async def custom_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎂 Надішліть фото або опис бажаного торта"
    )
