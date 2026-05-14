from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

from database.products_db import get_all_products, get_product, get_categories
from handlers.cleanup import delete_callback_message


def _category_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎂 Торти", callback_data="catalog_category_Торти")],
        [InlineKeyboardButton("🧁 Тістечка", callback_data="catalog_category_Тістечка")],
    ])


def _products_keyboard(products):
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(product["name"], callback_data=f"catalog_product_{product['id']}")
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ До категорій", callback_data="catalog_back")
    ])

    return InlineKeyboardMarkup(keyboard)


async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Оберіть категорію каталогу 🍰",
        reply_markup=_category_keyboard(),
    )


async def catalog_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await delete_callback_message(query)

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Оберіть категорію каталогу 🍰",
        reply_markup=_category_keyboard(),
    )


async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("catalog_category_", "", 1)

    await delete_callback_message(query)

    if category not in get_categories():
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Категорію не знайдено.",
            reply_markup=_category_keyboard(),
        )
        return

    products = get_all_products(category=category)

    if not products:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"У категорії «{category}» поки немає товарів 🍰",
            reply_markup=_category_keyboard(),
        )
        return

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"{category}:\nОберіть товар:",
        reply_markup=_products_keyboard(products),
    )


async def show_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[-1])
    product = get_product(product_id)

    await delete_callback_message(query)

    if not product:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Товар не знайдено ❌",
        )
        return

    caption = f"""
🍰 {product['name']}

💰 {product['price']:.2f} zł

📝 {product['description']}
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton("❤️ Додати в обране", callback_data=f"favorite_{product_id}")],
        [InlineKeyboardButton("⬅️ Назад до категорії", callback_data=f"catalog_category_{product['category']}")],
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
            text="Додати цей товар у кошик?",
            reply_markup=keyboard,
        )
        return

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=caption,
        reply_markup=keyboard,
    )
