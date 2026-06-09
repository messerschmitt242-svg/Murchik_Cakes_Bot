from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import is_admin
from handlers.cleanup import delete_callback_message
from handlers.pickup import PICKUP_READY_STATUS, pickup_button, send_pickup_info_to_chat
from database.orders_db import (
    STATUSES,
    get_all_orders,
    count_all_orders,
    get_active_orders,
    get_order,
    update_order_status,
    delete_cancelled_order,
    format_items,
    next_status,
)
from database.custom_orders_db import (
    get_active_custom_orders,
    get_custom_order,
    update_custom_order_status,
    delete_cancelled_custom_order,
    next_custom_status,
)
from services.google_tasks import create_google_task_for_order, TASKS_HOME_URL

ORDERS_PAGE_SIZE = 10
FINAL_STATUSES = ("Завершено", "Скасовано")


def _row_get(row, key: str, default=""):
    try:
        if hasattr(row, "keys") and key in row.keys():
            value = row[key]
            return default if value is None else value
        value = row[key]
        return default if value is None else value
    except Exception:
        return default


def _orders_page_keyboard(orders, page: int, total: int):
    keyboard = []
    for order in orders:
        keyboard.append([
            InlineKeyboardButton(
                f"#{order['id']} — {order['name']} — {order['status']} — {float(order['total'] or 0):.2f} zł",
                callback_data=f"admin_order_{order['id']}",
            )
        ])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"admin_orders_page_{page - 1}"))
    if (page + 1) * ORDERS_PAGE_SIZE < total:
        nav.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"admin_orders_page_{page + 1}"))
    if nav:
        keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)


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


def _order_keyboard(order):
    keyboard = []
    next_value, button_text = next_status(order["status"])
    if next_value:
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"admin_next_status_{order['id']}")])
    if order["status"] not in FINAL_STATUSES:
        keyboard.append([InlineKeyboardButton("➕ Додати у Tasks", callback_data=f"admin_add_tasks_order_{order['id']}")])
        keyboard.append([InlineKeyboardButton("❌ Скасувати замовлення", callback_data=f"admin_cancel_order_{order['id']}")])
    if order["status"] == "Скасовано":
        keyboard.append([InlineKeyboardButton("🗑️ Видалити замовлення", callback_data=f"admin_delete_order_{order['id']}")])
    return InlineKeyboardMarkup(keyboard) if keyboard else None


def _custom_order_keyboard(order):
    keyboard = []
    next_value, button_text = next_custom_status(order["status"])
    if next_value:
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"admin_next_custom_status_{order['id']}")])
    if order["status"] not in FINAL_STATUSES:
        keyboard.append([InlineKeyboardButton("➕ Додати у Tasks", callback_data=f"admin_add_tasks_custom_order_{order['id']}")])
        keyboard.append([InlineKeyboardButton("❌ Скасувати замовлення", callback_data=f"admin_cancel_custom_order_{order['id']}")])
    if order["status"] == "Скасовано":
        keyboard.append([InlineKeyboardButton("🗑️ Видалити замовлення", callback_data=f"admin_delete_custom_order_{order['id']}")])
    return InlineKeyboardMarkup(keyboard) if keyboard else None


async def _notify_order_status(context: ContextTypes.DEFAULT_TYPE, order, new_status: str):
    user_id = int(_row_get(order, "user_id", 0) or 0)
    order_id = _row_get(order, "id", "")
    if not user_id:
        return
    try:
        if new_status == PICKUP_READY_STATUS:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📦 Ваше замовлення №{order_id} готове до видачі.",
                reply_markup=pickup_button(f"pickup_order_{order_id}", user_id),
            )
            await send_pickup_info_to_chat(context=context, chat_id=user_id, user_id=user_id)
        elif new_status == "Прийнято":
            await context.bot.send_message(chat_id=user_id, text=f"✅ Ваше замовлення №{order_id} прийнято в роботу.")
        elif new_status == "Готується":
            await context.bot.send_message(chat_id=user_id, text=f"👨‍🍳 Ваше замовлення №{order_id} готується.")
        elif new_status == "Завершено":
            await context.bot.send_message(chat_id=user_id, text=f"🎉 Ваше замовлення №{order_id} успішно завершено.\nДякуємо за замовлення в Murchik Cakes!")
        elif new_status == "Скасовано":
            await context.bot.send_message(chat_id=user_id, text=f"❌ Ваше замовлення №{order_id} було скасовано.\nЯкщо це сталося помилково, будь ласка, зв'яжіться з нами.")
        else:
            await context.bot.send_message(chat_id=user_id, text=f"📦 Статус вашого замовлення #{order_id} змінено: {new_status}")
    except Exception as exc:
        print(f"CUSTOMER STATUS NOTIFY ERROR order #{order_id}: {exc}")


