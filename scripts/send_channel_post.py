"""
Send a Telegram channel post with a real inline button that opens the bot/Mini App flow.

Usage:
    python scripts/send_channel_post.py

Required .env variables:
    BOT_TOKEN=123456:ABC...
    CHANNEL_ID=@your_channel_username

Optional .env variables:
    CHANNEL_POST_BUTTON_TEXT=🧁 Відкрити меню
    CHANNEL_POST_URL=https://t.me/your_bot?start=menu

If CHANNEL_POST_URL is not provided, the script automatically uses:
    https://t.me/<bot_username>?start=menu
"""

import asyncio
import os
from html import escape

from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError


DEFAULT_POST_TEXT = (
    "🍰 <b>Хочеш замовити десерти?</b>\n\n"
    "Відкрий меню Murchik Cakes, обери десерти та оформи замовлення через наш бот."
)
DEFAULT_BUTTON_TEXT = "🧁 Відкрити меню"


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def main() -> None:
    load_dotenv()

    token = get_required_env("BOT_TOKEN")
    channel_id = get_required_env("CHANNEL_ID")

    post_text = os.getenv("CHANNEL_POST_TEXT", DEFAULT_POST_TEXT).strip() or DEFAULT_POST_TEXT
    button_text = os.getenv("CHANNEL_POST_BUTTON_TEXT", DEFAULT_BUTTON_TEXT).strip() or DEFAULT_BUTTON_TEXT

    bot = Bot(token=token)
    me = await bot.get_me()

    default_url = f"https://t.me/{me.username}?start=menu"
    button_url = os.getenv("CHANNEL_POST_URL", default_url).strip() or default_url

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(button_text, url=button_url)]]
    )

    try:
        message = await bot.send_message(
            chat_id=channel_id,
            text=post_text,
            parse_mode="HTML",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    except TelegramError as exc:
        raise RuntimeError(
            "Failed to send channel post. Check that the bot is an admin of the channel "
            "and has permission to publish messages."
        ) from exc

    print("✅ Channel post sent successfully")
    print(f"Bot: @{me.username}")
    print(f"Channel: {escape(str(channel_id))}")
    print(f"Message ID: {message.message_id}")
    print(f"Button URL: {button_url}")


if __name__ == "__main__":
    asyncio.run(main())
