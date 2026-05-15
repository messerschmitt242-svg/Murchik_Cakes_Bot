from telegram import Update
from telegram.ext import ContextTypes

from keyboards.main_menu import get_main_menu


HOME_BUTTON_TEXT = "🏠 Повернутися до головного меню"


async def go_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Best-effort chat cleanup and return to main menu.

    Telegram Bot API does not guarantee that a bot can delete absolutely every
    message in a private chat. This function tries to delete the last messages
    and then sends a fresh main menu.
    """

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Clear active temporary flows.
    context.user_data.clear()

    current_message_id = update.effective_message.message_id

    # Best-effort cleanup of recent chat messages.
    for message_id in range(current_message_id, max(0, current_message_id - 15), -1):
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
        except Exception:
            pass

    await context.bot.send_message(
        chat_id=chat_id,
        text="Головне меню 🍰",
        reply_markup=get_main_menu(user_id),
    )


async def go_home_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    chat_id = query.message.chat_id

    context.user_data.clear()

    current_message_id = query.message.message_id

    for message_id in range(current_message_id, max(0, current_message_id - 15), -1):
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
        except Exception:
            pass

    await context.bot.send_message(
        chat_id=chat_id,
        text="Головне меню 🍰",
        reply_markup=get_main_menu(user_id),
    )
