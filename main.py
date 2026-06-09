import warnings

warnings.filterwarnings(
    "ignore",
    message=r"If 'per_message=False'.*CallbackQueryHandler.*",
    category=UserWarning,
)

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
from handlers.admin_panel import admin_panel, admin_panel_callback
from handlers.product_translations import regenerate_translations
from handlers.home import go_home, go_home_inline
from handlers.language import language_menu, set_language
from handlers.pickup import pickup_info
from handlers.start import start
from handlers.id import get_id
from handlers.faq import faq
from handlers.contacts import contacts
from handlers.products import show_products, show_category_products, show_product_detail, catalog_back
from handlers.my_orders import my_orders
from handlers.admin_orders import (
    list_orders,
    orders_page,
    set_status,
    active_orders,
    show_admin_order,
    show_admin_custom_order,
    advance_order_status,
    advance_custom_order_status,
    cancel_order,
    cancel_custom_order,
    delete_order,
    delete_custom_order,
    add_order_to_tasks,
    add_custom_order_to_tasks,
)
from handlers.delete_product import delete_product, delete_product_callback
from handlers.promo import (
    promo_menu,
    promo_start,
    promo_get_code,
    promo_choose_discount,
    promo_choose_scope,
    promo_choose_product,
    promo_cancel,
    promo_delete_callback,
    PROMO_CODE_INPUT,
    PROMO_DISCOUNT_SELECT,
    PROMO_SCOPE_SELECT,
    PROMO_PRODUCT_SELECT,
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
from handlers.favorites import toggle_favorite, show_favorites
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
from handlers.update_photos import (
    update_photos_start,
    update_photos_choose_product,
    update_photos_add_photo,
    update_photos_finish,
    update_photos_cancel,
    UPDATE_PHOTOS_PRODUCT,
    UPDATE_PHOTOS_UPLOAD,
)

from handlers.calendar_export import send_order_calendar_file
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
            CallbackQueryHandler(add_product_start, pattern="^admin_panel_add_product$"),
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
        fallbacks=[CommandHandler("cancel", cancel_add_product), CallbackQueryHandler(cancel_add_product, pattern="^cancel_add_product$")],
        allow_reentry=True,
    )

    update_photos_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(update_photos_start, pattern="^admin_panel_update_photos$")],
        states={
            UPDATE_PHOTOS_PRODUCT: [CallbackQueryHandler(update_photos_choose_product, pattern=r"^update_photos_product_\d+$")],
            UPDATE_PHOTOS_UPLOAD: [
                MessageHandler(filters.PHOTO, update_photos_add_photo),
                CallbackQueryHandler(update_photos_finish, pattern="^update_photos_finish$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", update_photos_cancel),
            CallbackQueryHandler(update_photos_cancel, pattern="^update_photos_cancel$"),
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
        entry_points=[
            CallbackQueryHandler(cart_promo_start, pattern=r"^cart_promo_\d+$"),
            CallbackQueryHandler(cart_promo_start, pattern=r"^cart_promo_all$"),
        ],
        states={PROMO_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cart_promo_apply)]},
        fallbacks=[CommandHandler("cancel", cart_promo_cancel)],
        allow_reentry=True,
    )

    app.add_handler(CallbackQueryHandler(promo_delete_callback, pattern=r"^promo_delete_.+$"))

    promo_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(promo_start, pattern="^promo_create$")],
        states={
            PROMO_CODE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, promo_get_code)],
            PROMO_DISCOUNT_SELECT: [CallbackQueryHandler(promo_choose_discount, pattern="^promo_discount_(10|20)$")],
            PROMO_SCOPE_SELECT: [CallbackQueryHandler(promo_choose_scope, pattern="^promo_scope_(cart|product)$")],
            PROMO_PRODUCT_SELECT: [CallbackQueryHandler(promo_choose_product, pattern=r"^promo_product_\d+$")],
        },
        fallbacks=[CommandHandler("cancel", promo_cancel), CallbackQueryHandler(promo_cancel, pattern="^promo_cancel$")],
        allow_reentry=True,
    )

    review_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^⭐ (Відгуки|Отзывы|Opinie|Reviews)$"), review_start)],
        states={
            REVIEW_MENU: [CallbackQueryHandler(reviews_view, pattern="^reviews_view$"), CallbackQueryHandler(reviews_leave, pattern="^reviews_leave$")],
            REVIEW_TYPE: [CallbackQueryHandler(review_type_bakery, pattern="^review_type_bakery$"), CallbackQueryHandler(review_type_product, pattern="^review_type_product$")],
            REVIEW_PRODUCT: [CallbackQueryHandler(review_choose_product, pattern=r"^review_product_\d+$")],
            REVIEW_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_get_text)],
            REVIEW_RATING: [CallbackQueryHandler(review_choose_rating, pattern=r"^review_rating_[1-5]$")],
        },
        fallbacks=[CommandHandler("cancel", review_cancel), CallbackQueryHandler(review_cancel, pattern="^review_cancel$")],
        allow_reentry=True,
    )

    custom_order_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^🎂 (Індивідуальне замовлення|Индивидуальный заказ|Zamówienie indywidualne|Custom order)$"), custom_order_start)],
        states={
            CUSTOM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_get_name)],
            CUSTOM_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), custom_get_phone)],
            CUSTOM_CATEGORY: [CallbackQueryHandler(custom_choose_category, pattern="^custom_category_")],
            CUSTOM_PRODUCT: [CallbackQueryHandler(custom_choose_product, pattern=r"^custom_product_\d+$"), CallbackQueryHandler(custom_choose_category, pattern="^custom_back_categories$")],
            CUSTOM_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_get_description)],
            CUSTOM_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_get_date)],
            CUSTOM_PHOTO: [MessageHandler(filters.PHOTO, custom_get_photo), CallbackQueryHandler(custom_skip_photo, pattern="^custom_skip_photo$")],
        },
        fallbacks=[CommandHandler("cancel", custom_cancel), CallbackQueryHandler(custom_cancel, pattern="^custom_cancel$")],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("orders", list_orders))
    app.add_handler(CommandHandler("set_status", set_status))
    app.add_handler(CommandHandler("clear_test_data", clear_test_data))
    app.add_handler(CommandHandler("regen_translations", regenerate_translations))

    app.add_handler(MessageHandler(filters.Regex(r"^🏠 (Повернутися до головного меню|Вернуться в главное меню|Wróć do menu głównego|Back to main menu)$"), go_home))
    app.add_handler(CallbackQueryHandler(go_home_inline, pattern="^home_inline$"))
    app.add_handler(MessageHandler(filters.Regex(r"^🌐 (Мова|Язык|Język|Language|Мова / Язык / Język / Language)$"), language_menu))
    app.add_handler(CallbackQueryHandler(set_language, pattern=r"^lang_"))
    app.add_handler(CallbackQueryHandler(pickup_info, pattern=r"^pickup_(order|custom_order)_\d+$"))

    app.add_handler(MessageHandler(filters.Regex("^🗑️ Видалити продукт$"), delete_product))
    app.add_handler(MessageHandler(filters.Regex("^🎁 Промокоди$"), promo_menu))
    app.add_handler(MessageHandler(filters.Regex("^🛠 Адмін-панель$"), admin_panel))

    app.add_handler(add_product_handler)
    app.add_handler(update_photos_handler)
    app.add_handler(checkout_handler)
    app.add_handler(cart_promo_handler)
    app.add_handler(promo_handler)
    app.add_handler(review_handler)
    app.add_handler(custom_order_handler)

    app.add_handler(CallbackQueryHandler(catalog_back, pattern="^catalog_back$"))
    app.add_handler(CallbackQueryHandler(show_category_products, pattern="^catalog_category_"))
    app.add_handler(CallbackQueryHandler(show_product_detail, pattern=r"^catalog_product_\d+$"))
    app.add_handler(CallbackQueryHandler(toggle_favorite, pattern=r"^favorite_\d+$"))
    app.add_handler(CallbackQueryHandler(show_product_reviews, pattern=r"^product_reviews_\d+$"))
    app.add_handler(CallbackQueryHandler(delete_review_admin, pattern=r"^delete_review_\d+$"))

    app.add_handler(CallbackQueryHandler(admin_panel_callback, pattern=r"^admin_panel_"))

    app.add_handler(CallbackQueryHandler(delete_product_callback, pattern=r"^delete_product_\d+$"))
    app.add_handler(CallbackQueryHandler(orders_page, pattern=r"^admin_orders_page_\d+$"))
    app.add_handler(CallbackQueryHandler(send_order_calendar_file, pattern=r"^admin_calendar_order_\d+$"))
    app.add_handler(CallbackQueryHandler(show_admin_order, pattern=r"^admin_order_\d+$"))
    app.add_handler(CallbackQueryHandler(show_admin_custom_order, pattern=r"^admin_custom_order_\d+$"))
    app.add_handler(CallbackQueryHandler(advance_order_status, pattern=r"^admin_next_status_\d+$"))
    app.add_handler(CallbackQueryHandler(advance_custom_order_status, pattern=r"^admin_next_custom_status_\d+$"))
    app.add_handler(CallbackQueryHandler(cancel_order, pattern=r"^admin_cancel_order_\d+$"))
    app.add_handler(CallbackQueryHandler(cancel_custom_order, pattern=r"^admin_cancel_custom_order_\d+$"))
    app.add_handler(CallbackQueryHandler(add_order_to_tasks, pattern=r"^admin_add_tasks_order_\d+$"))
    app.add_handler(CallbackQueryHandler(add_custom_order_to_tasks, pattern=r"^admin_add_tasks_custom_order_\d+$"))
    app.add_handler(CallbackQueryHandler(delete_order, pattern=r"^admin_delete_order_\d+$"))
    app.add_handler(CallbackQueryHandler(delete_custom_order, pattern=r"^admin_delete_custom_order_\d+$"))

    app.add_handler(CallbackQueryHandler(add_to_cart, pattern=r"^add_\d+$"))
    app.add_handler(CallbackQueryHandler(plus_item, pattern=r"^cart_plus_\d+$"))
    app.add_handler(CallbackQueryHandler(minus_item, pattern=r"^cart_minus_\d+$"))
    app.add_handler(CallbackQueryHandler(delete_item, pattern=r"^cart_del_\d+$"))

    app.add_handler(MessageHandler(filters.Regex(r"^🧁 (Каталог|Katalog|Catalog)$"), show_products))
    app.add_handler(MessageHandler(filters.Regex(r"^🛒 (Кошик|Корзина|Koszyk|Cart)$"), show_cart))
    app.add_handler(MessageHandler(filters.Regex(r"^📦 (Мої замовлення|Мои заказы|Moje zamówienia|My orders)$"), my_orders))
    app.add_handler(MessageHandler(filters.Regex(r"^❤️ (Обране|Избранное|Ulubione|Favorites)$"), show_favorites))
    app.add_handler(MessageHandler(filters.Regex(r"^📦 Активні замовлення$"), active_orders))
    app.add_handler(CommandHandler("reviews", show_reviews_admin))
    app.add_handler(MessageHandler(filters.Regex(r"^❓ FAQ$"), faq))
    app.add_handler(MessageHandler(filters.Regex(r"^📞 (Контакти|Контакты|Kontakt|Contacts)$"), contacts))

    app.add_error_handler(error_handler)
    return app


if __name__ == "__main__":
    application = build_app()
    print("Bot started")
    application.run_polling()