async def _notify_custom_order_status(context: ContextTypes.DEFAULT_TYPE, order, new_status: str):
    user_id = int(_row_get(order, "user_id", 0) or 0)
    order_id = _row_get(order, "id", "")
    if not user_id:
        return
    try:
        if new_status == PICKUP_READY_STATUS:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📦 Ваше індивідуальне замовлення C№{order_id} готове до видачі.",
                reply_markup=pickup_button(f"pickup_custom_order_{order_id}", user_id),
            )
            await send_pickup_info_to_chat(context=context, chat_id=user_id, user_id=user_id)
        elif new_status == "Прийнято":
            await context.bot.send_message(chat_id=user_id, text=f"✅ Ваше індивідуальне замовлення C№{order_id} прийнято в роботу.")
        elif new_status == "Готується":
            await context.bot.send_message(chat_id=user_id, text=f"👨‍🍳 Ваше індивідуальне замовлення C№{order_id} готується.")
        elif new_status == "Завершено":
            await context.bot.send_message(chat_id=user_id, text=f"🎉 Ваше індивідуальне замовлення C№{order_id} успішно завершено.\nДякуємо за замовлення в Murchik Cakes!")
        elif new_status == "Скасовано":
            await context.bot.send_message(chat_id=user_id, text=f"❌ Ваше індивідуальне замовлення C№{order_id} було скасовано.\nЯкщо це сталося помилково, будь ласка, зв'яжіться з нами.")
        else:
            await context.bot.send_message(chat_id=user_id, text=f"📦 Статус вашого індивідуального замовлення C#{order_id} змінено: {new_status}")
    except Exception as exc:
        print(f"CUSTOMER STATUS NOTIFY ERROR custom order C#{order_id}: {exc}")


def _create_google_task_from_order(order):
    items_text = format_items(order["items"])
    return create_google_task_for_order(
        order_id=int(order["id"]),
        customer_name=order["name"],
        phone=order["phone"],
        items_text=items_text,
        total=float(order["total"] or 0),
        order_date=_row_get(order, "order_date", ""),
        delivery_method=_row_get(order, "delivery_method", ""),
        payment_method=_row_get(order, "payment_method", ""),
        comment=_row_get(order, "comment", ""),
    )


def _create_google_task_from_custom_order(order):
    items_text = (
        f"Індивідуальне замовлення\n"
        f"Базовий десерт: {_row_get(order, 'product_name', '') or '—'}\n"
        f"Опис: {_row_get(order, 'description', '') or '—'}"
    )
    return create_google_task_for_order(
        order_id=int(order["id"]),
        customer_name=order["name"],
        phone=order["phone"],
        items_text=items_text,
        total=0,
        order_date=_row_get(order, "date", "") or _row_get(order, "order_date", ""),
        delivery_method=_row_get(order, "delivery_method", "Індивідуальне замовлення"),
        payment_method=_row_get(order, "payment_method", ""),
        comment=_row_get(order, "comment", ""),
    )


async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await _send_orders_page(update, context, page=0, edit=False)


async def orders_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    page = int(query.data.split("_")[-1])
    await _send_orders_page(update, context, page=page, edit=True)


async def _send_orders_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int, edit: bool):
    total = count_all_orders()
    if total == 0:
        text = "Замовлень поки немає 🧁"
        if edit:
            await update.callback_query.message.edit_text(text)
        else:
            await update.message.reply_text(text)
        return

    offset = page * ORDERS_PAGE_SIZE
    orders = get_all_orders(limit=ORDERS_PAGE_SIZE, offset=offset)
    max_page = (total - 1) // ORDERS_PAGE_SIZE
    text = f"📦 Усі замовлення — сторінка {page + 1}/{max_page + 1}\nОберіть замовлення:"
    keyboard = _orders_page_keyboard(orders, page, total)
    if edit:
        await update.callback_query.message.edit_text(text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text, reply_markup=keyboard)


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
        await update.message.reply_text("Невірний статус.\nДоступні:\n" + "\n".join(STATUSES))
        return
    order = get_order(order_id)
    changed = update_order_status(order_id, new_status)
    if changed and order:
        await _notify_order_status(context, order, new_status)
    await update.message.reply_text("✅ Статус оновлено" if changed else "❌ Замовлення не знайдено")


