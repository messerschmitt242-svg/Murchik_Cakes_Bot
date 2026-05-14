from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters
)

from config import BOT_TOKEN
from handlers.start import start
from handlers.id import get_id
from handlers.catalog import catalog
from handlers.faq import faq
from handlers.products import show_products
from handlers.delete_product import delete_product, confirm_delete
from handlers.add_product import finish_add
from handlers.catalog import catalog
from handlers.my_orders import my_orders
from handlers.contacts import contacts
from handlers.add_product import (
    add_product_start,
    add_photo,
    add_name,
    PHOTO,
    NAME
)


from handlers.order import (
    order_start,
    get_name,
    get_phone,
    get_cake,
    NAME,
    PHONE,
    CAKE
)

from database.db import init_db

init_db()

app = Application.builder().token(
    BOT_TOKEN
).build()

app.add_handler(CommandHandler("delete_product", delete_product))

app.add_handler(
    MessageHandler(filters.Regex("📦 Мої замовлення"), my_orders)
)

app.add_handler(
    CallbackQueryHandler(finish_add, pattern="finish_add")
)

app.add_handler(
    MessageHandler(filters.Regex("📍 Контакти"), contacts)
)

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CommandHandler(
        "id",
        get_id
    )
)

app.add_handler(
    MessageHandler(
        filters.Regex("🍰 Каталог"),
        show_products
    )
)

app.add_handler(
    MessageHandler(
        filters.Regex("❓ FAQ"),
        faq
    )
)

order_handler = ConversationHandler(
    entry_points=[
        MessageHandler(
            filters.Regex("🎂 Замовити"),
            order_start
        )
    ],

    states={

        NAME:[
            MessageHandler(
                filters.TEXT,
                get_name
            )
        ],

        PHONE: [
            MessageHandler(
                filters.CONTACT | filters.TEXT,
                get_phone
            )
        ],

        CAKE:[
            MessageHandler(
                filters.TEXT,
                get_cake
            )
        ]
    },

    fallbacks=[]
)

app.add_handler(
    order_handler
)

add_product_handler = ConversationHandler(
    entry_points=[
        CommandHandler("add", add_product_start)
    ],
    states={
        PHOTO: [
            MessageHandler(filters.PHOTO | filters.TEXT, add_photo)
        ],
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)]
    },
    fallbacks=[]
)

app.add_handler(add_product_handler)

app.add_handler(MessageHandler(filters.TEXT, confirm_delete))

print("Bot started")

app.run_polling()
