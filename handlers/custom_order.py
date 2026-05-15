from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from database.custom_orders_db import create_custom_order_db
from database.products_db import get_all_products, get_product, get_categories
from keyboards.main_menu import get_main_menu
from handlers.cleanup import delete_callback_message
from handlers.home import HOME_BUTTON_TEXT
from locales import tr
from handlers.admin_notify import notify_admins_text, notify_admins_photo, admin_contact_keyboard

CUSTOM_NAME = 800
CUSTOM_PHONE = 801
CUSTOM_CATEGORY = 802
CUSTOM_PRODUCT = 803
CUSTOM_DESCRIPTION = 804
CUSTOM_DATE = 805
CUSTOM_PHOTO = 806


def _category_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎂 Торти", callback_data="custom_category_Торти")],
        [InlineKeyboardButton("🧁 Тістечка", callback_data="custom_category_Тістечка")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="custom_cancel")],
        [InlineKeyboardButton(HOME_BUTTON_TEXT, callback_data="home_inline")],
    ])


def _products_keyboard(products):
    keyboard = []

    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                product["name"],
                callback_data=f"custom_product_{product['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton("⬅️ До категорій", callback_data="custom_back_categories")])
    keyboard.append([InlineKeyboardButton("❌ Скасувати", callback_data="custom_cancel")])
    keyboard.append([InlineKeyboardButton(HOME_BUTTON_TEXT, callback_data="home_inline")])

    return InlineKeyboardMarkup(keyboard)


def _skip_photo_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(user_id, "skip_photo"), callback_data="custom_skip_photo")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="custom_cancel")],
        [InlineKeyboardButton(HOME_BUTTON_TEXT, callback_data="home_inline")],
    ])


async def custom_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["custom_order"] = {}

    await update.message.reply_text(
        tr(update.effective_user.id, "custom_start")
    )

    return CUSTOM_NAME


async def custom_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text(tr(update.effective_user.id, "name_empty"))
        return CUSTOM_NAME

    context.user_data.setdefault("custom_order", {})["name"] = name

    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(tr(update.effective_user.id, "share_phone"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await update.message.reply_text(
        tr(update.effective_user.id, "phone_prompt"),
        reply_markup=keyboard,
    )

    return CUSTOM_PHONE


async def custom_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    if not phone:
        await update.message.reply_text(tr(update.effective_user.id, "phone_empty"))
        return CUSTOM_PHONE

    context.user_data.setdefault("custom_order", {})["phone"] = phone

    await update.message.reply_text(
        tr(update.effective_user.id, "custom_choose_category"),
        reply_markup=_category_keyboard(),
    )

    return CUSTOM_CATEGORY


async def custom_choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await delete_callback_message(query)

    if query.data == "custom_back_categories":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=tr(query.from_user.id, "custom_choose_category_short"),
            reply_markup=_category_keyboard(),
        )
        return CUSTOM_CATEGORY

    category = query.data.replace("custom_category_", "", 1)

    if category not in get_categories():
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=tr(query.from_user.id, "category_not_found"),
            reply_markup=_category_keyboard(),
        )
        return CUSTOM_CATEGORY

    products = get_all_products(category=category)

    if not products:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=tr(query.from_user.id, "category_empty").format(category=category),
            reply_markup=_category_keyboard(),
        )
        return CUSTOM_CATEGORY

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"{category}:\n{tr(query.from_user.id, 'custom_choose_base')}",
        reply_markup=_products_keyboard(products),
    )

    return CUSTOM_PRODUCT


async def custom_choose_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await delete_callback_message(query)

    product_id = int(query.data.split("_")[-1])
    product = get_product(product_id)

    if not product:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=tr(query.from_user.id, "product_not_found"),
            reply_markup=_category_keyboard(),
        )
        return CUSTOM_CATEGORY

    context.user_data.setdefault("custom_order", {})["product_id"] = product_id
    context.user_data.setdefault("custom_order", {})["product_name"] = product["name"]

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=tr(query.from_user.id, "custom_chosen_product").format(name=product["name"]),
    )

    return CUSTOM_DESCRIPTION


async def custom_get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text.strip()

    if len(description) < 5:
        await update.message.reply_text(tr(update.effective_user.id, "description_too_short"))
        return CUSTOM_DESCRIPTION

    context.user_data.setdefault("custom_order", {})["description"] = description

    await update.message.reply_text(
        tr(update.effective_user.id, "custom_date_prompt")
    )

    return CUSTOM_DATE


async def custom_get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text.strip()

    if not date:
        await update.message.reply_text(tr(update.effective_user.id, "date_empty"))
        return CUSTOM_DATE

    context.user_data.setdefault("custom_order", {})["date"] = date

    await update.message.reply_text(
        tr(update.effective_user.id, "custom_photo_prompt"),
        reply_markup=_skip_photo_keyboard(update.effective_user.id),
    )

    return CUSTOM_PHOTO


async def custom_get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = ""

    if update.message and update.message.photo:
        photo = update.message.photo[-1].file_id

    return await _save_custom_order(update, context, photo)


async def custom_skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await delete_callback_message(query)

    return await _save_custom_order(update, context, "")


async def _save_custom_order(update: Update, context: ContextTypes.DEFAULT_TYPE, photo: str):
    user = update.effective_user
    data = context.user_data.get("custom_order", {})

    name = data.get("name", "Клієнт")
    phone = data.get("phone", "")
    product_id = data.get("product_id")
    product_name = data.get("product_name", "")
    description = data.get("description", "")
    date = data.get("date", "")

    order_id = create_custom_order_db(
        user_id=user.id,
        name=name,
        phone=phone,
        product_id=product_id,
        product_name=product_name,
        description=description,
        date=date,
        photo=photo,
    )

    context.user_data.pop("custom_order", None)

    chat_id = update.effective_chat.id

    text = f"""
Нове індивідуальне замовлення C#{order_id} 🎂

Ім'я: {name}
Телефон: {phone}
Дата: {date}
Базовий десерт: {product_name}

Опис:
{description}
"""

    if photo:
        admin_notified = await notify_admins_photo(
            context=context,
            photo=photo,
            caption=text,
        )
    else:
        admin_notified = await notify_admins_text(
            context=context,
            text=text,
        )

    if admin_notified > 0:
        confirmation_text = tr(user.id, "custom_created_ok").format(id=order_id)
    else:
        confirmation_text = tr(user.id, "custom_created_no_admin").format(id=order_id)

    await context.bot.send_message(
        chat_id=chat_id,
        text=confirmation_text,
        reply_markup=ReplyKeyboardRemove(),
    )

    contact_keyboard = admin_contact_keyboard(user.id)
    if contact_keyboard:
        await context.bot.send_message(
            chat_id=chat_id,
            text=tr(user.id, "need_details"),
            reply_markup=contact_keyboard,
        )

    await context.bot.send_message(
        chat_id=chat_id,
        text=tr(user.id, "home_menu"),
        reply_markup=get_main_menu(user.id),
    )

    return ConversationHandler.END


async def custom_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("custom_order", None)

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await delete_callback_message(query)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=tr(query.from_user.id, "custom_cancelled")
        )
    elif update.message:
        await update.message.reply_text(tr(update.effective_user.id, "custom_cancelled"))

    return ConversationHandler.END
