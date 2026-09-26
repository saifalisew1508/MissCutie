"""Runtime configuration for MissCutie."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Settings needed to run the bot.

    Values come from environment variables so bot credentials never need to be
    committed.  ``TELEGRAM_BOT_TOKEN`` is required; the other setting is
    optional.
    """

    token: str
    drop_pending_updates: bool = True

    @classmethod
    def from_environment(cls) -> "Settings":
        """Load and validate settings from the process environment."""
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError(
                "TELEGRAM_BOT_TOKEN must be set before starting MissCutie."
            )

        drop_pending_updates = os.environ.get(
            "DROP_PENDING_UPDATES", "true"
        ).strip().lower()
        if drop_pending_updates not in {"true", "false"}:
            raise RuntimeError("DROP_PENDING_UPDATES must be either 'true' or 'false'.")

        return cls(token=token, drop_pending_updates=drop_pending_updates == "true")
