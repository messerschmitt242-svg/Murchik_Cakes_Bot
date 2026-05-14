from telegram import ReplyKeyboardMarkup

from config import ADMIN_ID


def get_main_menu(user_id: int | None = None):
    rows = [
        ["🍰 Каталог", "🛒 Кошик"],
        ["📦 Мої замовлення"],
        ["❓ FAQ", "📍 Контакти"],
    ]

    # Адмінське меню бачить тільки власник бота
    if ADMIN_ID and user_id == ADMIN_ID:
        rows.insert(2, ["📋 Активні замовлення", "🎟 Промокоди"])
        rows.insert(3, ["➕ Додати продукт", "🗑 Видалити продукт"])

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
    )


main_menu = get_main_menu()
