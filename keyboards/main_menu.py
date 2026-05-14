from telegram import ReplyKeyboardMarkup

main_menu = ReplyKeyboardMarkup(
    [
        ["🍰 Каталог", "🛒 Кошик"],
        ["📦 Мої замовлення"],
        ["❓ FAQ", "📍 Контакти"]
    ],
    resize_keyboard=True
)
