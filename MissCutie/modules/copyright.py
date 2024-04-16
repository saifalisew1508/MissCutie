from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import datetime
from MissCutie import application, OWNER_ID
from Database.mongodb.copyright import (
    enable_anticopyright,
    disable_anticopyright,
    is_anticopyright_enabled,
)

async def handle_message(update: Update, context: CallbackContext) -> None:
    message = update.message
    chat_id = message.chat_id
    anticopyright_enabled = is_anticopyright_enabled(chat_id)

    if anticopyright_enabled:
        if (
            message.edit_date
            or message.sticker
            or message.video
            and message.date < datetime.now().timestamp() - 120
        ):
            await message.delete()

async def set_anticopyright(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user = update.effective_user

    if len(args) > 0:
        s = args[0].lower()
        if s in ["yes", "on", "true"]:
            enable_anticopyright(chat.id)
            await message.reply_html(
                f"Anticopyright has been enabled in {html.escape(chat.title)}\nI will delete edited messages, stickers, and videos after 2 minutes"
            )
            log_message = (
                f"#ANTICOPYRIGHT\n"
                f"Enabled\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}"
            )
            return log_message
        elif s in ["off", "no", "false"]:
            disable_anticopyright(chat.id)
            await message.reply_html(
                f"Anticopyright has been disabled in {html.escape(chat.title)}\nI will no longer delete edited messages, stickers, and videos after 2 minutes"
            )
            log_message = (
                f"#ANTICOPYRIGHT\n"
                f"Disabled\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}"
            )
            return log_message
        else:
            await message.reply_text(f"Unrecognized arguments {s}")
            return
    await message.reply_html(
        f"Anticopyright setting is currently <b><i>{anticopyright_status(chat.id)}</i></b> in <code>{html.escape(chat.title)}</code>\n\n"
        "When this setting is on, I will delete edited messages, stickers, and videos after 2 minutes"
    )
    return

application.add_handler(CommandHandler("anticopyright", set_anticopyright))
application.add_handler(MessageHandler(Filters.all, handle_message))
