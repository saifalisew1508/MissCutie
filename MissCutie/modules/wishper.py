from datetime import datetime
from uuid import uuid4

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes, InlineQueryHandler, CallbackQueryHandler, ChosenInlineResultHandler
from telegram.constants import ParseMode

from MissCutie import LOGGER, application
from MissCutie.modules.users import get_user_id
import MissCutie.modules.sql.whisper_sql as sql

class Whisper():
    receiver = 0
    message = 0

    def __init__(self, receiver, message):
        self.message = message,
        self.receiver = receiver

    def to_string(self):
        return str(self.receiver.id) + str(self.message)


LIST = []


async def chosen_inline_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chosen_inline_result
    query = result.query
    q = query.split(" ")
    username = q[-1]
    receiver_id = get_user_id(username)
    sender_id = update.effective_user.id
    text = ""
    for element in q:
        if element is not username:
            text = text + " " + element
    sql.add_whisper(sender_id, receiver_id, text, sql.get_whispers(context.bot.id))
    sql.increase_whisper_ids(context.bot.id)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(query)
    id = query.data.replace("whisper_", "")
    whisper_message = sql.get_message(int(id))
    sender = whisper_message.sender_id
    receiver = whisper_message.receiver_id
    message = whisper_message.message
    if update.effective_user.id not in (sender, receiver):
        await context.bot.answer_callback_query(update.callback_query.id,
                                          "You are not permitted to read this message.",
                                          show_alert=False)
        return
    await context.bot.answer_callback_query(update.callback_query.id, message, show_alert=True)


async def process_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.inline_query.query
    results = []
    q = query.split(" ")
    username = q[-1]
    if not username.startswith("@"):
        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title="This does not work.",
            description="You need to specify the user you want to message. If this person does not have one, you can not whisper to them.",
            input_message_content=InputTextMessageContent("Write targets @username at the end of your message in order to send a message.", ParseMode.MARKDOWN)
        ))
    else:
        for element in q:
            if element is not username:
                try:
                    current_time = datetime.now()
                    receiver = context.bot.get_chat(get_user_id(username))
                    name = receiver.first_name
                    title = "A whisper message to " + name
                    print("Title: " + title)
                    results.append(InlineQueryResultArticle(
                        id=uuid4(),
                        title=title,
                        description="Only they can open it.",
                        input_message_content=InputTextMessageContent(f"🔒 A whisper message to @{receiver.username}, Only they can open it."),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                            text="show message",
                            callback_data="whisper_" + str(sql.get_whispers(context.bot.id)))
                        ]])
                    ))


                except BadRequest as excp:
                    if excp.message == 'Chat not found':
                        pass
                    else:
                        LOGGER.exception("Error extracting user ID")
    await update.inline_query.answer(results)


QUERY_HANDLER = InlineQueryHandler(process_inline_query, block=False)
BUTTON_HANDLER = CallbackQueryHandler(button, pattern=r"whisper", block=False)
INLINE_RESULT_HANDLER = ChosenInlineResultHandler(chosen_inline_button, block=False)

application.add_handler(QUERY_HANDLER)
application.add_handler(BUTTON_HANDLER)
application.add_handler(INLINE_RESULT_HANDLER)
