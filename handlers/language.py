
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from database.user_settings_db import set_user_language
from locales import tr
from keyboards.main_menu import get_main_menu

async def language_menu(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_id=update.effective_user.id
    keyboard=InlineKeyboardMarkup([
        [InlineKeyboardButton("Українська",callback_data="lang_ua")],
        [InlineKeyboardButton("Русский",callback_data="lang_ru")],
        [InlineKeyboardButton("Polska",callback_data="lang_pl")],
        [InlineKeyboardButton("English",callback_data="lang_en")],
    ])
    await update.message.reply_text(
        tr(user_id,"choose_lang"),
        reply_markup=keyboard
    )

async def set_language(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query=update.callback_query
    await query.answer()
    lang=query.data.split("_")[1]
    set_user_language(query.from_user.id,lang)

    await query.message.reply_text(
        tr(query.from_user.id,"lang_changed"),
        reply_markup=get_main_menu(query.from_user.id)
    )
