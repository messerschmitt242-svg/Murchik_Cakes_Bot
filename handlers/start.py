from telegram import Update
from telegram.ext import ContextTypes

from keyboards.main_menu import get_main_menu
from locales import tr


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        tr(user_id, "start_welcome"),
        reply_markup=get_main_menu(user_id),
    )
