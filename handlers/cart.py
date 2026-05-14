from telegram import Update
from telegram.ext import ContextTypes

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data.split("_")[1]

    product = PRODUCTS[product_id]

    cart = context.user_data.get("cart", {})

    if product_id in cart:
        cart[product_id]["qty"] += 1
    else:
        cart[product_id] = {
            "name": product["name"],
            "price": product.get("price", 0),
            "qty": 1
        }

    context.user_data["cart"] = cart

    await query.message.reply_text("Додано в кошик 🛒")
