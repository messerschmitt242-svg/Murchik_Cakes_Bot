from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from locales import tr

PICKUP_READY_STATUS = "Готове до видачі"

PICKUP_SCHEME_PATH = Path(__file__).resolve().parent.parent / "assets" / "pickup_scheme.png"


def pickup_button(callback_data: str = "pickup_info", user_id: int | None = None):
    text = tr(user_id, "pickup_button") if user_id is not None else "📍 Як отримати замовлення"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=callback_data)]
    ])


async def send_pickup_info_to_chat(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int | None = None):
    if user_id is None:
        user_id = chat_id

    details = tr(user_id, "pickup_details")

    if PICKUP_SCHEME_PATH.exists():
        with PICKUP_SCHEME_PATH.open("rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=details,
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=details,
        )


async def pickup_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await send_pickup_info_to_chat(
        context=context,
        chat_id=query.message.chat_id,
        user_id=query.from_user.id,
    )
