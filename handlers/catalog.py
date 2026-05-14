from telegram import Update
from telegram.ext import ContextTypes

from keyboards.catalog_menu import catalog_menu


async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Оберіть категорію 🍰",
        reply_markup=catalog_menu
    )
