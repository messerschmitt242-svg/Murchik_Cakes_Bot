from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN
from database.db import init_db

from handlers.start import start
from handlers.id import get_id
from handlers.faq import faq
from handlers.contacts import contacts
from handlers.products import show_products
from handlers.my_orders import my_orders
from handlers.admin_orders import list_orders, set_status
from handlers.delete_product import delete_product, delete_product_callback

from handlers.add_product import (
    add_product_start,
    add_photo,
    finish_add_photos,
    add_name,
    add_price,
    add_description,
    cancel_add_product,
    ADD_PHOTO,
    ADD_NAME,
    ADD_PRICE,
    ADD_DESCRIPTION,
)

from handlers.cart import (
    add_to_cart,
    show_cart,
    plus_item,
    minus_item,
    delete_item,
    checkout_start,
    checkout_get_name,
    checkout_get_phone,
    checkout_cancel,
    CART_NAME,
    CART_PHONE,
)


async def error_handler(update, context):
    print("ERROR:")
    print(context.error)


def build_app():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    add_product_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_product_start)],
        states={
            ADD_PHOTO: [
                MessageHandler(filters.PHOTO, add_photo),
                CallbackQueryHandler(finish_add_photos, pattern="^finish_add_photos$"),
            ],
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_price)],
            ADD_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_description)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_add_product),
            CallbackQueryHandler(cancel_add_product, pattern="^cancel_add_product$"),
        ],
        allow_reentry=True,
    )

    checkout_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(checkout_start, pattern="^cart_checkout$")],
        states={
            CART_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_get_name)],
            CART_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), checkout_get_phone)],
        },
        fallbacks=[CommandHandler("cancel", checkout_cancel)],
        allow_reentry=True,
    )

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("orders", list_orders))
    app.add_handler(CommandHandler("set_status", set_status))
    app.add_handler(CommandHandler("delete_product", delete_product))

    # Диалоги должны стоять выше обычных текстовых кнопок
    app.add_handler(add_product_handler)
    app.add_handler(checkout_handler)

    # Inline-кнопки
    app.add_handler(CallbackQueryHandler(delete_product_callback, pattern="^delete_product_\\d+$"))
    app.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_\\d+$"))
    app.add_handler(CallbackQueryHandler(plus_item, pattern="^cart_plus_\\d+$"))
    app.add_handler(CallbackQueryHandler(minus_item, pattern="^cart_minus_\\d+$"))
    app.add_handler(CallbackQueryHandler(delete_item, pattern="^cart_del_\\d+$"))

    # Главное меню
    app.add_handler(MessageHandler(filters.Regex("^🍰 Каталог$"), show_products))
    app.add_handler(MessageHandler(filters.Regex("^🛒 Кошик$"), show_cart))
    app.add_handler(MessageHandler(filters.Regex("^📦 Мої замовлення$"), my_orders))
    app.add_handler(MessageHandler(filters.Regex("^❓ FAQ$"), faq))
    app.add_handler(MessageHandler(filters.Regex("^📍 Контакти$"), contacts))

    app.add_error_handler(error_handler)
    return app


if __name__ == "__main__":
    application = build_app()
    print("Bot started")
    application.run_polling()
