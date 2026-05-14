from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from database.temp_storage import PRODUCTS


PHOTO, NAME = range(2)
