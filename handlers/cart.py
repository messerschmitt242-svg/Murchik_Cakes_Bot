from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from database.cart_db import (
    add_to_cart_db,
    get_cart_items_db,
    change_cart_qty_db,
    remove_from_cart_db,
    clear_cart_db,
    apply_promo_to_cart_item,
    apply_promo_to_cart,
)
from database.orders_db import create_order
from keyboards.main_menu import get_main_menu
from handlers.cleanup import delete_callback_message
from handlers.admin_notify import notify_admins_text, admin_contact_keyboard
from locales import tr
from services.calendar_links import google_calendar_order_url
from services.google_tasks import create_google_task_for_order, TASKS_HOME_URL

CART_NAME = 200
CART_PHONE = 201
PROMO_CODE = 202


def _format_cart(user_id: int):
    items, total, total_before_discount, total_discount = get_cart_items_db(user_id)
    if not items:
        return tr(user_id, "cart_empty"), None

    text = tr(user_id, "cart_title")
    keyboard = []

    keyboard.append([InlineKeyboardButton("🎁 Промокод на всю корзину", callback_data="cart_promo_all")])

    for item in items:
        text += f"• {item['name']} x{item['qty']} = {item['final_subtotal']:.2f} zł\n"
        if item.get("discount_percent"):
            text += f"  Промо {item['promo_code']}: -{item['discount_percent']}%\n"
        keyboard.append([
            InlineKeyboardButton("➕", callback_data=f"cart_plus_{item['product_id']}"),
            InlineKeyboardButton("➖", callback_data=f"cart_minus_{item['product_id']}"),
            InlineKeyboardButton("🗑️", callback_data=f"cart_del_{item['product_id']}"),
            InlineKeyboardButton("🎁 Промо товару", callback_data=f"cart_promo_{item['product_id']}"),
        ])

    if total_discount > 0:
        text += f"\nСума без знижки: {total_before_discount:.2f} zł"
        text += f"\nЗнижка: -{total_discount:.2f} zł"
    text += f"\n💰 Разом: {total:.2f} zł"

    keyboard.append([InlineKeyboardButton(tr(user_id, "checkout"), callback_data="cart_checkout")])
    keyboard.append([InlineKeyboardButton(tr(user_id, "home_button"), callback_data="home_inline")])
    return text, InlineKeyboardMarkup(keyboard)


async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    product_id = int(query.data.split("_")[1])
    add_to_cart_db(user_id, product_id)
    chat_id = query.message.chat_id
    await delete_callback_message(query)
    await context.bot.send_message(chat_id=chat_id, text=tr(user_id, "cart_added"))


async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text, keyboard = _format_cart(user_id)
    await update.message.reply_text(text, reply_markup=keyboard)


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
    if query.data == "cart_promo_all":
        context.user_data["promo_scope"] = "cart"
        context.user_data.pop("promo_product_id", None)
    else:
        product_id = int(query.data.split("_")[-1])
        context.user_data["promo_scope"] = "item"
        context.user_data["promo_product_id"] = product_id
    chat_id = query.message.chat_id
    await delete_callback_message(query)
    await context.bot.send_message(chat_id=chat_id, text=tr(query.from_user.id, "enter_promo"))
    return PROMO_CODE


async def promo_apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    code = update.message.text.strip()
    scope = context.user_data.get("promo_scope", "item")

    if scope == "cart":
        success, applied_count, discount = apply_promo_to_cart(user_id, code)
        context.user_data.pop("promo_scope", None)
        if not success:
            await update.message.reply_text(tr(user_id, "promo_not_found"))
            return ConversationHandler.END
        await update.message.reply_text(f"{tr(user_id, 'promo_applied')} -{discount}%\nЗастосовано до товарів: {applied_count}")
    else:
        product_id = context.user_data.get("promo_product_id")
        if not product_id:
            await update.message.reply_text(tr(user_id, "promo_missing_product"))
            return ConversationHandler.END
        success, discount = apply_promo_to_cart_item(user_id, product_id, code)
        context.user_data.pop("promo_product_id", None)
        context.user_data.pop("promo_scope", None)
        if not success:
            await update.message.reply_text(tr(user_id, "promo_not_found"))
            return ConversationHandler.END
        await update.message.reply_text(f"{tr(user_id, 'promo_applied')} -{discount}%")

    text, keyboard = _format_cart(user_id)
    await update.message.reply_text(text, reply_markup=keyboard)
    return ConversationHandler.END


