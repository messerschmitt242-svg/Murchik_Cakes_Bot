from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.products_db import get_all_products
from database.db import get_conn


# =========================
# ➕ ADD TO CART
# =========================
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[1])

    products = get_all_products()
    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        await query.message.reply_text("Товар не найден ❌")
        return

    cart = context.user_data.get("cart", {})

    pid = str(product_id)

    if pid in cart:
        cart[pid]["qty"] += 1
    else:
        cart[pid] = {
            "name": product["name"],
            "price": product["price"],
            "qty": 1
        }

    context.user_data["cart"] = cart

    await query.message.reply_text(f"➕ Додано: {product['name']}")


# =========================
# 🛒 SHOW CART
# =========================
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cart = context.user_data.get("cart", {})

    if not cart:
        await update.message.reply_text("Кошик порожній 🛒")
        return

    text = "🛒 Ваш кошик:\n\n"
    total = 0

    keyboard = []

    for pid, item in cart.items():

        sum_item = item["price"] * item["qty"]
        total += sum_item

        text += f"{item['name']} x{item['qty']} = {sum_item} zł\n"

        keyboard.append([
            InlineKeyboardButton("➕", callback_data=f"plus_{pid}"),
            InlineKeyboardButton("➖", callback_data=f"minus_{pid}"),
            InlineKeyboardButton("🗑", callback_data=f"del_{pid}")
        ])

    text += f"\n💰 Разом: {total} zł"

    keyboard.append([
        InlineKeyboardButton("📦 Оформити замовлення", callback_data="checkout")
    ])

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# ➕ PLUS
# =========================
async def plus_item(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    pid = query.data.split("_")[1]

    cart = context.user_data.get("cart", {})

    if pid in cart:
        cart[pid]["qty"] += 1

    context.user_data["cart"] = cart

    await query.message.edit_text("Оновлено ➕")


# =========================
# ➖ MINUS
# =========================
async def minus_item(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    pid = query.data.split("_")[1]

    cart = context.user_data.get("cart", {})

    if pid in cart:
        cart[pid]["qty"] -= 1

        if cart[pid]["qty"] <= 0:
            del cart[pid]

    context.user_data["cart"] = cart

    await query.message.edit_text("Оновлено ➖")


# =========================
# 🗑 DELETE ITEM
# =========================
async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    pid = query.data.split("_")[1]

    cart = context.user_data.get("cart", {})

    if pid in cart:
        del cart[pid]

    context.user_data["cart"] = cart

    await query.message.edit_text("Видалено 🗑")


# =========================
# 📦 CHECKOUT
# =========================
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    cart = context.user_data.get("cart", {})

    if not cart:
        await query.message.reply_text("Кошик порожній 🛒")
        return

    items_text = ""
    total = 0

    for item in cart.values():
        sum_item = item["price"] * item["qty"]
        total += sum_item
        items_text += f"{item['name']} x{item['qty']}\n"

    context.user_data["order_items"] = items_text
    context.user_data["order_total"] = total

    await query.message.reply_text("Ваше ім'я:")
    return "NAME"


# =========================
# 💾 SAVE ORDER
# =========================
async def save_order(update: Update, context: ContextTypes.DEFAULT_TYPE):

    name = update.message.text
    phone = context.user_data.get("phone")

    items = context.user_data.get("order_items")
    total = context.user_data.get("order_total")

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders (user_id, name, phone, items, total, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        update.effective_user.id,
        name,
        phone,
        items,
        total,
        "Прийнято"
    ))

    conn.commit()
    conn.close()

    context.user_data["cart"] = {}

    await update.message.reply_text("✅ Замовлення прийнято")
