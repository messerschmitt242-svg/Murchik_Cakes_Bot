from telegram import Update
from telegram.ext import ContextTypes


async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🍰 Наш каталог

🎂 Торти
від 70 zł

🍮Тістечка
от 50 zł

"""

    await update.message.reply_text(text)