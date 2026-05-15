from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

from database.products_db import get_all_products, get_product, get_categories
from database.reviews_db import get_product_rating_db
from database.favorites_db import is_favorite_db
from handlers.cleanup import delete_callback_message
from locales import tr
from utils_translation import translate_product_name, translate_description


def _category_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(user_id, "cat_cakes"), callback_data="catalog_category_Торти")],
        [InlineKeyboardButton(tr(user_id, "cat_pastries"), callback_data="catalog_category_Тістечка")],
        [InlineKeyboardButton(tr(user_id, "home_button"), callback_data="home_inline")],
    ])


def _products_keyboard(products, user_id: int):
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(translate_product_name(product["name"], user_id, product.get("translations")), callback_data=f"catalog_product_{product['id']}")
        ])

    keyboard.append([InlineKeyboardButton(tr(user_id, "back_categories"), callback_data="catalog_back")])
    keyboard.append([InlineKeyboardButton(tr(user_id, "home_button"), callback_data="home_inline")])
    return InlineKeyboardMarkup(keyboard)


async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        tr(user_id, "cat_choose"),
        reply_markup=_category_keyboard(user_id),
    )


async def catalog_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    await delete_callback_message(query)

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=tr(user_id, "cat_choose"),
        reply_markup=_category_keyboard(user_id),
    )


async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    category = query.data.replace("catalog_category_", "", 1)
    await delete_callback_message(query)

    if category not in get_categories():
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Категорію не знайдено.",
            reply_markup=_category_keyboard(user_id),
        )
        return

    products = get_all_products(category=category)

    if not products:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"У категорії «{category}» поки немає товарів 🍰",
            reply_markup=_category_keyboard(user_id),
        )
        return

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"{category}:\n{tr(user_id, 'choose_product')}",
        reply_markup=_products_keyboard(products, user_id),
    )


async def show_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    product_id = int(query.data.split("_")[-1])
    product = get_product(product_id)

    await delete_callback_message(query)

    if not product:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Товар не знайдено ❌",
        )
        return

    avg_rating, count_reviews = get_product_rating_db(product_id)

    if count_reviews:
        rating_line = tr(user_id, "rating_prefix") + f" {avg_rating:.1f}/5 ({count_reviews})"
    else:
        rating_line = tr(user_id, "rating_empty")

    translated_name = translate_product_name(product["name"], user_id, product.get("translations"))
    translated_description = translate_description(product["description"], user_id, product.get("translations"))

    caption = f"""
🍰 {translated_name}

💰 {product['price']:.2f} zł
{rating_line}

📝 {translated_description}
"""

    favorite_text = tr(user_id, "remove_favorite") if is_favorite_db(user_id, product_id) else tr(user_id, "add_favorite")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(user_id, "add_to_cart"), callback_data=f"add_{product_id}")],
        [InlineKeyboardButton(favorite_text, callback_data=f"favorite_{product_id}")],
        [InlineKeyboardButton(tr(user_id, "view_reviews"), callback_data=f"product_reviews_{product_id}")],
        [InlineKeyboardButton(tr(user_id, "back_categories"), callback_data=f"catalog_category_{product['category']}")],
        [InlineKeyboardButton(tr(user_id, "home_button"), callback_data="home_inline")],
    ])

    photos = product.get("photos", [])

    if len(photos) == 1:
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=photos[0],
            caption=caption,
            reply_markup=keyboard,
        )
        return

    if len(photos) > 1:
        media = []
        for index, photo_id in enumerate(photos[:10]):
            media.append(
                InputMediaPhoto(
                    media=photo_id,
                    caption=caption if index == 0 else None,
                )
            )

        await context.bot.send_media_group(
            chat_id=query.message.chat_id,
            media=media,
        )

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=tr(user_id, "add_product_question"),
            reply_markup=keyboard,
        )
        return

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=caption,
        reply_markup=keyboard,
    )
