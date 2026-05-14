from telegram.error import BadRequest, Forbidden


async def delete_callback_message(query):
    """Delete the message that contained an inline button, if Telegram allows it."""
    try:
        if query and query.message:
            await query.message.delete()
    except (BadRequest, Forbidden):
        # Message may already be deleted, too old, or not deletable.
        pass
