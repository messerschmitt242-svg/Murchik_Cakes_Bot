from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_IDS, ADMIN_CHAT_IDS, ADMIN_USERNAME
from locales import tr


def admin_contact_keyboard(user_id: int | None = None):
    if not ADMIN_USERNAME:
        return None
    text = tr(user_id, "write_admin") if user_id is not None else "✍️ Написати адміністратору"
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, url=f"https://t.me/{ADMIN_USERNAME}")]])


def _admin_targets() -> list[int]:
    seen = set()
    result = []
    for chat_id in [*ADMIN_IDS, *ADMIN_CHAT_IDS]:
        if chat_id not in seen:
            seen.add(chat_id)
            result.append(chat_id)
    return result


async def notify_admins_text(context, text: str, reply_markup=None) -> int:
    success_count = 0
    for admin_id in _admin_targets():
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=text,
                reply_markup=reply_markup,
            )
            success_count += 1
        except Exception as e:
            print(f"ADMIN NOTIFY ERROR {admin_id}: {e}")
    return success_count


async def notify_admins_photo(context, photo: str, caption: str, reply_markup=None) -> int:
    success_count = 0
    for admin_id in _admin_targets():
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup,
            )
            success_count += 1
        except Exception as e:
            print(f"ADMIN PHOTO NOTIFY ERROR {admin_id}: {e}")
    return success_count
