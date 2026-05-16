import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.orders_db import get_user_orders, format_order_details
from database.custom_orders_db import get_user_custom_orders
from handlers.pickup import PICKUP_READY_STATUS
from locales import tr
from utils_translation import translate_product_name_raw
from database.user_settings_db import get_user_language


def _status(user_id: int, status: str) -> str:
    mapping = {
        "Прийнято": "status_accepted",
        "Готується": "status_cooking",
        "Готове до видачі": "status_ready",
        "Завершено": "status_done",
    }
    key = mapping.get(status)
    return tr(user_id, key) if key else status



def _format_items_for_user(raw_items: str, user_id: int) -> str:
    try:
        items = json.loads(raw_items or "[]")
    except Exception:
        return raw_items or "—"

    if not items:
        return "—"

    lang = get_user_language(user_id)
    promo_label = {
        "ua": "промо",
        "ru": "промо",
        "pl": "promo",
        "en": "promo",
    }.get(lang, "promo")

    result = []
    for item in items:
        name = translate_product_name_raw(item.get("name", "Товар"), lang)
        qty = item.get("qty", 1)
        total = item.get("final_subtotal", item.get("subtotal", 0))
        line = f"• {name} x{qty} — {total:.2f} zł"
        if item.get("promo_code"):
            line += f"\n  {promo_label}: {item.get('promo_code')} (-{item.get('discount_percent', 0)}%)"
        result.append(line)

    return "\n".join(result)


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    orders = get_user_orders(user_id)
    custom_orders = get_user_custom_orders(user_id)

    if not orders and not custom_orders:
        await update.message.reply_text(tr(user_id, "orders_empty"))
        return

    text = tr(user_id, "orders_title")
    keyboard = []

    for order in orders:
        text += f"""
{tr(user_id, "order_label")} #{order['id']}
{tr(user_id, "status_label")} {_status(user_id, order['status'])}
{tr(user_id, "sum_label")} {float(order['total'] or 0):.2f} zł
{format_order_details(order)}

{_format_items_for_user(order['items'], user_id)}
------------------
"""

        if order["status"] == PICKUP_READY_STATUS:
            keyboard.append([
                InlineKeyboardButton(
                    f"{tr(user_id, 'pickup_button')} #{order['id']}",
                    callback_data=f"pickup_order_{order['id']}"
                )
            ])

    for order in custom_orders:
        text += f"""
{tr(user_id, "custom_order_label")} C#{order['id']}
{tr(user_id, "status_label")} {_status(user_id, order['status'])}
{tr(user_id, "base_dessert_label")} {order['product_name'] or '—'}
{tr(user_id, "date_label")} {order['date']}

{order['description']}
------------------
"""

        if order["status"] == PICKUP_READY_STATUS:
            keyboard.append([
                InlineKeyboardButton(
                    f"{tr(user_id, 'pickup_button')} C#{order['id']}",
                    callback_data=f"pickup_custom_order_{order['id']}"
                )
            ])

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
    )
