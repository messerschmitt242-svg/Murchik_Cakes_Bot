from telegram import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import is_admin, WEBAPP_URL


ADMIN_MAIN_MENU = [
    ["📋 Активні замовлення", "📦 Усі замовлення"],
    ["➕ Додати продукт", "🗑 Видалити продукт"],
    ["🖼 Оновити фото продукту", "🎟 Промокоди"],
    ["💬 Відгуки", "🌐 Оновити переклади"],
    ["🧹 Очистити тестові дані"],
]


def _webapp_row():
    if not WEBAPP_URL:
        return [KeyboardButton("🛍 Mini App")]
    return [KeyboardButton("🛍 Mini App", web_app=WebAppInfo(url=WEBAPP_URL))]


def get_main_menu(user_id: int | None = None):
    # Для адміністратора головне меню тепер одразу є адмін-меню.
    # Кнопку "Адмін-панель" прибрано, усі функції винесені на ReplyKeyboard.
    if user_id is not None and is_admin(user_id):
        keyboard = ADMIN_MAIN_MENU
    else:
        # Для клієнтів залишаємо тільки Mini App, щоб вони користувалися застосунком.
        keyboard = [_webapp_row()]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )


main_menu = get_main_menu()
