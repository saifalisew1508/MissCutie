import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, filters, CallbackQueryHandler
from telegram.helpers import mention_html

from MissCutie import BOT_NAME, BOT_USERNAME, application


async def handwrite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message

    if not message.reply_to_message:
        text = message.text.split(None, 1)[1]
    else:
        text = message.reply_to_message.text

    m = await update.effective_message.reply_text("Please wait writing your text to notebook...")
    API = f"https://notes.apinepdev.workers.dev/?text={text}"
    NOTE = requests.get(API).url

    caption = f"""
Successfully written text 💘

✨ **Written By :** [{BOT_NAME}](https://t.me/{BOT_USERNAME})
🥀 **Requested By :** {mention_html(message.from_user.id, message.from_user.first_name)}
🔗 **Link :** `{NOTE}`
"""

    await m.delete()
    await update.effective_message.reply_photo(
        photo=NOTE,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("• Telegraph •", url=NOTE)]]
        ),
        parse_mode=ParseMode.MARKDOWN,
    )

application.add_handler(CommandHandler("write", handwrite))
