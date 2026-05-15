from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.orders_db import get_user_orders, format_items
from database.custom_orders_db import get_user_custom_orders
from handlers.pickup import PICKUP_READY_STATUS


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    orders = get_user_orders(user_id)
    custom_orders = get_user_custom_orders(user_id)

    if not orders and not custom_orders:
        await update.message.reply_text("У вас немає замовлень 🍰")
        return

    text = "📦 Ваші замовлення:\n\n"
    keyboard = []

    for order in orders:
        text += f"""
Замовлення #{order['id']}
📊 Статус: {order['status']}
💰 Сума: {float(order['total'] or 0):.2f} zł

{format_items(order['items'])}
------------------
"""

        if order["status"] == PICKUP_READY_STATUS:
            keyboard.append([
                InlineKeyboardButton(
                    f"📍 Як отримати замовлення #{order['id']}",
                    callback_data=f"pickup_order_{order['id']}"
                )
            ])

    for order in custom_orders:
        text += f"""
Індивідуальне замовлення C#{order['id']}
📊 Статус: {order['status']}
🎂 Базовий десерт: {order['product_name'] or '—'}
📅 Дата: {order['date']}

{order['description']}
------------------
"""

        if order["status"] == PICKUP_READY_STATUS:
            keyboard.append([
                InlineKeyboardButton(
                    f"📍 Як отримати замовлення C#{order['id']}",
                    callback_data=f"pickup_custom_order_{order['id']}"
                )
            ])

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
    )
