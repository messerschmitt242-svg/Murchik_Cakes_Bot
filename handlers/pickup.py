from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

PICKUP_READY_STATUS = "Готове до видачі"

PICKUP_DETAILS = """
📍 Подробиці на місці:

На брамі на клавіатурі натиснути 69,
потім кнопку з значком ключа,
потім код 6314.

Поверх 5, квартира 69.
""".strip()

PICKUP_SCHEME_PATH = Path(__file__).resolve().parent.parent / "assets" / "pickup_scheme.png"


def pickup_button(callback_data: str = "pickup_info"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📍 Як отримати замовлення", callback_data=callback_data)]
    ])


async def send_pickup_info_to_chat(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    if PICKUP_SCHEME_PATH.exists():
        with PICKUP_SCHEME_PATH.open("rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=PICKUP_DETAILS,
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=PICKUP_DETAILS,
        )


async def pickup_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await send_pickup_info_to_chat(
        context=context,
        chat_id=query.message.chat_id,
    )
