from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import is_admin
from database.promo_db import create_promo, get_all_promos
from database.products_db import get_all_products, get_product
from handlers.cleanup import delete_callback_message

PROMO_CODE_INPUT = 300
PROMO_DISCOUNT_SELECT = 301
PROMO_SCOPE_SELECT = 302
PROMO_PRODUCT_SELECT = 303


def _start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Сгенерувати промокод", callback_data="promo_create")],
    ])


def _discount_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("-20%", callback_data="promo_discount_20")],
        [InlineKeyboardButton("-10%", callback_data="promo_discount_10")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="promo_cancel")],
    ])


def _scope_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 На всю корзину", callback_data="promo_scope_cart")],
        [InlineKeyboardButton("🍰 На конкретний товар", callback_data="promo_scope_product")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="promo_cancel")],
    ])


def _products_keyboard():
    keyboard = []
    for product in get_all_products():
        keyboard.append([
            InlineKeyboardButton(
                f"#{product['id']} — {product['name']}",
                callback_data=f"promo_product_{product['id']}",
            )
        ])
    keyboard.append([InlineKeyboardButton("❌ Скасувати", callback_data="promo_cancel")])
    return InlineKeyboardMarkup(keyboard)


async def promo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("Панель промокодів:", reply_markup=_start_keyboard())


async def promo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return ConversationHandler.END
    chat_id = query.message.chat_id
    await delete_callback_message(query)
    await context.bot.send_message(chat_id=chat_id, text="Введіть код промокоду.\nНаприклад: MURCHIK20 або TORT10")
    return PROMO_CODE_INPUT


async def promo_get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    if len(code) < 3:
        await update.message.reply_text("Код занадто короткий.\nВведіть інший код:")
        return PROMO_CODE_INPUT
    context.user_data["new_promo_code"] = code
    await update.message.reply_text(f"Промокод: {code}\nОберіть розмір знижки:", reply_markup=_discount_keyboard())
    return PROMO_DISCOUNT_SELECT


async def promo_choose_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return ConversationHandler.END
    discount = int(query.data.split("_")[-1])
    context.user_data["new_promo_discount"] = discount
    chat_id = query.message.chat_id
    await delete_callback_message(query)
    await context.bot.send_message(chat_id=chat_id, text="Куди застосовується промокод?", reply_markup=_scope_keyboard())
    return PROMO_SCOPE_SELECT


async def promo_choose_scope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return ConversationHandler.END
    chat_id = query.message.chat_id
    await delete_callback_message(query)

    if query.data == "promo_scope_cart":
        code = context.user_data.get("new_promo_code")
        discount = context.user_data.get("new_promo_discount")
        if not code or not discount:
            await context.bot.send_message(chat_id=chat_id, text="Помилка: дані промокоду не знайдено. Почніть знову.")
            return ConversationHandler.END
        create_promo(code, int(discount), product_id=None)
        context.user_data.pop("new_promo_code", None)
        context.user_data.pop("new_promo_discount", None)
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Промокод створено:\n{code} — -{discount}% — на всю корзину")
        return ConversationHandler.END

    products = get_all_products()
    if not products:
        await context.bot.send_message(chat_id=chat_id, text="Немає товарів для прив'язки промокоду.")
        return ConversationHandler.END
    await context.bot.send_message(chat_id=chat_id, text="Оберіть товар для промокоду:", reply_markup=_products_keyboard())
    return PROMO_PRODUCT_SELECT


async def promo_choose_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return ConversationHandler.END
    chat_id = query.message.chat_id
    await delete_callback_message(query)

    product_id = int(query.data.split("_")[-1])
    product = get_product(product_id)
    code = context.user_data.get("new_promo_code")
    discount = context.user_data.get("new_promo_discount")
    if not code or not discount or not product:
        await context.bot.send_message(chat_id=chat_id, text="Помилка: промокод або товар не знайдено. Почніть знову.")
        return ConversationHandler.END

    create_promo(code, int(discount), product_id=product_id)
    context.user_data.pop("new_promo_code", None)
    context.user_data.pop("new_promo_discount", None)
    await context.bot.send_message(chat_id=chat_id, text=f"✅ Промокод створено:\n{code} — -{discount}% — товар: {product['name']}")
    return ConversationHandler.END


async def promo_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        await delete_callback_message(query)
        await context.bot.send_message(chat_id=chat_id, text="Створення промокоду скасовано.")
    elif update.message:
        await update.message.reply_text("Створення промокоду скасовано.")
    context.user_data.pop("new_promo_code", None)
    context.user_data.pop("new_promo_discount", None)
    return ConversationHandler.END


async def promo_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    promos = get_all_promos()
    if not promos:
        await update.message.reply_text("Промокодів поки немає.")
        return
    text = "🎁 Промокоди:\n\n"
    for promo in promos:
        status = "активний" if promo["is_active"] else "вимкнений"
        scope = "вся корзина" if promo["product_id"] is None else f"товар: {promo['product_name'] or promo['product_id']}"
        text += f"• {promo['code']} — -{promo['discount_percent']}% — {scope} — {status}\n"
    await update.message.reply_text(text)