async def promo_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("promo_product_id", None)
    context.user_data.pop("promo_scope", None)
    await update.message.reply_text(tr(update.effective_user.id, "cancel"))
    return ConversationHandler.END


async def checkout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    items, _, _, _ = get_cart_items_db(query.from_user.id)
    if not items:
        await query.message.reply_text(tr(query.from_user.id, "cart_empty"))
        return ConversationHandler.END
    chat_id = query.message.chat_id
    await delete_callback_message(query)
    await context.bot.send_message(chat_id=chat_id, text=tr(query.from_user.id, "name_prompt"))
    return CART_NAME


async def checkout_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["checkout_name"] = update.message.text.strip()
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(tr(update.effective_user.id, "share_phone"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(tr(update.effective_user.id, "phone_prompt"), reply_markup=keyboard)
    return CART_PHONE


async def checkout_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone = update.message.contact.phone_number if update.message.contact else update.message.text.strip()
    name = context.user_data.get("checkout_name", "Клієнт")
    items, total, _, _ = get_cart_items_db(user_id)
    if not items:
        await update.message.reply_text(tr(user_id, "cart_empty"), reply_markup=get_main_menu(user_id))
        return ConversationHandler.END

    order_id = create_order(user_id=user_id, name=name, phone=phone, items=items, total=total)
    clear_cart_db(user_id)
    context.user_data.pop("checkout_name", None)

    items_text = "\n".join(
        f"• {item['name']} x{item['qty']} = {item['final_subtotal']:.2f} zł"
        + (f" ({item['promo_code']} -{item['discount_percent']}%)" if item.get("discount_percent") else "")
        for item in items
    )
    admin_text = f"""
🆕 Нове замовлення #{order_id}

Ім'я: {name}
Телефон: {phone}

Замовлення:
{items_text}

Разом: {total:.2f} zł
Статус: Створено
"""
    google_task = create_google_task_for_order(
        order_id=order_id,
        customer_name=name,
        phone=phone,
        items_text=items_text,
        total=total,
    )
    calendar_url = google_calendar_order_url(
        order_id=order_id,
        customer_name=name,
        phone=phone,
        items_text=items_text,
        total=total,
    )
    admin_buttons = [[InlineKeyboardButton("📋 Відкрити замовлення", callback_data=f"admin_order_{order_id}")]]
    if google_task:
        admin_buttons.append([InlineKeyboardButton("✅ Відкрити Google Tasks", url=TASKS_HOME_URL)])
        admin_text += "\nGoogle Tasks: ✅ задачу створено"
    else:
        admin_buttons.append([InlineKeyboardButton("📅 Додати в календар", url=calendar_url)])
        admin_text += "\nGoogle Tasks: ⚠️ задачу не створено"
    admin_keyboard = InlineKeyboardMarkup(admin_buttons)
    admin_notified = await notify_admins_text(context=context, text=admin_text, reply_markup=admin_keyboard)

    if admin_notified > 0:
        confirmation_text = tr(user_id, "order_created_ok").format(id=order_id)
    else:
        confirmation_text = tr(user_id, "order_created_no_admin").format(id=order_id)

    await update.message.reply_text(confirmation_text, reply_markup=ReplyKeyboardRemove())

    contact_keyboard = admin_contact_keyboard(user_id)
    if contact_keyboard:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=tr(user_id, "need_details"), reply_markup=contact_keyboard)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=tr(user_id, "home_menu"), reply_markup=get_main_menu(user_id))
    return ConversationHandler.END


async def checkout_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else None
    await update.message.reply_text("Оформлення скасовано.", reply_markup=get_main_menu(user_id))
    context.user_data.pop("checkout_name", None)
    return ConversationHandler.END
