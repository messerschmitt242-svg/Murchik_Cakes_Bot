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
from handlers.maintenance import clear_test_data
from handlers.home import go_home, go_home_inline, HOME_BUTTON_TEXT
from handlers.language import language_menu, set_language
from handlers.pickup import pickup_info

from handlers.start import start
from handlers.id import get_id
from handlers.faq import faq
from handlers.contacts import contacts
from handlers.products import (
    show_products,
    show_category_products,
    show_product_detail,
    catalog_back,
)
from handlers.my_orders import my_orders
from handlers.admin_orders import (
    list_orders,
    set_status,
    active_orders,
    show_admin_order,
    show_admin_custom_order,
    advance_order_status,
    advance_custom_order_status,
)
from handlers.delete_product import delete_product, delete_product_callback
from handlers.promo import (
    promo_menu,
    promo_start,
    promo_get_code,
    promo_choose_discount,
    promo_cancel,
    PROMO_CODE_INPUT,
    PROMO_DISCOUNT_SELECT,
)

from handlers.add_product import (
    add_product_start,
    add_photo,
    finish_add_photos,
    add_name,
    add_price,
    add_description,
    choose_category,
    cancel_add_product,
    ADD_PHOTO,
    ADD_NAME,
    ADD_PRICE,
    ADD_DESCRIPTION,
    ADD_CATEGORY,
)

from handlers.cart import (
    add_to_cart,
    show_cart,
    plus_item,
    minus_item,
    delete_item,
    promo_start as cart_promo_start,
    promo_apply as cart_promo_apply,
    promo_cancel as cart_promo_cancel,
    checkout_start,
    checkout_get_name,
    checkout_get_phone,
    checkout_cancel,
    CART_NAME,
    CART_PHONE,
    PROMO_CODE,
)

from handlers.favorites import (
    toggle_favorite,
    show_favorites,
)

from handlers.reviews import (
    review_start,
    reviews_view,
    reviews_leave,
    review_type_bakery,
    review_type_product,
    review_choose_product,
    review_get_text,
    review_choose_rating,
    review_cancel,
    show_reviews_admin,
    show_product_reviews,
    delete_review_admin,
    REVIEW_MENU,
    REVIEW_TYPE,
    REVIEW_PRODUCT,
    REVIEW_TEXT,
    REVIEW_RATING,
)

from handlers.custom_order import (
    custom_order_start,
    custom_get_name,
    custom_get_phone,
    custom_choose_category,
    custom_choose_product,
    custom_get_description,
    custom_get_date,
    custom_get_photo,
    custom_skip_photo,
    custom_cancel,
    CUSTOM_NAME,
    CUSTOM_PHONE,
    CUSTOM_CATEGORY,
    CUSTOM_PRODUCT,
    CUSTOM_DESCRIPTION,
    CUSTOM_DATE,
    CUSTOM_PHOTO,
)


async def error_handler(update, context):
    print("ERROR:")
    print(context.error)


