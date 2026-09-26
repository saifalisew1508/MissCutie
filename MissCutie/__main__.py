"""Run MissCutie with ``python -m MissCutie``."""

from __future__ import annotations

import logging

from telegram import Update

from MissCutie.application import create_application
from MissCutie.config import Settings


def configure_logging() -> None:
    """Configure the process-wide logging used by the bot and its HTTP client."""
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    """Create the application from the environment and start long polling."""
    configure_logging()
    settings = Settings.from_environment()
    application = create_application(settings)
    logging.getLogger(__name__).info("MissCutie is starting up")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=settings.drop_pending_updates,
    )


if __name__ == "__main__":
    main()
