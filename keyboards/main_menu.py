from telegram import ReplyKeyboardMarkup

from config import is_admin


def get_main_menu(user_id: int | None = None):
    rows = [
        ["🍰 Каталог", "🛒 Кошик"],
        ["❤️ Обране", "💬 Відгуки"],
        ["🎂 Індивідуальне замовлення"],
        ["📦 Мої замовлення"],
        ["❓ FAQ", "📍 Контакти"],
        ["🏠 Повернутися до головного меню"],
    ]

    if user_id is not None and is_admin(user_id):
        rows.insert(3, ["📋 Активні замовлення", "🎟 Промокоди"])
        rows.insert(4, ["➕ Додати продукт", "🗑 Видалити продукт"])

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
    )


main_menu = get_main_menu()
