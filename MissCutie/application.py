"""Application factory and handler registration for the current PTB API."""

from __future__ import annotations

from telegram.ext import Application, ApplicationBuilder, CommandHandler

from MissCutie.config import Settings
from MissCutie.handlers import help_command, log_error, start


def create_application(settings: Settings) -> Application:
    """Build a fully registered :class:`telegram.ext.Application` instance.

    The factory follows the asynchronous ``ApplicationBuilder`` API introduced
    by python-telegram-bot v20 and retained by the current v22 release.
    """
    application = ApplicationBuilder().token(settings.token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(log_error)
    return application
