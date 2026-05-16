import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BOT_USERNAME = os.getenv("BOT_USERNAME")

async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")
    if not CHANNEL_ID:
        raise RuntimeError("CHANNEL_ID is not set")
    if not BOT_USERNAME:
        raise RuntimeError("BOT_USERNAME is not set")

    bot = Bot(token=TOKEN)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🧁 Відкрити меню",
                url=f"https://t.me/{BOT_USERNAME}?start=menu"
            )
        ]
    ])

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=(
            "🍰 Хочеш замовити десерти?\n\n"
            "Відкрий меню Murchik Cakes, обери десерти "
            "та оформи замовлення через наш бот."
        ),
        reply_markup=keyboard
    )

asyncio.run(main())
