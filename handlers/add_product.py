from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import is_admin
from database.products_db import add_product, CATEGORIES

ADD_PHOTO = 100
ADD_NAME = 101
ADD_PRICE = 102
ADD_DESCRIPTION = 103
ADD_CATEGORY = 104


def _finish_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Завершити фото", callback_data="finish_add_photos")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_add_product")],
    ])


def _category_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎂 Торти", callback_data="add_category_Торти")],
        [InlineKeyboardButton("🧁 Тістечка", callback_data="add_category_Тістечка")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_add_product")],
    ])


async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != is_admin():
        return ConversationHandler.END

    context.user_data["add_product"] = {"photos": []}

    await update.message.reply_text(
        "Надішліть фото товару 🍰\n\nМожна надіслати декілька фото. Після останнього фото натисніть кнопку нижче.",
        reply_markup=_finish_keyboard(),
    )

    return ADD_PHOTO


async def add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.setdefault("add_product", {"photos": []})

    if not update.message or not update.message.photo:
        await update.message.reply_text(
            "❌ Надішліть саме фото товару.",
            reply_markup=_finish_keyboard(),
        )
        return ADD_PHOTO

    photo_id = update.message.photo[-1].file_id
    data["photos"].append(photo_id)

    await update.message.reply_text(
        f"Фото додано ✅ ({len(data['photos'])})",
        reply_markup=_finish_keyboard(),
    )

    return ADD_PHOTO


async def finish_add_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = context.user_data.get("add_product", {"photos": []})

    if not data.get("photos"):
        await query.message.reply_text(
            "Спочатку додайте хоча б одне фото.",
            reply_markup=_finish_keyboard(),
        )
        return ADD_PHOTO

    await query.message.reply_text("Напишіть назву товару:")
    return ADD_NAME


async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.setdefault("add_product", {"photos": []})
    data["name"] = update.message.text.strip()

    if not data["name"]:
        await update.message.reply_text("Назва не може бути порожньою. Напишіть назву товару:")
        return ADD_NAME

    await update.message.reply_text("Вкажіть ціну у zł, наприклад: 120 або 120.50")
    return ADD_PRICE


async def add_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_price = update.message.text.strip().replace(",", ".")

    try:
        price = float(raw_price)
    except ValueError:
        await update.message.reply_text("❌ Ціна має бути числом. Наприклад: 120 або 120.50")
        return ADD_PRICE

    data = context.user_data.setdefault("add_product", {"photos": []})
    data["price"] = price

    await update.message.reply_text("Напишіть опис товару:")
    return ADD_DESCRIPTION


async def add_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.setdefault("add_product", {"photos": []})
    data["description"] = update.message.text.strip()

    if not data["description"]:
        await update.message.reply_text("Опис не може бути порожнім. Напишіть опис товару:")
        return ADD_DESCRIPTION

    await update.message.reply_text(
        "Оберіть категорію, куди додати товар:",
        reply_markup=_category_keyboard(),
    )
    return ADD_CATEGORY


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("add_category_", "", 1)
    if category not in CATEGORIES:
        await query.message.reply_text("❌ Невідома категорія. Оберіть категорію ще раз:", reply_markup=_category_keyboard())
        return ADD_CATEGORY

    data = context.user_data.get("add_product", {})
    name = data.get("name")
    price = data.get("price", 0)
    description = data.get("description", "")
    photos = data.get("photos", [])

    product_id = add_product(
        name=name,
        price=price,
        description=description,
        photos=photos,
        category=category,
    )

    context.user_data.pop("add_product", None)

    await query.message.reply_text(
        f"✅ Товар збережено у каталозі.\n\nID: {product_id}\nНазва: {name}\nКатегорія: {category}\nЦіна: {price:.2f} zł"
    )

    return ConversationHandler.END


async def cancel_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text("❌ Додавання товару скасовано.")
    elif update.message:
        await update.message.reply_text("❌ Додавання товару скасовано.")

    context.user_data.pop("add_product", None)
    return ConversationHandler.END
