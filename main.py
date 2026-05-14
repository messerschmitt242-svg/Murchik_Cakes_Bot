from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

from config import BOT_TOKEN
from handlers.start import start
from handlers.id import get_id
from handlers.catalog import catalog
from handlers.faq import faq
from handlers.products import show_cakes
from handlers.catalog import catalog

from handlers.order import (
    order_start,
    get_name,
    get_phone,
    get_cake,
    NAME,
    PHONE,
    CAKE
)

app = Application.builder().token(
    BOT_TOKEN
).build()

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
        catalog
    )
)

app.add_handler(
    MessageHandler(
        filters.Regex("🍰 Торти|🍮 Тістечка"),
        show_cakes
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

        PHONE:[
            MessageHandler(
                filters.TEXT,
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

print("Bot started")

app.run_polling()
