from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

print("CONTACTS TRIGGERED")

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

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )
