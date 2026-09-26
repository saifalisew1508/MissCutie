"""Telegram update handlers registered by :mod:`MissCutie.application`."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome a user who invokes ``/start``."""
    del context
    if update.effective_message is None:
        return

    await update.effective_message.reply_text(
        "Hi! I’m MissCutie. Use /help to see what I can do."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the currently available commands."""
    del context
    if update.effective_message is None:
        return

    await update.effective_message.reply_text(
        "<b>Available commands</b>\n"
        "/start — introduce the bot\n"
        "/help — show this message",
        parse_mode=ParseMode.HTML,
    )


async def log_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log unhandled handler exceptions without leaking them to chat users."""
    logger.error("Unhandled exception while processing update %r", update, exc_info=context.error)
