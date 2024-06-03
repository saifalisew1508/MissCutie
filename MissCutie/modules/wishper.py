import shortuuid
from pymongo import MongoClient
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.ext import CallbackQueryHandler, ContextTypes, InlineQueryHandler

from MissCutie import DB_NAME, MONGO_DB_URI, application

# Initialize MongoDB client
client = MongoClient(MONGO_DB_URI)
db = client[DB_NAME]
collection = db["whispers"]

# Whispers Class
class Whispers:
    @staticmethod
    def add_whisper(WhisperId, WhisperData):
        whisper = {"WhisperId": WhisperId, "whisperData": WhisperData}
        collection.insert_one(whisper)

    @staticmethod
    def del_whisper(WhisperId):
        collection.delete_one({"WhisperId": WhisperId})

    @staticmethod
    def get_whisper(WhisperId):
        whisper = collection.find_one({"WhisperId": WhisperId})
        return whisper["whisperData"] if whisper else None

# Inline query handler
async def mainwhisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query
    if not query.query:
        return await query.answer(
            [],
            switch_pm_text="Provide a message and user ID!",
            switch_pm_parameter="ghelp_whisper",
        )

    user_id, message = parse_user_message(query.query)
    if not user_id.isdigit() or len(message) > 200:
        return

    whisperData = {
        "user": query.from_user.id,
        "withuser": int(user_id),
        "type": "inline",
        "message": message,
    }
    whisperId = shortuuid.uuid()

    # Add the whisper to the database
    Whispers.add_whisper(whisperId, whisperData)

    answers = [
        InlineQueryResultArticle(
            id=whisperId,
            title=f"👤 Send a whisper message to {user_id}!",
            description="Only they can see it!",
            input_message_content=InputTextMessageContent(
                f"🔐 A Whisper Message For User ID {user_id}\nOnly they can see it!"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📩 Show Message 📩",
                            callback_data=f"whisper_{whisperId}",
                        )
                    ]
                ]
            ),
        )
    ]

    await context.bot.answer_inline_query(query.id, answers)

# Callback query handler
async def showWhisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_query = update.callback_query
    whisperId = callback_query.data.split("_")[-1]
    whisper = Whispers.get_whisper(whisperId)

    if not whisper:
        await context.bot.answer_callback_query(
            callback_query.id, "This whisper is not valid anymore!"
        )
        return

    from_user_id = callback_query.from_user.id

    if from_user_id == whisper["user"] or from_user_id == whisper["withuser"]:
        await context.bot.answer_callback_query(
            callback_query.id, whisper["message"], show_alert=True
        )
    else:
        await context.bot.answer_callback_query(
            callback_query.id, "Not your Whisper!", show_alert=True
        )

# Function to parse user message
def parse_user_message(query_text):
    parts = query_text.split(" ", 1)
    if len(parts) < 2:
        return "", ""
    user_id = parts[0]
    message = parts[1]
    return user_id, message

application.add_handler(InlineQueryHandler(mainwhisper, block=False))
application.add_handler(CallbackQueryHandler(showWhisper, pattern="^whisper_", block=False))

__mod_name__ = "Whispers"
