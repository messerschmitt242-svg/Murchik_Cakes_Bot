from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_ID
from database.orders_db import get_all_orders, update_order_status, format_items

STATUSES = [
    "Прийнято",
    "Готується",
    "Готове до видачі",
    "Завершено",
]


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
        await update.message.reply_text(
            "Невірний статус. Доступні:\n" + "\n".join(STATUSES)
        )
        return

    changed = update_order_status(order_id, new_status)

    if changed:
        await update.message.reply_text("✅ Статус оновлено")
    else:
        await update.message.reply_text("❌ Замовлення не знайдено")
