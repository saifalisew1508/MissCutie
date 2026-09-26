"""MissCutie, a Telegram bot built with python-telegram-bot.

The package deliberately does not construct an application at import time.  This
makes importing it safe for tools and tests, and keeps configuration validation
at the executable boundary.
"""

from MissCutie.config import Settings

__all__ = ("Settings", "create_application")


def __getattr__(name: str):
    """Import PTB-dependent application code only when it is requested."""
    if name == "create_application":
        from MissCutie.application import create_application

        return create_application
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
