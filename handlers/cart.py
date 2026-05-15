from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from database.cart_db import (
    add_to_cart_db,
    get_cart_items_db,
    change_cart_qty_db,
    remove_from_cart_db,
    clear_cart_db,
    apply_promo_to_cart_item,
)
from database.orders_db import create_order
from keyboards.main_menu import get_main_menu
from handlers.cleanup import delete_callback_message
from handlers.home import HOME_BUTTON_TEXT
from handlers.admin_notify import notify_admins_text, admin_contact_keyboard

CART_NAME = 200
CART_PHONE = 201
PROMO_CODE = 202


def _format_cart(user_id: int):
    items, total, total_before_discount, total_discount = get_cart_items_db(user_id)

    if not items:
        return "Кошик порожній 🛒", None

    text = "🛒 Ваш кошик:\n\n"
    keyboard = []

    for item in items:
        text += f"• {item['name']} x{item['qty']} = {item['final_subtotal']:.2f} zł\n"
        if item.get("discount_percent"):
            text += f"  🎟 Промо {item['promo_code']}: -{item['discount_percent']}%\n"

        keyboard.append([
            InlineKeyboardButton("➕", callback_data=f"cart_plus_{item['product_id']}"),
            InlineKeyboardButton("➖", callback_data=f"cart_minus_{item['product_id']}"),
            InlineKeyboardButton("🗑", callback_data=f"cart_del_{item['product_id']}"),
            InlineKeyboardButton("🎟 Промо", callback_data=f"cart_promo_{item['product_id']}"),
        ])

    if total_discount > 0:
        text += f"\nСума без знижки: {total_before_discount:.2f} zł"
        text += f"\nЗнижка: -{total_discount:.2f} zł"
    text += f"\n💰 Разом: {total:.2f} zł"

    keyboard.append([InlineKeyboardButton("📦 Оформити замовлення", callback_data="cart_checkout")])
    keyboard.append([InlineKeyboardButton(HOME_BUTTON_TEXT, callback_data="home_inline")])

    return text, InlineKeyboardMarkup(keyboard)


async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    product_id = int(query.data.split("_")[1])

    add_to_cart_db(user_id, product_id)

    chat_id = query.message.chat_id
    await delete_callback_message(query)

    await context.bot.send_message(
        chat_id=chat_id,
        text="✅ Додано у кошик 🛒"
    )


async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text, keyboard = _format_cart(user_id)

    await update.message.reply_text(
        text,
        reply_markup=keyboard,
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


async def promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[-1])
    context.user_data["promo_product_id"] = product_id

    chat_id = query.message.chat_id
    await delete_callback_message(query)

    await context.bot.send_message(
        chat_id=chat_id,
        text="Введіть промокод для цього товару:"
    )
    return PROMO_CODE


async def promo_apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    product_id = context.user_data.get("promo_product_id")
    code = update.message.text.strip()

    if not product_id:
        await update.message.reply_text("Помилка: товар не обрано.")
        return ConversationHandler.END

    success, discount = apply_promo_to_cart_item(user_id, product_id, code)
    context.user_data.pop("promo_product_id", None)

    if not success:
        await update.message.reply_text("❌ Промокод не знайдено або він неактивний.")
        return ConversationHandler.END

    await update.message.reply_text(f"✅ Промокод застосовано: -{discount}%")
    text, keyboard = _format_cart(user_id)
    await update.message.reply_text(text, reply_markup=keyboard)

    return ConversationHandler.END


async def promo_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("promo_product_id", None)
    await update.message.reply_text("Введення промокоду скасовано.")
    return ConversationHandler.END


async def checkout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    items, _, _, _ = get_cart_items_db(query.from_user.id)

    if not items:
        await query.message.reply_text("Кошик порожній 🛒")
        return ConversationHandler.END

    chat_id = query.message.chat_id
    await delete_callback_message(query)

    await context.bot.send_message(
        chat_id=chat_id,
        text="Ваше ім'я:"
    )
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
        reply_markup=keyboard,
    )

    return CART_PHONE


async def checkout_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    name = context.user_data.get("checkout_name", "Клієнт")
    items, total, _, _ = get_cart_items_db(user_id)

    if not items:
        await update.message.reply_text("Кошик порожній 🛒", reply_markup=get_main_menu(user_id))
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
        f"• {item['name']} x{item['qty']} = {item['final_subtotal']:.2f} zł"
        + (f" ({item['promo_code']} -{item['discount_percent']}%)" if item.get("discount_percent") else "")
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

    admin_notified = await notify_admins_text(
        context=context,
        text=admin_text,
    )

    if admin_notified > 0:
        confirmation_text = f"✅ Замовлення #{order_id} прийнято.\nМи скоро з вами зв'яжемося ❤️"
    else:
        confirmation_text = (
            f"✅ Замовлення #{order_id} створено.\n"
            "Адміністратор може побачити його в панелі активних замовлень."
        )

    await update.message.reply_text(
        confirmation_text,
        reply_markup=ReplyKeyboardRemove(),
    )

    contact_keyboard = admin_contact_keyboard()
    if contact_keyboard:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Потрібно уточнити деталі?",
            reply_markup=contact_keyboard,
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Головне меню 🍰",
        reply_markup=get_main_menu(user_id),
    )

    return ConversationHandler.END


async def checkout_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else None
    await update.message.reply_text("Оформлення скасовано.", reply_markup=get_main_menu(user_id))
    context.user_data.pop("checkout_name", None)
    return ConversationHandler.END
