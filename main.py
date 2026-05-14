from telegram.ext import (
    Application,
    CommandHandler
)

from config import BOT_TOKEN
from handlers.start import start
from handlers.id import get_id

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", get_id))

print("Bot started")

app.run_polling()
