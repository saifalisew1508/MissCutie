"""Tests for configuration that do not require Telegram network access."""

from __future__ import annotations

import pytest

from MissCutie.config import Settings


def test_settings_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "a-token")
    monkeypatch.setenv("DROP_PENDING_UPDATES", "false")

    settings = Settings.from_environment()

    assert settings.token == "a-token"
    assert settings.drop_pending_updates is False


def test_settings_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
        Settings.from_environment()
