from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID
from database.cart_db import (
    add_to_cart_db,
    get_cart_items_db,
    change_cart_qty_db,
    remove_from_cart_db,
    clear_cart_db,
)
from database.orders_db import create_order
from keyboards.main_menu import main_menu

CART_NAME = 200
CART_PHONE = 201


def _format_cart(user_id: int):
    items, total = get_cart_items_db(user_id)

    if not items:
        return "Кошик порожній 🛒", None

    text = "🛒 Ваш кошик:\n\n"
    keyboard = []

    for item in items:
        text += f"• {item['name']} x{item['qty']} = {item['subtotal']:.2f} zł\n"
        keyboard.append([
            InlineKeyboardButton("➕", callback_data=f"cart_plus_{item['product_id']}"),
            InlineKeyboardButton("➖", callback_data=f"cart_minus_{item['product_id']}"),
            InlineKeyboardButton("🗑", callback_data=f"cart_del_{item['product_id']}"),
        ])

    text += f"\n💰 Разом: {total:.2f} zł"
    keyboard.append([InlineKeyboardButton("📦 Оформити замовлення", callback_data="cart_checkout")])

    return text, InlineKeyboardMarkup(keyboard)


async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    product_id = int(query.data.split("_")[1])

    add_to_cart_db(user_id, product_id)

    await query.message.reply_text("✅ Додано у кошик 🛒")


async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text, keyboard = _format_cart(user_id)

    await update.message.reply_text(
        text,
        reply_markup=keyboard
    )


async def plus_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    product_id = int(query.data.split("_")[-1])
    change_cart_qty_db(user_id, product_id, +1)

    text, keyboard = _format_cart(user_id)
    await query.message.edit_text(text, reply_markup=keyboard)


async def minus_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    product_id = int(query.data.split("_")[-1])
    change_cart_qty_db(user_id, product_id, -1)

    text, keyboard = _format_cart(user_id)
    await query.message.edit_text(text, reply_markup=keyboard)


async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    product_id = int(query.data.split("_")[-1])
    remove_from_cart_db(user_id, product_id)

    text, keyboard = _format_cart(user_id)
    await query.message.edit_text(text, reply_markup=keyboard)


async def checkout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    items, _ = get_cart_items_db(query.from_user.id)

    if not items:
        await query.message.reply_text("Кошик порожній 🛒")
        return ConversationHandler.END

    await query.message.reply_text("Ваше ім'я:")
    return CART_NAME


async def checkout_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["checkout_name"] = update.message.text.strip()

    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Надіслати номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await update.message.reply_text(
        "Надішліть ваш номер телефону:",
        reply_markup=keyboard
    )

    return CART_PHONE


async def checkout_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    name = context.user_data.get("checkout_name", "Клієнт")
    items, total = get_cart_items_db(user_id)

    if not items:
        await update.message.reply_text("Кошик порожній 🛒", reply_markup=main_menu)
        return ConversationHandler.END

    order_id = create_order(
        user_id=user_id,
        name=name,
        phone=phone,
        items=items,
        total=total,
    )

    clear_cart_db(user_id)
    context.user_data.pop("checkout_name", None)

    items_text = "\n".join(
        f"• {item['name']} x{item['qty']} = {item['subtotal']:.2f} zł"
        for item in items
    )

    admin_text = f"""
Нове замовлення #{order_id} 🎂

Ім'я: {name}
Телефон: {phone}

Замовлення:
{items_text}

Разом: {total:.2f} zł
Статус: Прийнято
"""

    if ADMIN_ID:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text
        )

    await update.message.reply_text(
        f"✅ Замовлення #{order_id} прийнято.\nМи скоро з вами зв'яжемося ❤️",
        reply_markup=main_menu
    )

    return ConversationHandler.END


async def checkout_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оформлення скасовано.", reply_markup=main_menu)
    context.user_data.pop("checkout_name", None)
    return ConversationHandler.END
