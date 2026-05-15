from telegram import ReplyKeyboardMarkup
from config import is_admin
from locales import tr


def get_main_menu(user_id: int | None = None):
    if user_id is None:
        # Backward compatibility for old handlers that still import main_menu.
        # Default language: Ukrainian.
        keyboard = [
            ["🍰 Каталог", "🛒 Кошик"],
            ["📦 Мої замовлення", "💬 Відгуки"],
            ["🎂 Індивідуальне замовлення", "❤️ Обране"],
            ["❓ FAQ", "📍 Контакти"],
            ["🌐 Мова"],
        ]

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

    if is_admin(user_id):
        keyboard.insert(0, ["📋 Активні замовлення", "🎟 Промокоди"])
        keyboard.insert(1, ["➕ Додати продукт", "🗑 Видалити продукт"])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# Compatibility with old imports:
# from keyboards.main_menu import main_menu
main_menu = get_main_menu()
