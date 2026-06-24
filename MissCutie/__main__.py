"""
MissCutie – Entry point.
Run with:  python -m MissCutie
"""

import logging

from MissCutie import application

# Import all modules so their handlers get registered
import MissCutie.modules  # noqa: F401  (triggers __init__.py auto-loader)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("🌸 MissCutie is starting up...")
    application.run_polling(
        allowed_updates=[
            "message",
            "edited_message",
            "chat_member",
            "my_chat_member",
            "callback_query",
        ],
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
  
