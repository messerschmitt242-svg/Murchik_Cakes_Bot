from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (ContextTypes,ConversationHandler,MessageHandler,filters)
from keyboards.main_menu import main_menu
from config import ADMIN_ID
from config import ADMIN_ID


NAME = 1
PHONE = 2
CAKE = 3


async def order_start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "Ваше ім'я:"
    )

    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["name"] = update.message.text

    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("📱 Надіслати номер", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Надішліть ваш номер телефону:",
        reply_markup=keyboard
    )

    return PHONE


async def get_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text

    context.user_data["phone"] = phone

    await update.message.reply_text(
        "Що бажаєте замовити?"
    )

    return CAKE


async def get_cake(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["cake"] = update.message.text

    text = f"""
Нове замовлення 🎂

Ім'я:
{context.user_data["name"]}

Телефон:
{context.user_data["phone"]}

Замовлення:
{context.user_data["cake"]}
"""

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

    await update.message.reply_text(
        "Дякуємо ❤️ Заявка відправлена",
        reply_markup=main_menu
    )

    return ConversationHandler.END
