# MissCutie

MissCutie is a small Telegram bot rewritten for the modern asynchronous
[`python-telegram-bot`](https://docs.python-telegram-bot.org/) API (v22).

## Requirements

* Python 3.10 or newer
* A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
export TELEGRAM_BOT_TOKEN='your-token'
python -m MissCutie
```

By default the bot discards updates that accumulated while it was offline. Set
`DROP_PENDING_UPDATES=false` to process them instead.

## Commands

* `/start` — introduces the bot.
* `/help` — lists available commands.

## Development

```bash
python -m pytest
```
