from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
from MissCutie import application, OWNER_ID
from Database.mongodb.copyright import enable_anticopyright, disable_anticopyright, is_anticopyright_enabled

# Define the callback function to handle messages
async def message_handler(update: Update, context: CallbackContext) -> None:
    message = update.message
    chat_id = message.chat_id

    # Check if the chat has enabled anticopyright
    anticopyright_enabled = is_anticopyright_enabled(chat_id)

    if anticopyright_enabled:
        # Check if the message is edited or contains stickers or videos
        if (message.edit_date or message.sticker or message.video) and message.date < time.time() - 120:
            message.delete()

# Define the command handler to enable anticopyright
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
                "Anticopyright has been enabled in {}\nI will delete edited messages, stickers, and videos after 2 minutes".format(
                    html.escape(chat.title)))
            log_message = (
                f"#ANTICOPYRIGHT\n"
                f"Enabled\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}"
            )
            return log_message

        elif s in ["off", "no", "false"]:
            disable_anticopyright(chat.id)
            await message.reply_html(
                "Anticopyright has been disabled in {}\nI will no longer delete edited messages, stickers, and videos after 2 minutes".format(
                    html.escape(chat.title)))
            log_message = (
                f"#ANTICOPYRIGHT\n"
                f"Disabled\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}"
            )
            return log_message

        else:
            await message.reply_text("Unrecognized arguments {}".format(s))
            return

    await message.reply_html(
        "Anticopyright setting is currently <b><i>{}</i></b> in <code>{}</code>\n\n"
        "When this setting is on, I will delete edited messages, stickers, and videos after 2 minutes".format(
            anticopyright_status(chat.id), html.escape(chat.title)))
    return



# Add handlers
application.add_handler(CommandHandler('anticopyright, set_anticopyright))
application.add_handler(MessageHandler(Filters.all, message_handler))



