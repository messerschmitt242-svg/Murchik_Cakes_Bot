from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import ADMIN_ID
from database.orders_db import (
    STATUSES,
    get_all_orders,
    get_active_orders,
    get_order,
    update_order_status,
    format_items,
    next_status,
)


async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
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

    text += "\nЗміна статусу:\n/set_status ID Статус\n\nНаприклад:\n/set_status 3 Готується"

    await update.message.reply_text(text)


async def set_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
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


def _active_orders_keyboard(orders):
    keyboard = []
    for order in orders:
        keyboard.append([
            InlineKeyboardButton(
                f"#{order['id']} — {order['name']} — {order['status']}",
                callback_data=f"admin_order_{order['id']}",
            )
        ])
    return InlineKeyboardMarkup(keyboard)


async def active_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Цей розділ доступний тільки адміністратору.")
        return

    orders = get_active_orders()
    if not orders:
        await update.message.reply_text("Активних замовлень немає ✅")
        return

    await update.message.reply_text(
        "📋 Активні замовлення:",
        reply_markup=_active_orders_keyboard(orders),
    )


async def show_admin_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.message.reply_text("Недоступно.")
        return

    order_id = int(query.data.split("_")[-1])
    order = get_order(order_id)

    if not order:
        await query.message.reply_text("Замовлення не знайдено.")
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

    await query.message.reply_text(text, reply_markup=keyboard)


async def advance_order_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.message.reply_text("Недоступно.")
        return

    order_id = int(query.data.split("_")[-1])
    order = get_order(order_id)

    if not order:
        await query.message.reply_text("Замовлення не знайдено.")
        return

    next_value, _ = next_status(order["status"])
    if not next_value:
        await query.message.reply_text("Замовлення вже завершено.")
        return

    update_order_status(order_id, next_value)
    await query.message.reply_text(f"✅ Статус замовлення #{order_id} змінено на: {next_value}")

    refreshed = get_order(order_id)
    next_next_value, button_text = next_status(refreshed["status"])
    if next_next_value:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(button_text, callback_data=f"admin_next_status_{order_id}")]
        ])
        await query.message.reply_text("Наступна дія:", reply_markup=keyboard)
