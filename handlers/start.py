from telegram import Update
from telegram.ext import ContextTypes

from keyboards.main_menu import main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Добро пожаловать в кондитерскую 🎂",
        reply_markup=main_menu
    )