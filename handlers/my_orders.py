import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.orders_db import get_user_orders, get_order, format_order_details, can_cancel_order
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
        "Скасовано": "status_cancelled",
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
📊 {tr(user_id, "status_label")} {_status(user_id, order['status'])}
💰 {tr(user_id, "sum_label")} {float(order['total'] or 0):.2f} zł
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

        if can_cancel_order(order["status"]):
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ Скасувати замовлення #{order['id']}",
                    callback_data=f"user_cancel_order_{order['id']}"
                )
            ])

    for order in custom_orders:
        text += f"""
{tr(user_id, "custom_order_label")} C#{order['id']}
📊 {tr(user_id, "status_label")} {_status(user_id, order['status'])}
🧁 {tr(user_id, "base_dessert_label")} {order['product_name'] or '—'}
📅 {tr(user_id, "date_label")} {order['date']}

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


async def show_user_cancel_order_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[-1])
    order = get_order(order_id)

    if not order or int(order["user_id"]) != int(query.from_user.id):
        await query.message.reply_text("Замовлення не знайдено.")
        return

    if not can_cancel_order(order["status"]):
        await query.message.reply_text("Це замовлення вже не можна скасувати через бот. Будь ласка, звʼяжіться з нами.")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📍 Перейти в контакти", callback_data="user_cancel_contacts")],
        [InlineKeyboardButton("✖️ Закрити", callback_data="user_cancel_close")],
    ])

    await query.message.reply_text(
        "❗ Щоб скасувати замовлення, будь ласка, звʼяжіться з нами за номером телефону.\n\n"
        "Адміністратор перевірить замовлення і скасує його вручну.",
        reply_markup=keyboard,
    )


async def show_user_cancel_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(query.from_user.id, "route_button"), url="https://maps.app.goo.gl/7YLX42TMak4FdaXm9")],
        [InlineKeyboardButton("✖️ Закрити", callback_data="user_cancel_close")],
    ])
    await query.message.reply_text(
        tr(query.from_user.id, "contacts_text"),
        reply_markup=keyboard,
    )


async def close_user_cancel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except Exception:
        await query.message.edit_reply_markup(reply_markup=None)
