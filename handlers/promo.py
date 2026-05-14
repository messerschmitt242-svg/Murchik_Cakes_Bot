from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import is_admin
from database.promo_db import create_promo, get_all_promos
from handlers.cleanup import delete_callback_message

PROMO_CODE_INPUT = 300
PROMO_DISCOUNT_SELECT = 301


def _start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎟 Сгенерувати промокод", callback_data="promo_create")]
    ])


def _discount_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("-20%", callback_data="promo_discount_20")],
        [InlineKeyboardButton("-10%", callback_data="promo_discount_10")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="promo_cancel")],
    ])


async def promo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    await update.message.reply_text(
        "Панель промокодів:",
        reply_markup=_start_keyboard(),
    )


async def promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return ConversationHandler.END

    chat_id = query.message.chat_id
    await delete_callback_message(query)

    await context.bot.send_message(
        chat_id=chat_id,
        text="Введіть код промокоду. Наприклад: MURCHIK20 або TORT10"
    )
    return PROMO_CODE_INPUT


async def promo_get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()

    if len(code) < 3:
        await update.message.reply_text("Код занадто короткий. Введіть інший код:")
        return PROMO_CODE_INPUT

    context.user_data["new_promo_code"] = code

    await update.message.reply_text(
        f"Промокод: {code}\nОберіть розмір знижки:",
        reply_markup=_discount_keyboard(),
    )
    return PROMO_DISCOUNT_SELECT


async def promo_choose_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return ConversationHandler.END

    chat_id = query.message.chat_id
    await delete_callback_message(query)

    discount = int(query.data.split("_")[-1])
    code = context.user_data.get("new_promo_code")

    if not code:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Помилка: код не знайдено. Почніть знову через кнопку Промокоди"
        )
        return ConversationHandler.END

    create_promo(code, discount)
    context.user_data.pop("new_promo_code", None)

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Промокод створено:\n{code} — -{discount}%"
    )
    return ConversationHandler.END


async def promo_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        await delete_callback_message(query)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Створення промокоду скасовано."
        )
    elif update.message:
        await update.message.reply_text("Створення промокоду скасовано.")

    context.user_data.pop("new_promo_code", None)
    return ConversationHandler.END


async def promo_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    promos = get_all_promos()
    if not promos:
        await update.message.reply_text("Промокодів поки немає.")
        return

    text = "🎟 Промокоди:\n\n"
    for promo in promos:
        status = "активний" if promo["is_active"] else "вимкнений"
        text += f"• {promo['code']} — -{promo['discount_percent']}% — {status}\n"

    await update.message.reply_text(text)
