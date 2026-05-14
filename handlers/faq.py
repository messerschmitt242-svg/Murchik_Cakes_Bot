from telegram import Update
from telegram.ext import ContextTypes
from keyboards.main_menu import main_menu


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
❓ Питання та відповіді

📌 За скільки днів замовляти?
За 4 дні.

📌 Можна свій дизайн?
Так, можна надіслати референс або опис.

📌 Чи є доставка?
Поки власної доставки немає. За потреби можемо надіслати через Glovo.
"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu
    )
