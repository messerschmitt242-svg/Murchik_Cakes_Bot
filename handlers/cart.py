from telegram import Update
from telegram.ext import ContextTypes

from database.products_db import get_all_products


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

    if str(product_id) in cart:
        cart[str(product_id)]["qty"] += 1
    else:
        cart[str(product_id)] = {
            "name": product["name"],
            "price": product["price"],
            "qty": 1
        }

    context.user_data["cart"] = cart

    await query.message.reply_text(f"Добавлено: {product['name']} 🛒")


async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cart = context.user_data.get("cart", {})

    if not cart:
        await update.message.reply_text("Кошик порожній 🛒")
        return

    text = "🛒 Ваш кошик:\n\n"
    total = 0

    for item in cart.values():
        sum_item = item["price"] * item["qty"]
        total += sum_item
        text += f"{item['name']} x{item['qty']} = {sum_item} zł\n"

    text += f"\n💰 Разом: {total} zł"

    await update.message.reply_text(text)
