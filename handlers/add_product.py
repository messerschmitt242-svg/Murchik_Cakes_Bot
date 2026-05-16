from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import is_admin
from database.products_db import add_product, CATEGORIES
from handlers.cleanup import delete_callback_message
from handlers.home import HOME_BUTTON_TEXT

ADD_PHOTO = 100
ADD_NAME = 101
ADD_PRICE = 102
ADD_DESCRIPTION = 103
ADD_CATEGORY = 104
ADD_PORTION = 105
ADD_LABEL = 106


def _finish_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Завершити фото", callback_data="finish_add_photos")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_add_product")],
        [InlineKeyboardButton(HOME_BUTTON_TEXT, callback_data="home_inline")],
    ])


def _category_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎂 Торти", callback_data="add_dessert_category_Торти")],
        [InlineKeyboardButton("🧁 Тістечка", callback_data="add_dessert_category_Тістечка")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="cancel_add_product")],
        [InlineKeyboardButton(HOME_BUTTON_TEXT, callback_data="home_inline")],
    ])


async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END

    context.user_data["add_product"] = {"photos": []}
    print("ADD_DESSERT_FLOW_START")
    await update.message.reply_text(
        "Надішліть живі фото товару 🍰\n\nМожна надіслати декілька фото. Після останнього фото натисніть кнопку нижче.",
        reply_markup=_finish_keyboard(),
    )
    return ADD_PHOTO


async def add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.setdefault("add_product", {"photos": []})
    if not update.message or not update.message.photo:
        await update.message.reply_text("❌ Надішліть саме фото товару.", reply_markup=_finish_keyboard())
        return ADD_PHOTO

    data["photos"].append(update.message.photo[-1].file_id)
    await update.message.reply_text(f"Фото додано ✅ ({len(data['photos'])})", reply_markup=_finish_keyboard())
    return ADD_PHOTO


async def finish_add_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = context.user_data.get("add_product", {"photos": []})
    chat_id = query.message.chat_id
    await delete_callback_message(query)

    if not data.get("photos"):
        await context.bot.send_message(chat_id=chat_id, text="Спочатку додайте хоча б одне живе фото.", reply_markup=_finish_keyboard())
        return ADD_PHOTO

    await context.bot.send_message(chat_id=chat_id, text="Напишіть назву товару:")
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

    context.user_data.setdefault("add_product", {"photos": []})["price"] = price
    await update.message.reply_text("Напишіть опис товару:")
    return ADD_DESCRIPTION


async def add_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.setdefault("add_product", {"photos": []})
    data["description"] = update.message.text.strip()
    if not data["description"]:
        await update.message.reply_text("Опис не може бути порожнім. Напишіть опис товару:")
        return ADD_DESCRIPTION

    await update.message.reply_text("Оберіть категорію товару:", reply_markup=_category_keyboard())
    return ADD_CATEGORY


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("add_dessert_category_", "", 1)
    chat_id = query.message.chat_id
    await delete_callback_message(query)

    if category not in CATEGORIES:
        await context.bot.send_message(chat_id=chat_id, text="❌ Невідома категорія. Оберіть категорію ще раз:", reply_markup=_category_keyboard())
        return ADD_CATEGORY

    data = context.user_data.setdefault("add_product", {"photos": []})
    data["category"] = category
    print("ADD_DESSERT_CATEGORY_CHOSEN:", category)

    example = "Наприклад: 1 кг або 1.5 кг" if category == "Торти" else "Наприклад: ≈ 9 шт або ≈ 12 шт"
    await context.bot.send_message(chat_id=chat_id, text=f"Вкажіть порцію товару 📦\n\n{example}")
    return ADD_PORTION


async def add_portion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.setdefault("add_product", {"photos": []})
    portion = update.message.text.strip()
    if not portion:
        await update.message.reply_text("Порція не може бути порожньою.")
        return ADD_PORTION

    data["portion"] = portion
    print("ADD_DESSERT_PORTION_RECEIVED:", portion)
    await update.message.reply_text(
        "Надішліть ярлик товару 🖼\n\nЦе красива квадратна картинка для каталогу Mini App. Живі фото вже додані раніше."
    )
    return ADD_LABEL


async def add_label(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.setdefault("add_product", {"photos": []})
    if not update.message or not update.message.photo:
        await update.message.reply_text("❌ Надішліть саме фото-ярлик товару.")
        return ADD_LABEL

    data["label_image"] = update.message.photo[-1].file_id
    print("ADD_DESSERT_SAVING_AFTER_LABEL_ONLY")

    product_id = add_product(
        name=data.get("name", ""),
        price=data.get("price", 0),
        description=data.get("description", ""),
        photos=data.get("photos", []),
        category=data.get("category", "Торти"),
        portion=data.get("portion", ""),
        label_image=data.get("label_image", ""),
    )

    context.user_data.pop("add_product", None)
    await update.message.reply_text(f"✅ Товар додано!\nID: {product_id}")
    return ConversationHandler.END


async def cancel_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("add_product", None)
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await delete_callback_message(query)
        await context.bot.send_message(chat_id=query.message.chat_id, text="Додавання товару скасовано ❌")
    elif update.message:
        await update.message.reply_text("Додавання товару скасовано ❌")
    return ConversationHandler.END
