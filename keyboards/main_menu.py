from telegram import ReplyKeyboardMarkup

main_menu = ReplyKeyboardMarkup(
    [
        ["🍰 Каталог", "🎂 Замовити"],
        ["❓ FAQ", "📍 Контакти"]
    ],
    resize_keyboard=True
)
