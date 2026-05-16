from telegram import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import is_admin, WEBAPP_URL


def _webapp_row():
    if not WEBAPP_URL:
        return [KeyboardButton("🛍 Mini App")]
    return [KeyboardButton("🛍 Mini App", web_app=WebAppInfo(url=WEBAPP_URL))]


def get_main_menu(user_id: int | None = None):
    """Main reply keyboard.

    Admins should see only the entry point to the admin panel.
    User ordering is handled through the Telegram Mini App menu button / channel link,
    so extra reply buttons are intentionally hidden from the main chat menu.
    """
    if user_id is not None and is_admin(user_id):
        keyboard = [["🛠 Адмін-панель"]]
    else:
        keyboard = [_webapp_row()]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )


main_menu = get_main_menu()
