from telegram import ReplyKeyboardMarkup

main_menu = ReplyKeyboardMarkup(
    [
        ["🍰 Каталог", "🎂 Замовити"],
        ["📦 Мої замовлення"],
        ["❓ FAQ", "📍 Контакти"]
    ],
    resize_keyboard=True
)
