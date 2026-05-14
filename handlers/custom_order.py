from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_IDS
from database.custom_orders_db import create_custom_order_db
from keyboards.main_menu import get_main_menu

CUSTOM_NAME = 800
CUSTOM_PHONE = 801
CUSTOM_DESCRIPTION = 802
CUSTOM_DATE = 803
CUSTOM_PHOTO = 804


def _skip_photo_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Пропустити фото", callback_data="custom_skip_photo")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="custom_cancel")],
    ])


async def custom_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["custom_order"] = {}

    await update.message.reply_text(
        "🎂 Індивідуальне замовлення\n\nНапишіть ваше ім'я:"
    )

    return CUSTOM_NAME


async def custom_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text("Ім'я не може бути порожнім. Напишіть ваше ім'я:")
        return CUSTOM_NAME

    context.user_data.setdefault("custom_order", {})["name"] = name

    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Надіслати номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await update.message.reply_text(
        "Надішліть ваш номер телефону:",
        reply_markup=keyboard,
    )

    return CUSTOM_PHONE


async def custom_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    if not phone:
        await update.message.reply_text("Телефон не може бути порожнім. Надішліть номер:")
        return CUSTOM_PHONE

    context.user_data.setdefault("custom_order", {})["phone"] = phone

    await update.message.reply_text(
        "Опишіть, який торт/десерт ви хочете:\n"
        "розмір, начинка, декор, напис, побажання."
    )

    return CUSTOM_DESCRIPTION


async def custom_get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text.strip()

    if len(description) < 5:
        await update.message.reply_text("Опишіть замовлення трохи детальніше:")
        return CUSTOM_DESCRIPTION

    context.user_data.setdefault("custom_order", {})["description"] = description

    await update.message.reply_text(
        "На яку дату потрібне замовлення?\nНаприклад: 25.05 або 25 травня"
    )

    return CUSTOM_DATE


async def custom_get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text.strip()

    if not date:
        await update.message.reply_text("Вкажіть дату:")
        return CUSTOM_DATE

    context.user_data.setdefault("custom_order", {})["date"] = date

    await update.message.reply_text(
        "Можете надіслати фото-приклад або натиснути «Пропустити фото».",
        reply_markup=_skip_photo_keyboard(),
    )

    return CUSTOM_PHOTO


async def custom_get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = ""

    if update.message and update.message.photo:
        photo = update.message.photo[-1].file_id

    return await _save_custom_order(update, context, photo)


async def custom_skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    return await _save_custom_order(update, context, "")


async def _save_custom_order(update: Update, context: ContextTypes.DEFAULT_TYPE, photo: str):
    user = update.effective_user
    data = context.user_data.get("custom_order", {})

    name = data.get("name", "Клієнт")
    phone = data.get("phone", "")
    description = data.get("description", "")
    date = data.get("date", "")

    order_id = create_custom_order_db(
        user_id=user.id,
        name=name,
        phone=phone,
        description=description,
        date=date,
        photo=photo,
    )

    context.user_data.pop("custom_order", None)

    text = f"""
Нове індивідуальне замовлення #{order_id} 🎂

Ім'я: {name}
Телефон: {phone}
Дата: {date}

Опис:
{description}
"""

    for admin_id in ADMIN_IDS:
        if photo:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo,
                caption=text,
            )
        else:
            await context.bot.send_message(
                chat_id=admin_id,
                text=text,
            )

    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Індивідуальне замовлення #{order_id} прийнято. Ми скоро з вами зв'яжемося ❤️",
        reply_markup=get_main_menu(user.id),
    )

    return ConversationHandler.END


async def custom_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("custom_order", None)

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text("Індивідуальне замовлення скасовано.")
    elif update.message:
        await update.message.reply_text("Індивідуальне замовлення скасовано.")

    return ConversationHandler.END
