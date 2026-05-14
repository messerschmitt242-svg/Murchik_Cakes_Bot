from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_conn
from config import ADMIN_ID


STATUSES = [
    "Прийнято",
    "Готується",
    "Готове до видачі",
    "Завершено"
]

async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT id, product, status FROM orders")
    orders = cursor.fetchall()
    conn.close()

    text = "📦 ВСІ ЗАМОВЛЕННЯ:\n\n"

    for o in orders:
        text += f"ID: {o[0]} | {o[1]} | {o[2]}\n"

    text += "\nЩоб змінити статус: /set_status ID СТАТУС"

    await update.message.reply_text(text)
    
async def set_status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    try:
        order_id = int(context.args[0])
        new_status = " ".join(context.args[1:])
    except:
        await update.message.reply_text("Формат: /set_status ID Статус")
        return

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET status = ?
        WHERE id = ?
    """, (new_status, order_id))

    conn.commit()
    conn.close()

    await update.message.reply_text("✅ Статус оновлено")
