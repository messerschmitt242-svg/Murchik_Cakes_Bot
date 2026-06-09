from io import BytesIO

from telegram import InputFile, Update
from telegram.ext import ContextTypes

from config import is_admin
from database.orders_db import get_order, format_items
from services.calendar_links import build_order_ics


def _row_get(row, key: str, default: str = ""):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
        if isinstance(row, dict):
            return row.get(key, default)
    except Exception:
        pass
    return default


async def send_order_calendar_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id if update.effective_user else 0
    if not is_admin(user_id):
        await query.answer("Недостатньо прав", show_alert=True)
        return

    try:
        order_id = int(query.data.rsplit("_", 1)[1])
    except Exception:
        await query.message.reply_text("Не вдалося визначити номер замовлення.")
        return

    order = get_order(order_id)
    if not order:
        await query.message.reply_text("Замовлення не знайдено.")
        return

    items_text = format_items(_row_get(order, "items", "[]"))
    ics = build_order_ics(
        order_id=int(_row_get(order, "id", order_id)),
        customer_name=_row_get(order, "name", ""),
        phone=_row_get(order, "phone", ""),
        items_text=items_text,
        total=float(_row_get(order, "total", 0) or 0),
        order_date=_row_get(order, "order_date", ""),
        delivery_method=_row_get(order, "delivery_method", ""),
        payment_method=_row_get(order, "payment_method", ""),
        comment=_row_get(order, "comment", ""),
    )

    bio = BytesIO(ics.encode("utf-8"))
    bio.name = f"murchik-order-{order_id}.ics"
    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=InputFile(bio, filename=bio.name),
        caption=(
            f"📅 Файл календаря для замовлення #{order_id}.\n"
            "На iPhone відкрий файл і вибери додавання в Календар."
        ),
    )
