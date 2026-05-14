from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_IDS, is_admin
from database.reviews_db import add_review_db, get_reviews_db

REVIEW_TEXT = 700
REVIEW_RATING = 701


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
        [
            InlineKeyboardButton("❌ Скасувати", callback_data="review_cancel")
        ]
    ])


async def review_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💬 Напишіть ваш відгук про замовлення або нашу кондитерську:"
    )
    return REVIEW_TEXT


async def review_get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 3:
        await update.message.reply_text("Відгук занадто короткий. Напишіть трохи детальніше:")
        return REVIEW_TEXT

    context.user_data["review_text"] = text

    await update.message.reply_text(
        "Оцініть нас від 1 до 5:",
        reply_markup=_rating_keyboard(),
    )

    return REVIEW_RATING


async def review_choose_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    rating = int(query.data.split("_")[-1])
    text = context.user_data.get("review_text", "")
    user = query.from_user
    name = user.full_name or user.username or "Клієнт"

    review_id = add_review_db(
        user_id=user.id,
        name=name,
        text=text,
        rating=rating,
    )

    context.user_data.pop("review_text", None)

    await query.message.reply_text(
        f"Дякуємо за відгук ❤️\nВаша оцінка: {rating}/5"
    )

    admin_text = f"""
Новий відгук #{review_id} 💬

Клієнт: {name}
Оцінка: {rating}/5

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

    reviews = get_reviews_db()

    if not reviews:
        await update.message.reply_text("Відгуків поки немає.")
        return

    text = "💬 Останні відгуки:\n\n"

    for r in reviews:
        text += f"""
#{r['id']} — {r['rating']}/5
{r['name']}
{r['text']}
------------------
"""

    await update.message.reply_text(text)
