from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from types import SimpleNamespace

from config import is_admin, WEBAPP_URL
from handlers.admin_orders import active_orders, list_orders
from handlers.maintenance import clear_test_data
from handlers.product_translations import regenerate_translations
from handlers.reviews import show_reviews_admin
from services.google_tasks import google_connect_url, google_tasks_status


def admin_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("📋 Активні замовлення", callback_data="admin_panel_active_orders")],
        [InlineKeyboardButton("📦 Усі замовлення", callback_data="admin_panel_all_orders")],
        [InlineKeyboardButton("➕ Додати продукт", callback_data="admin_panel_add_product")],
        [InlineKeyboardButton("🖼 Оновити фото продукту", callback_data="admin_panel_update_photos")],
        [InlineKeyboardButton("🗑 Видалити продукт", callback_data="admin_panel_delete_product")],
        [InlineKeyboardButton("🎟 Промокоди", callback_data="admin_panel_promos")],
        [InlineKeyboardButton("💬 Відгуки", callback_data="admin_panel_reviews")],
        [InlineKeyboardButton("🌐 Оновити переклади", callback_data="admin_panel_regen_translations")],
        [InlineKeyboardButton("🧹 Очистити тестові дані", callback_data="admin_panel_clear_test_data")],
    ]
    connect_url = google_connect_url()
    if connect_url:
        rows.append([InlineKeyboardButton("✅ Підключити Google Tasks", url=connect_url)])
    else:
        rows.append([InlineKeyboardButton("✅ Google Tasks: налаштувати", callback_data="admin_panel_google_tasks_status")])
    return InlineKeyboardMarkup(rows)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("🛠 Адмін-панель:", reply_markup=admin_keyboard())


async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    action = query.data.replace("admin_panel_", "", 1)

    fake_update = SimpleNamespace(
        effective_user=query.from_user,
        effective_chat=query.message.chat,
        message=query.message,
    )

    if action == "add_product":
        from handlers.add_product import add_product_start
        return await add_product_start(fake_update, context)
    if action == "update_photos":
        from handlers.update_photos import update_photos_start
        return await update_photos_start(fake_update, context)


    if action == "active_orders":
        await active_orders(fake_update, context)
    elif action == "all_orders":
        await list_orders(fake_update, context)
    elif action == "delete_product":
        from handlers.delete_product import delete_product
        await delete_product(fake_update, context)
    elif action == "promos":
        from handlers.promo import promo_menu
        await promo_menu(fake_update, context)
    elif action == "reviews":
        await show_reviews_admin(fake_update, context)
    elif action == "regen_translations":
        await regenerate_translations(fake_update, context)
    elif action == "clear_test_data":
        await clear_test_data(fake_update, context)
    elif action == "google_tasks_status":
        status = google_tasks_status()
        connect_url = status.get("connect_url") or ""
        text = (
            "✅ Google Tasks\n\n"
            f"Client ID/Secret: {'✅' if status.get('client_configured') else '❌'}\n"
            f"Підключено: {'✅' if status.get('connected') or status.get('env_refresh_token') else '❌'}\n"
            f"Акаунт: {status.get('account_email') or '—'}\n\n"
            "Щоб підключити без PowerShell, додай GOOGLE_CLIENT_ID і GOOGLE_CLIENT_SECRET в API-сервіс Railway, "
            "а потім відкрий посилання підключення."
        )
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Підключити Google Tasks", url=connect_url)]]) if connect_url else None
        await query.message.reply_text(text, reply_markup=markup)
