from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📍 Наші контакти

📞 Номер телефону:
+48 504 690 652

🕒 Графік роботи:
Пн–Нд: 10:00 – 18:00

🏠 Адреса:
ul. Toruńska 45D, Bydgoszcz
"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📍 Побудувати маршрут",
                url="https://maps.app.goo.gl/7YLX42TMak4FdaXm9"
            )
        ]
    ])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard
    )
