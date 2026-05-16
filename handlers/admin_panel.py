from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from types import SimpleNamespace

from config import is_admin
from handlers.admin_orders import active_orders, list_orders
from handlers.maintenance import clear_test_data
from handlers.product_translations import regenerate_translations
from handlers.reviews import show_reviews_admin


def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Активні замовлення", callback_data="admin_panel_active_orders")],
        [InlineKeyboardButton("📦 Усі замовлення", callback_data="admin_panel_all_orders")],
        [InlineKeyboardButton("➕ Додати продукт", callback_data="admin_panel_add_product")],
        [InlineKeyboardButton("🖼 Оновити фото продукту", callback_data="admin_panel_update_photos")],
        [InlineKeyboardButton("🗑 Видалити продукт", callback_data="admin_panel_delete_product")],
        [InlineKeyboardButton("🎟 Промокоди", callback_data="admin_panel_promos")],
        [InlineKeyboardButton("💬 Відгуки", callback_data="admin_panel_reviews")],
        [InlineKeyboardButton("🌐 Оновити переклади", callback_data="admin_panel_regen_translations")],
        [InlineKeyboardButton("🧹 Очистити тестові дані", callback_data="admin_panel_clear_test_data")],
    ])


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
