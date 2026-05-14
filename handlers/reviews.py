import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_IDS, is_admin
from database.orders_db import get_user_orders
from database.reviews_db import (
    add_review_db,
    get_reviews_db,
    get_bakery_reviews_db,
    get_product_reviews_db,
    format_reviews,
)

REVIEW_MENU = 700
REVIEW_TYPE = 701
REVIEW_PRODUCT = 702
REVIEW_TEXT = 703
REVIEW_RATING = 704


def _reviews_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👀 Подивитися відгуки", callback_data="reviews_view")],
        [InlineKeyboardButton("✍️ Залишити відгук", callback_data="reviews_leave")],
    ])


def _review_type_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Про кондитерську", callback_data="review_type_bakery")],
        [InlineKeyboardButton("🍰 Про конкретний десерт", callback_data="review_type_product")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="review_cancel")],
    ])


def _rating_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⭐ 5", callback_data="review_rating_5"),
            InlineKeyboardButton("⭐ 4", callback_data="review_rating_4"),
            InlineKeyboardButton("⭐ 3", callback_data="review_rating_3"),
        ],
        [
            InlineKeyboardButton("⭐ 2", callback_data="review_rating_2"),
            InlineKeyboardButton("⭐ 1", callback_data="review_rating_1"),
        ],
        [InlineKeyboardButton("❌ Скасувати", callback_data="review_cancel")],
    ])


def _last_order_products(user_id: int):
    orders = get_user_orders(user_id)

    if not orders:
        return []

    last_order = orders[0]

    try:
        items = json.loads(last_order["items"] or "[]")
    except Exception:
        return []

    products = []
    seen = set()

    for item in items:
        product_id = item.get("product_id")
        name = item.get("name", "Товар")

        if not product_id or product_id in seen:
            continue

        seen.add(product_id)
        products.append({
            "product_id": int(product_id),
            "name": name,
        })

    return products


def _last_order_products_keyboard(products):
    keyboard = []

    for item in products:
        keyboard.append([
            InlineKeyboardButton(
                item["name"],
                callback_data=f"review_product_{item['product_id']}",
            )
        ])

    keyboard.append([InlineKeyboardButton("❌ Скасувати", callback_data="review_cancel")])

    return InlineKeyboardMarkup(keyboard)


async def review_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💬 Відгуки",
        reply_markup=_reviews_main_keyboard(),
    )
    return REVIEW_MENU


async def reviews_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    reviews = get_reviews_db(limit=5)

    await query.message.reply_text(
        "⭐ Топ-5 відгуків:\n\n" + format_reviews(reviews)
    )

    return ConversationHandler.END


async def reviews_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "Про що хочете залишити відгук?",
        reply_markup=_review_type_keyboard(),
    )

    return REVIEW_TYPE


async def review_type_bakery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["review_context"] = {
        "review_type": "bakery",
        "product_id": None,
        "product_name": "",
    }

    await query.message.reply_text(
        "Напишіть ваш відгук про кондитерську:"
    )

    return REVIEW_TEXT


async def review_type_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    products = _last_order_products(query.from_user.id)

    if not products:
        await query.message.reply_text(
            "У вас поки немає завершених або створених замовлень, з яких можна вибрати десерт для відгуку."
        )
        return ConversationHandler.END

    await query.message.reply_text(
        "Оберіть десерт з вашого останнього замовлення:",
        reply_markup=_last_order_products_keyboard(products),
    )

    return REVIEW_PRODUCT


async def review_choose_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[-1])
    products = _last_order_products(query.from_user.id)
    product = next((p for p in products if p["product_id"] == product_id), None)

    if not product:
        await query.message.reply_text("Не вдалося знайти цей продукт у вашому останньому замовленні.")
        return ConversationHandler.END

    context.user_data["review_context"] = {
        "review_type": "product",
        "product_id": product_id,
        "product_name": product["name"],
    }

    await query.message.reply_text(
        f"Напишіть відгук про «{product['name']}»:"
    )

    return REVIEW_TEXT


async def review_get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 3:
        await update.message.reply_text("Відгук занадто короткий. Напишіть трохи детальніше:")
        return REVIEW_TEXT

    context.user_data["review_text"] = text

    await update.message.reply_text(
        "Оцініть від 1 до 5:",
        reply_markup=_rating_keyboard(),
    )

    return REVIEW_RATING


async def review_choose_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    rating = int(query.data.split("_")[-1])
    text = context.user_data.get("review_text", "")
    review_context = context.user_data.get("review_context", {"review_type": "bakery"})

    user = query.from_user
    name = user.full_name or user.username or "Клієнт"

    review_id = add_review_db(
        user_id=user.id,
        name=name,
        text=text,
        rating=rating,
        review_type=review_context.get("review_type", "bakery"),
        product_id=review_context.get("product_id"),
        product_name=review_context.get("product_name", ""),
    )

    context.user_data.pop("review_text", None)
    context.user_data.pop("review_context", None)

    await query.message.reply_text(
        f"Дякуємо за відгук ❤️\nВаша оцінка: {rating}/5"
    )

    product_line = ""
    if review_context.get("review_type") == "product":
        product_line = f"\nТовар: {review_context.get('product_name')}"

    admin_text = f"""
Новий відгук #{review_id} 💬

Клієнт: {name}
Оцінка: {rating}/5{product_line}

{text}
"""

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin_id,
            text=admin_text,
        )

    return ConversationHandler.END


async def review_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("review_text", None)
    context.user_data.pop("review_context", None)

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text("Відгук скасовано.")
    elif update.message:
        await update.message.reply_text("Відгук скасовано.")

    return ConversationHandler.END


async def show_reviews_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    reviews = get_reviews_db(limit=10)

    await update.message.reply_text(
        "💬 Останні відгуки:\n\n" + format_reviews(reviews)
    )


async def show_product_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[-1])
    reviews = get_product_reviews_db(product_id, limit=5)

    await query.message.reply_text(
        "💬 Відгуки про продукт:\n\n" + format_reviews(reviews)
    )


async def show_bakery_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    reviews = get_bakery_reviews_db(limit=5)

    await query.message.reply_text(
        "💬 Відгуки про кондитерську:\n\n" + format_reviews(reviews)
    )
