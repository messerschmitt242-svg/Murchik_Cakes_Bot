from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, WebAppInfo
from config import is_admin, WEBAPP_URL


def _webapp_row():
    if not WEBAPP_URL:
        return [KeyboardButton("🛍 Mini App")]
    return [KeyboardButton("🛍 Mini App", web_app=WebAppInfo(url=WEBAPP_URL))]


def get_main_menu(user_id: int | None = None):
    """Main chat keyboard.

    Users work with the shop through the Telegram Mini App menu button,
    so the bot chat menu stays clean. Admins see only the Admin Panel entry.
    """

    if user_id is not None and is_admin(user_id):
        return ReplyKeyboardMarkup(
            [["🛠 Адмін-панель"]],
            resize_keyboard=True,
        )

    return ReplyKeyboardRemove()


main_menu = ReplyKeyboardRemove()
