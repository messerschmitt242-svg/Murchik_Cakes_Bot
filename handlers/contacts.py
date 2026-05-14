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
                url="https://maps.app.goo.gl/h3XoRor8GWZucXFj8"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Зателефонувати",
                url="tel:+48504690652"
            )
        ]
    ])

    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard
    )
