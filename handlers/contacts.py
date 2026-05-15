from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from locales import tr


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                tr(user_id, "route_button"),
                url="https://maps.app.goo.gl/7YLX42TMak4FdaXm9"
            )
        ]
    ])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=tr(user_id, "contacts_text"),
        reply_markup=keyboard
    )