async def active_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Цей розділ доступний тільки адміністратору.")
        return
    regular_orders = get_active_orders()
    custom_orders = get_active_custom_orders()
    if not regular_orders and not custom_orders:
        await update.message.reply_text("Активних замовлень немає ✅")
        return
    await update.message.reply_text("📦 Активні замовлення:", reply_markup=_active_orders_keyboard(regular_orders, custom_orders))


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
        await context.bot.send_message(chat_id=chat_id, text="Замовлення не знайдено.")
        return
    text = f"""
📦 Замовлення #{order['id']}

Клієнт: {order['name']}
Телефон: {order['phone']}
Дата створення: {order['created_at']}
Дата видачі: {_row_get(order, 'order_date', '') or '—'}
Доставка: {_row_get(order, 'delivery_method', '') or '—'}
Оплата: {_row_get(order, 'payment_method', '') or '—'}
Коментар: {_row_get(order, 'comment', '') or '—'}
Статус: {order['status']}
Сума: {float(order['total'] or 0):.2f} zł

{format_items(order['items'])}
"""
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=_order_keyboard(order))


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
        await context.bot.send_message(chat_id=chat_id, text="Індивідуальне замовлення не знайдено.")
        return
    text = f"""
🎂 Індивідуальне замовлення C#{order['id']}

Клієнт: {order['name']}
Телефон: {order['phone']}
Дата видачі: {order['date']}
Створено: {order['created_at']}
Статус: {order['status']}
Базовий десерт: {order['product_name'] or '—'}

Опис: {order['description']}
"""
    if order["photo"]:
        await context.bot.send_photo(chat_id=chat_id, photo=order["photo"], caption=text, reply_markup=_custom_order_keyboard(order))
    else:
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=_custom_order_keyboard(order))


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
        await context.bot.send_message(chat_id=chat_id, text="Замовлення не знайдено.")
        return
    next_value, _ = next_status(order["status"])
    if not next_value:
        await context.bot.send_message(chat_id=chat_id, text="Замовлення вже завершено або скасовано.")
        return
    update_order_status(order_id, next_value)
    await _notify_order_status(context, order, next_value)
    await context.bot.send_message(chat_id=chat_id, text=f"✅ Статус замовлення #{order_id} змінено на: {next_value}")
    refreshed = get_order(order_id)
    if refreshed:
        await context.bot.send_message(chat_id=chat_id, text="Наступна дія:", reply_markup=_order_keyboard(refreshed))


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
        await context.bot.send_message(chat_id=chat_id, text="Індивідуальне замовлення не знайдено.")
        return
    next_value, _ = next_custom_status(order["status"])
    if not next_value:
        await context.bot.send_message(chat_id=chat_id, text="Замовлення вже завершено або скасовано.")
        return
    update_custom_order_status(order_id, next_value)
    await _notify_custom_order_status(context, order, next_value)
    await context.bot.send_message(chat_id=chat_id, text=f"✅ Статус індивідуального замовлення C#{order_id} змінено на: {next_value}")
    refreshed = get_custom_order(order_id)
    if refreshed:
        await context.bot.send_message(chat_id=chat_id, text="Наступна дія:", reply_markup=_custom_order_keyboard(refreshed))


async def add_order_to_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return
    order_id = int(query.data.split("_")[-1])
    order = get_order(order_id)
    chat_id = query.message.chat_id
    if not order:
        await context.bot.send_message(chat_id=chat_id, text="Замовлення не знайдено.")
        return
    task = _create_google_task_from_order(order)
    if task:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Замовлення #{order_id} додано у Google Tasks.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Відкрити Google Tasks", url=TASKS_HOME_URL)]]),
        )
    else:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Не вдалося додати замовлення у Google Tasks. Перевір підключення Google Tasks в адмінці/API логах.")


async def add_custom_order_to_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return
    order_id = int(query.data.split("_")[-1])
    order = get_custom_order(order_id)
    chat_id = query.message.chat_id
    if not order:
        await context.bot.send_message(chat_id=chat_id, text="Індивідуальне замовлення не знайдено.")
        return
    task = _create_google_task_from_custom_order(order)
    if task:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Індивідуальне замовлення C#{order_id} додано у Google Tasks.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Відкрити Google Tasks", url=TASKS_HOME_URL)]]),
        )
    else:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Не вдалося додати індивідуальне замовлення у Google Tasks. Перевір підключення Google Tasks в адмінці/API логах.")


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return
    order_id = int(query.data.split("_")[-1])
    order = get_order(order_id)
    await delete_callback_message(query)
    changed = update_order_status(order_id, "Скасовано")
    if changed and order:
        await _notify_order_status(context, order, "Скасовано")
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(f"❌ Замовлення #{order_id} скасовано." if changed else "Замовлення не знайдено."),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ Видалити замовлення", callback_data=f"admin_delete_order_{order_id}")]]) if changed else None,
    )


async def cancel_custom_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return
    order_id = int(query.data.split("_")[-1])
    order = get_custom_order(order_id)
    await delete_callback_message(query)
    changed = update_custom_order_status(order_id, "Скасовано")
    if changed and order:
        await _notify_custom_order_status(context, order, "Скасовано")
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(f"❌ Індивідуальне замовлення C#{order_id} скасовано." if changed else "Замовлення не знайдено."),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ Видалити замовлення", callback_data=f"admin_delete_custom_order_{order_id}")]]) if changed else None,
    )


async def delete_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return
    order_id = int(query.data.split("_")[-1])
    await delete_callback_message(query)
    deleted = delete_cancelled_order(order_id)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(f"🗑️ Скасоване замовлення #{order_id} видалено." if deleted else "Видаляти можна тільки скасовані замовлення."),
    )


async def delete_custom_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return
    order_id = int(query.data.split("_")[-1])
    await delete_callback_message(query)
    deleted = delete_cancelled_custom_order(order_id)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(f"🗑️ Скасоване індивідуальне замовлення C#{order_id} видалено." if deleted else "Видаляти можна тільки скасовані замовлення."),
    )
