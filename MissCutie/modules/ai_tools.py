import html
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatType, ParseMode, ChatMemberStatus
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)

from MissCutie import application
from MissCutie.modules.helper_funcs.chat_status import check_admin
from Database.mongodb.chatbot_db import is_chatbot_enabled, enable_chatbot, disable_chatbot


API_URL = "https://gptchatly.com/felch-response?question="

# Enable/Disable Command
@check_admin(is_both=True, permission="can_change_info")
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    args = context.args
    user = update.effective_user

    if not args:
        keyboard = [
            [InlineKeyboardButton("Enable ChatBot", callback_data="chatbot_enable"),
             InlineKeyboardButton("Disable ChatBot", callback_data="chatbot_disable")]
        ]
        await update.effective_message.reply_html(
            f"ChatBot is currently <b>{'Enabled' if is_chatbot_enabled(chat.id) else 'Disabled'}</b> in <code>{html.escape(chat.title or 'Private Chat')}</code>",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    status = args[0].lower()
    if status in ["on", "enable", "yes"]:
        enable_chatbot(chat.id)
        await update.effective_message.reply_text("ChatBot enabled in this chat.")
    elif status in ["off", "disable", "no"]:
        disable_chatbot(chat.id)
        await update.effective_message.reply_text("ChatBot disabled in this chat.")
    else:
        await update.effective_message.reply_text("Use: /chatbot on | off")


# Callback for button toggle
async def chatbot_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat

    member = await chat.get_member(user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await query.answer("Only admins can change chatbot status.", show_alert=True)
        return

    if query.data == "chatbot_enable":
        enable_chatbot(chat.id)
        await query.edit_message_text("ChatBot enabled in this chat.")
    elif query.data == "chatbot_disable":
        disable_chatbot(chat.id)
        await query.edit_message_text("ChatBot disabled in this chat.")


# Main Chatbot Handler
async def chatbot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    # Check if chatbot is enabled
    if not is_chatbot_enabled(chat.id):
        return

    # Trigger conditions
    if (
        message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id
    ) or (
        context.bot.username.lower() in (message.text or "").lower()
    ) or (
        any(word in message.text.lower() for word in ["hi", "hello", "hey", "who are you", "what can you do"])
    ):
        question = message.text.strip()

        try:
            response = requests.get(API_URL + question)
            data = response.json()
            answer = data.get("answer", "I couldn't get a proper response right now.")
        except Exception:
            answer = "Sorry, I'm having trouble connecting to my brain right now."

        await message.reply_text(answer, parse_mode=ParseMode.HTML)


# Help and module meta
__mod_name__ = "ChatBot"
__help__ = """
➠ This module adds a GPT-powered ChatBot in groups or private chats using an external API.

➠ Only Admins can enable/disable in groups.

*Commands:*
» /chatbot - View or toggle ChatBot
» /chatbot on - Enable in chat
» /chatbot off - Disable in chat
"""

__command_list__ = ["chatbot"]

# Register handlers
application.add_handler(CommandHandler("chatbot", chatbot_toggle, block=False))
application.add_handler(CallbackQueryHandler(chatbot_cb, pattern="chatbot_enable|chatbot_disable"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_handler))