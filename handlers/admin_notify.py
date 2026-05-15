from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import ADMIN_IDS, ADMIN_USERNAME
from locales import tr


def admin_contact_keyboard(user_id: int | None = None):
    if not ADMIN_USERNAME:
        return None

    text = tr(user_id, "write_admin") if user_id is not None else "💬 Написати адміністратору"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text,
                url=f"https://t.me/{ADMIN_USERNAME}"
            )
        ]
    ])


async def notify_admins_text(context, text: str) -> int:
    success_count = 0

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=text,
            )
            success_count += 1
        except Exception as e:
            print(f"ADMIN NOTIFY ERROR {admin_id}: {e}")

    return success_count


async def notify_admins_photo(context, photo: str, caption: str) -> int:
    success_count = 0

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo,
                caption=caption,
            )
            success_count += 1
        except Exception as e:
            print(f"ADMIN PHOTO NOTIFY ERROR {admin_id}: {e}")

    return success_count