def build_app():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    add_product_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^➕ Додати продукт$"), add_product_start),
        ],
        states={
            ADD_PHOTO: [
                MessageHandler(filters.PHOTO, add_photo),
                CallbackQueryHandler(finish_add_photos, pattern="^finish_add_photos$"),
            ],
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_price)],
            ADD_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_description)],
            ADD_CATEGORY: [CallbackQueryHandler(choose_category, pattern="^add_category_")],
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

    cart_promo_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(cart_promo_start, pattern=r"^cart_promo_\d+$")],
        states={
            PROMO_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cart_promo_apply)],
        },
        fallbacks=[CommandHandler("cancel", cart_promo_cancel)],
        allow_reentry=True,
    )

    promo_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(promo_start, pattern="^promo_create$")],
        states={
            PROMO_CODE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, promo_get_code)],
            PROMO_DISCOUNT_SELECT: [
                CallbackQueryHandler(promo_choose_discount, pattern="^promo_discount_(10|20)$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", promo_cancel),
            CallbackQueryHandler(promo_cancel, pattern="^promo_cancel$"),
        ],
        allow_reentry=True,
    )


    review_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💬 Відгуки$"), review_start),
        ],
        states={
            REVIEW_MENU: [
                CallbackQueryHandler(reviews_view, pattern="^reviews_view$"),
                CallbackQueryHandler(reviews_leave, pattern="^reviews_leave$"),
            ],
            REVIEW_TYPE: [
                CallbackQueryHandler(review_type_bakery, pattern="^review_type_bakery$"),
                CallbackQueryHandler(review_type_product, pattern="^review_type_product$"),
            ],
            REVIEW_PRODUCT: [
                CallbackQueryHandler(review_choose_product, pattern=r"^review_product_\d+$"),
            ],
            REVIEW_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, review_get_text),
            ],
            REVIEW_RATING: [
                CallbackQueryHandler(review_choose_rating, pattern=r"^review_rating_[1-5]$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", review_cancel),
            CallbackQueryHandler(review_cancel, pattern="^review_cancel$"),
        ],
        allow_reentry=True,
    )

    custom_order_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🎂 Індивідуальне замовлення$"), custom_order_start),
        ],
        states={
            CUSTOM_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, custom_get_name),
            ],
            CUSTOM_PHONE: [
                MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), custom_get_phone),
            ],
            CUSTOM_CATEGORY: [
                CallbackQueryHandler(custom_choose_category, pattern="^custom_category_"),
            ],
            CUSTOM_PRODUCT: [
                CallbackQueryHandler(custom_choose_product, pattern=r"^custom_product_\d+$"),
                CallbackQueryHandler(custom_choose_category, pattern="^custom_back_categories$"),
            ],
            CUSTOM_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, custom_get_description),
            ],
            CUSTOM_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, custom_get_date),
            ],
            CUSTOM_PHOTO: [
                MessageHandler(filters.PHOTO, custom_get_photo),
                CallbackQueryHandler(custom_skip_photo, pattern="^custom_skip_photo$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", custom_cancel),
            CallbackQueryHandler(custom_cancel, pattern="^custom_cancel$"),
        ],
        allow_reentry=True,
    )

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("orders", list_orders))
    app.add_handler(CommandHandler("set_status", set_status))
    app.add_handler(CommandHandler("clear_test_data", clear_test_data))
    app.add_handler(MessageHandler(filters.Regex(f"^{HOME_BUTTON_TEXT}$"), go_home))
    app.add_handler(CallbackQueryHandler(go_home_inline, pattern="^home_inline$"))
    app.add_handler(CallbackQueryHandler(pickup_info, pattern=r"^pickup_(order|custom_order)_\d+$"))

    # Адмінські приховані кнопки головного меню
    app.add_handler(MessageHandler(filters.Regex("^🗑 Видалити продукт$"), delete_product))
    app.add_handler(MessageHandler(filters.Regex("^🎟 Промокоди$"), promo_menu))

    # Диалоги должны стоять выше обычных текстовых кнопок
    app.add_handler(add_product_handler)
    app.add_handler(checkout_handler)
    app.add_handler(cart_promo_handler)
    app.add_handler(promo_handler)
    app.add_handler(review_handler)
    app.add_handler(custom_order_handler)

    # Inline-кнопки каталога
    app.add_handler(CallbackQueryHandler(catalog_back, pattern="^catalog_back$"))
    app.add_handler(CallbackQueryHandler(show_category_products, pattern="^catalog_category_"))
    app.add_handler(CallbackQueryHandler(show_product_detail, pattern=r"^catalog_product_\d+$"))
    app.add_handler(CallbackQueryHandler(toggle_favorite, pattern=r"^favorite_\d+$"))
    app.add_handler(CallbackQueryHandler(show_product_reviews, pattern=r"^product_reviews_\d+$"))
    app.add_handler(CallbackQueryHandler(delete_review_admin, pattern=r"^delete_review_\d+$"))

    # Inline-кнопки админки и удаления
    app.add_handler(CallbackQueryHandler(delete_product_callback, pattern=r"^delete_product_\d+$"))
    app.add_handler(CallbackQueryHandler(show_admin_order, pattern=r"^admin_order_\d+$"))
    app.add_handler(CallbackQueryHandler(show_admin_custom_order, pattern=r"^admin_custom_order_\d+$"))
    app.add_handler(CallbackQueryHandler(advance_order_status, pattern=r"^admin_next_status_\d+$"))
    app.add_handler(CallbackQueryHandler(advance_custom_order_status, pattern=r"^admin_next_custom_status_\d+$"))

    # Inline-кнопки корзины
    app.add_handler(CallbackQueryHandler(add_to_cart, pattern=r"^add_\d+$"))
    app.add_handler(CallbackQueryHandler(plus_item, pattern=r"^cart_plus_\d+$"))
    app.add_handler(CallbackQueryHandler(minus_item, pattern=r"^cart_minus_\d+$"))
    app.add_handler(CallbackQueryHandler(delete_item, pattern=r"^cart_del_\d+$"))

    # Главное меню
    app.add_handler(MessageHandler(filters.Regex("^🍰 Каталог$"), show_products))
    app.add_handler(MessageHandler(filters.Regex("^🛒 Кошик$"), show_cart))
    app.add_handler(MessageHandler(filters.Regex("^📦 Мої замовлення$"), my_orders))
    app.add_handler(MessageHandler(filters.Regex("^❤️ Обране$"), show_favorites))
    app.add_handler(MessageHandler(filters.Regex("^📋 Активні замовлення$"), active_orders))
    app.add_handler(CommandHandler("reviews", show_reviews_admin))
    app.add_handler(MessageHandler(filters.Regex("^❓ FAQ$"), faq))
    app.add_handler(MessageHandler(filters.Regex("^📍 Контакти$"), contacts))

    app.add_error_handler(error_handler)
    return app


if __name__ == "__main__":
    application = build_app()
    print("Bot started")
    application.run_polling()


app.add_handler(MessageHandler(filters.Regex("🌐 Мова|🌐 Язык|🌐 Język|🌐 Language"), language_menu))
app.add_handler(CallbackQueryHandler(set_language, pattern=r"^lang_"))
