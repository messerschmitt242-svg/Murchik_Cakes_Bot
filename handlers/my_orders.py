from telegram import Update
from telegram.ext import ContextTypes

from database.orders_db import get_user_orders, format_items


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = get_user_orders(update.effective_user.id)

    if not orders:
        await update.message.reply_text("У вас немає замовлень 🍰")
        return

    text = "📦 Ваші замовлення:\n\n"

    for order in orders:
        text += f"""
Замовлення #{order['id']}
📊 Статус: {order['status']}
💰 Сума: {float(order['total'] or 0):.2f} zł

{format_items(order['items'])}
------------------
"""

    await update.message.reply_text(text)
