from telegram import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import is_admin, WEBAPP_URL


def _webapp_row():
    if not WEBAPP_URL:
        return [KeyboardButton("🛍 Mini App")]
    return [KeyboardButton("🛍 Mini App", web_app=WebAppInfo(url=WEBAPP_URL))]


def get_main_menu(user_id: int | None = None):
    keyboard = [_webapp_row()]

    if user_id is not None and is_admin(user_id):
        keyboard.extend([
            ["🛠 Адмін-панель"],
            ["📋 Активні замовлення", "🎟 Промокоди"],
            ["➕ Додати продукт", "🖼 Оновити фото"],
            ["🗑 Видалити продукт"],
        ])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )


main_menu = get_main_menu()
