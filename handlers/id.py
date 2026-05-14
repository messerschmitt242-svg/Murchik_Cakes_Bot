from telegram import Update
from telegram.ext import ContextTypes


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Ваш Telegram ID:\n{update.effective_user.id}"
    )
