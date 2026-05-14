from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import is_admin
from handlers.cleanup import delete_callback_message
from database.orders_db import (
    STATUSES,
    get_all_orders,
    get_active_orders,
    get_order,
    update_order_status,
    format_items,
    next_status,
)
from database.custom_orders_db import (
    get_active_custom_orders,
    get_custom_order,
    update_custom_order_status,
    next_custom_status,
)


async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    orders = get_all_orders()

    if not orders:
        await update.message.reply_text("Замовлень поки немає 📦")
        return

    text = "📦 ВСІ ЗАМОВЛЕННЯ:\n\n"

    for order in orders:
        text += f"""
ID: {order['id']}
Клієнт: {order['name']}
Телефон: {order['phone']}
Статус: {order['status']}
Сума: {float(order['total'] or 0):.2f} zł
{format_items(order['items'])}
------------------
"""

    await update.message.reply_text(text)


async def set_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 2:
        await update.message.reply_text("Формат: /set_status ID Статус")
        return

    try:
        order_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID має бути числом.")
        return

    new_status = " ".join(context.args[1:]).strip()

    if new_status not in STATUSES:
        await update.message.reply_text("Невірний статус. Доступні:\n" + "\n".join(STATUSES))
        return

    changed = update_order_status(order_id, new_status)

    if changed:
        await update.message.reply_text("✅ Статус оновлено")
    else:
        await update.message.reply_text("❌ Замовлення не знайдено")


def _active_orders_keyboard(regular_orders, custom_orders):
    keyboard = []

    for order in regular_orders:
        keyboard.append([
            InlineKeyboardButton(
                f"#{order['id']} — {order['name']} — {order['status']}",
                callback_data=f"admin_order_{order['id']}",
            )
        ])

    for order in custom_orders:
        keyboard.append([
            InlineKeyboardButton(
                f"C#{order['id']} — {order['name']} — {order['status']}",
                callback_data=f"admin_custom_order_{order['id']}",
            )
        ])

    return InlineKeyboardMarkup(keyboard)


async def active_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Цей розділ доступний тільки адміністратору.")
        return

    regular_orders = get_active_orders()
    custom_orders = get_active_custom_orders()

    if not regular_orders and not custom_orders:
        await update.message.reply_text("Активних замовлень немає ✅")
        return

    await update.message.reply_text(
        "📋 Активні замовлення:",
        reply_markup=_active_orders_keyboard(regular_orders, custom_orders),
    )


async def show_admin_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return

    order_id = int(query.data.split("_")[-1])
    order = get_order(order_id)

    chat_id = query.message.chat_id
    await delete_callback_message(query)

    if not order:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Замовлення не знайдено."
        )
        return

    next_value, button_text = next_status(order["status"])

    text = f"""
📦 Замовлення #{order['id']}

Клієнт: {order['name']}
Телефон: {order['phone']}
Дата: {order['created_at']}
Статус: {order['status']}
Сума: {float(order['total'] or 0):.2f} zł

{format_items(order['items'])}
"""

    keyboard = None
    if next_value:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(button_text, callback_data=f"admin_next_status_{order['id']}")]
        ])

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard
    )


async def show_admin_custom_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return

    order_id = int(query.data.split("_")[-1])
    order = get_custom_order(order_id)

    chat_id = query.message.chat_id
    await delete_callback_message(query)

    if not order:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Індивідуальне замовлення не знайдено."
        )
        return

    next_value, button_text = next_custom_status(order["status"])

    text = f"""
🎂 Індивідуальне замовлення C#{order['id']}

Клієнт: {order['name']}
Телефон: {order['phone']}
Дата видачі: {order['date']}
Створено: {order['created_at']}
Статус: {order['status']}
Базовий десерт: {order['product_name'] or '—'}

Опис:
{order['description']}
"""

    keyboard = None
    if next_value:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(button_text, callback_data=f"admin_next_custom_status_{order['id']}")]
        ])

    if order["photo"]:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=order["photo"],
            caption=text,
            reply_markup=keyboard,
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
        )


async def advance_order_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return

    order_id = int(query.data.split("_")[-1])
    order = get_order(order_id)

    chat_id = query.message.chat_id
    await delete_callback_message(query)

    if not order:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Замовлення не знайдено."
        )
        return

    next_value, _ = next_status(order["status"])
    if not next_value:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Замовлення вже завершено."
        )
        return

    update_order_status(order_id, next_value)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Статус замовлення #{order_id} змінено на: {next_value}"
    )

    refreshed = get_order(order_id)
    next_next_value, button_text = next_status(refreshed["status"])
    if next_next_value:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(button_text, callback_data=f"admin_next_status_{order_id}")]
        ])
        await context.bot.send_message(
            chat_id=chat_id,
            text="Наступна дія:",
            reply_markup=keyboard
        )


async def advance_custom_order_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return

    order_id = int(query.data.split("_")[-1])
    order = get_custom_order(order_id)

    chat_id = query.message.chat_id
    await delete_callback_message(query)

    if not order:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Індивідуальне замовлення не знайдено."
        )
        return

    next_value, _ = next_custom_status(order["status"])
    if not next_value:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Замовлення вже завершено."
        )
        return

    update_custom_order_status(order_id, next_value)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Статус індивідуального замовлення C#{order_id} змінено на: {next_value}"
    )

    refreshed = get_custom_order(order_id)
    next_next_value, button_text = next_custom_status(refreshed["status"])
    if next_next_value:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(button_text, callback_data=f"admin_next_custom_status_{order_id}")]
        ])
        await context.bot.send_message(
            chat_id=chat_id,
            text="Наступна дія:",
            reply_markup=keyboard
        )
