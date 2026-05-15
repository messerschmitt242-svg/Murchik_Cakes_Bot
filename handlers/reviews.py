import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_IDS, is_admin
from database.orders_db import get_user_orders
from handlers.home import HOME_BUTTON_TEXT
from locales import tr
from database.reviews_db import (
    add_review_db,
    get_reviews_db,
    get_bakery_reviews_db,
    get_product_reviews_db,
    format_reviews,
    delete_review_db,
)

REVIEW_MENU = 700
REVIEW_TYPE = 701
REVIEW_PRODUCT = 702
REVIEW_TEXT = 703
REVIEW_RATING = 704


def _reviews_main_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(user_id, "view_reviews"), callback_data="reviews_view")],
        [InlineKeyboardButton(tr(user_id, "leave_review"), callback_data="reviews_leave")],
        [InlineKeyboardButton(tr(user_id, "home_button"), callback_data="home_inline")],
    ])


def _review_type_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(user_id, "review_bakery"), callback_data="review_type_bakery")],
        [InlineKeyboardButton(tr(user_id, "review_product"), callback_data="review_type_product")],
        [InlineKeyboardButton(tr(user_id, "cancel"), callback_data="review_cancel")],
        [InlineKeyboardButton(tr(user_id, "home_button"), callback_data="home_inline")],
    ])


def _rating_keyboard(user_id: int):
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
        [InlineKeyboardButton(tr(user_id, "cancel"), callback_data="review_cancel")],
        [InlineKeyboardButton(tr(user_id, "home_button"), callback_data="home_inline")],
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


def _last_order_products_keyboard(products, user_id: int):
    keyboard = []

    for item in products:
        keyboard.append([
            InlineKeyboardButton(
                item["name"],
                callback_data=f"review_product_{item['product_id']}",
            )
        ])

    keyboard.append([InlineKeyboardButton(tr(user_id, "cancel"), callback_data="review_cancel")])
    keyboard.append([InlineKeyboardButton(tr(user_id, "home_button"), callback_data="home_inline")])

    return InlineKeyboardMarkup(keyboard)


async def review_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        tr(update.effective_user.id, "reviews_title"),
        reply_markup=_reviews_main_keyboard(update.effective_user.id),
    )
    return REVIEW_MENU


async def reviews_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    reviews = get_reviews_db(limit=5)

    await query.message.reply_text(
        tr(query.from_user.id, "top_reviews") + format_reviews(reviews)
    )

    return ConversationHandler.END


async def reviews_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        tr(query.from_user.id, "review_question"),
        reply_markup=_review_type_keyboard(query.from_user.id),
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
        tr(query.from_user.id, "review_write_bakery")
    )

    return REVIEW_TEXT


async def review_type_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    products = _last_order_products(query.from_user.id)

    if not products:
        await query.message.reply_text(
            tr(query.from_user.id, "review_no_orders")
        )
        return ConversationHandler.END

    await query.message.reply_text(
        tr(query.from_user.id, "review_choose_last_product"),
        reply_markup=_last_order_products_keyboard(products, query.from_user.id),
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
        tr(query.from_user.id, "review_write_product").format(name=product["name"])
    )

    return REVIEW_TEXT


async def review_get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 3:
        await update.message.reply_text(tr(update.effective_user.id, "review_too_short"))
        return REVIEW_TEXT

    context.user_data["review_text"] = text

    await update.message.reply_text(
        "Оцініть від 1 до 5:",
        reply_markup=_rating_keyboard(update.effective_user.id),
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
        tr(query.from_user.id, "review_thanks").format(rating=rating)
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
        await query.message.reply_text(tr(query.from_user.id, "review_cancelled"))
    elif update.message:
        await update.message.reply_text(tr(update.effective_user.id, "review_cancelled"))

    return ConversationHandler.END


def _admin_reviews_keyboard(rows):
    keyboard = []
    for r in rows:
        keyboard.append([
            InlineKeyboardButton(
                f"🗑 Видалити відгук #{r['id']}",
                callback_data=f"delete_review_{r['id']}"
            )
        ])
    return InlineKeyboardMarkup(keyboard)


async def show_reviews_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    reviews = get_reviews_db(limit=10)

    await update.message.reply_text(
        "💬 Останні відгуки:\n\n" + format_reviews(reviews),
        reply_markup=_admin_reviews_keyboard(reviews) if reviews else None,
    )


async def show_product_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[-1])
    reviews = get_product_reviews_db(product_id, limit=5)

    await query.message.reply_text(
        tr(query.from_user.id, "product_reviews_title") + format_reviews(reviews)
    )


async def show_bakery_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    reviews = get_bakery_reviews_db(limit=5)

    await query.message.reply_text(
        tr(query.from_user.id, "bakery_reviews_title") + format_reviews(reviews)
    )


async def delete_review_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.message.reply_text("Недоступно.")
        return

    review_id = int(query.data.split("_")[-1])
    deleted = delete_review_db(review_id)

    if deleted:
        await query.message.reply_text(f"✅ Відгук #{review_id} видалено.")
    else:
        await query.message.reply_text(f"❌ Відгук #{review_id} не знайдено.")
