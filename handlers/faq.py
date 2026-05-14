from telegram import Update
from telegram.ext import ContextTypes
from keyboards.main_menu import main_menu

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
❓ Питання та відповіді

📌 За скільки днів замовляти?
За 4 дні

📌 Можна свій дизайн?
Так

📌 Чи є доставка?
Нажаль поки немає. Але можемо надіслати за допомогою сервісу Glovo.

"""

    await update.message.reply_text(
    text,
    reply_markup=main_menu
)
