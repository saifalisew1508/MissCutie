from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatType
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, CommandHandler, filters

from MissCutie import application
from MissCutie.modules.helper_funcs.alternate import typing_action, send_message
from Database.mongodb import dbname

import aiohttp

chatdb = dbname.chatbot
chatbot_status = {}

__mod_name__ = "ChatBot"
__help__ = """
• This is an AI-powered ChatBot using GPT API.

Commands:
‣ /chatbot [on|off] - Enable or disable chatbot in group or PM.
Only admins can toggle this in groups.

Chat triggers:
‣ Reply to bot
‣ Tag bot
‣ Send greeting words like "hello", "hi", etc.
"""

__command_list__ = ["chatbot"]


async def is_chatbot_on(chat_id: int) -> bool:
    mode = chatbot_status.get(chat_id)
    if mode is None:
        chat = await chatdb.find_one({"chat_id": chat_id})
        chatbot_status[chat_id] = False if chat else True
        return chatbot_status[chat_id]
    return mode


async def chatbot_on(chat_id: int):
    chatbot_status[chat_id] = True
    await chatdb.delete_one({"chat_id": chat_id})


async def chatbot_off(chat_id: int):
    chatbot_status[chat_id] = False
    await chatdb.insert_one({"chat_id": chat_id})


@typing_action
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type != ChatType.PRIVATE:
        member = await chat.get_member(user.id)
        if not member.can_change_info and not member.status == "creator":
            return await send_message(update.effective_message, "Only admins can change chatbot settings.")

    keyboard = [
        [
            InlineKeyboardButton("Enable", callback_data=f"chatbot_enable_{chat.id}"),
            InlineKeyboardButton("Disable", callback_data=f"chatbot_disable_{chat.id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(update.effective_message, "Choose chatbot mode:", reply_markup=reply_markup)


async def chatbot_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    action, mode, chat_id = data.split("_")
    chat_id = int(chat_id)

    if action != "chatbot":
        return

    if mode == "enable":
        await chatbot_on(chat_id)
        await query.edit_message_text("ChatBot Enabled.")
    else:
        await chatbot_off(chat_id)
        await query.edit_message_text("ChatBot Disabled.")


@typing_action
async def chatgpt_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not await is_chatbot_on(chat.id):
        return

    text = message.text or message.caption or ""
    if not (
        message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id
        or context.bot.username.lower() in text.lower()
        or text.lower() in ["hi", "hello", "hey", "hlo"]
    ):
        return

    # Send request to GPT API
    api_url = f"https://gptchatly.com/felch-response?question={text}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json={
                "past_conversations": [
                    {"role": "system", "content": "Hi! I'm ChatGPT. Let's chat."},
                    {"role": "user", "content": text}
                ]
            }) as resp:
                data = await resp.json()
                reply = data.get("chatGPTResponse", "No response from GPT.")
    except Exception:
        reply = "Sorry, I couldn’t connect to the GPT server."

    await send_message(message, reply)


def register_handlers():
    application.add_handler(CommandHandler("chatbot", chatbot_toggle))
    application.add_handler(CallbackQueryHandler(chatbot_button, pattern=r"chatbot_(enable|disable)_\d+"))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chatgpt_reply))


register_handlers()