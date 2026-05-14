from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_conn


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, product, status FROM orders
        WHERE user_id = ?
    """, (user_id,))

    orders = cursor.fetchall()
    conn.close()

    if not orders:
        await update.message.reply_text("У вас немає замовлень 🍰")
        return

    text = "📦 Ваші замовлення:\n\n"

    for o in orders:
        text += f"""
ID: {o[0]}
🍰 {o[1]}
📊 Статус: {o[2]}
------------------
"""

    await update.message.reply_text(text)
