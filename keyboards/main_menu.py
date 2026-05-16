from telegram import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import is_admin, WEBAPP_URL
from locales import tr


def _webapp_row():
    if not WEBAPP_URL:
        return None
    return [KeyboardButton("🛍 Mini App", web_app=WebAppInfo(url=WEBAPP_URL))]


def get_main_menu(user_id: int | None = None):
    if user_id is None:
        keyboard = [
            ["🍰 Каталог", "🛒 Кошик"],
            ["📦 Мої замовлення", "💬 Відгуки"],
            ["🎂 Індивідуальне замовлення", "❤️ Обране"],
            ["❓ FAQ", "📍 Контакти"],
            ["🌐 Мова / Язык / Język / Language"],
        ]

        webapp = _webapp_row()
        if webapp:
            keyboard.insert(0, webapp)

        return ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

    keyboard = [
        [tr(user_id, "menu_catalog"), tr(user_id, "menu_cart")],
        [tr(user_id, "menu_orders"), tr(user_id, "menu_reviews")],
        [tr(user_id, "menu_custom"), tr(user_id, "menu_favorites")],
        [tr(user_id, "menu_faq"), tr(user_id, "menu_contacts")],
        [tr(user_id, "menu_language")],
    ]

    webapp = _webapp_row()
    if webapp:
        keyboard.insert(0, webapp)

    if is_admin(user_id):
        keyboard.insert(0, ["📋 Активні замовлення", "🎟 Промокоди"])
        keyboard.insert(1, ["➕ Додати продукт", "🗑 Видалити продукт"])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


main_menu = get_main_menu()
