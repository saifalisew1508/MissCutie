import YouTubeMusicAPI
from MissCutie import application
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)



async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text('Please provide a search query.')
        return
    
    result = YouTubeMusicAPI.search(query)
    
    if result:
        title = result.get("title")
        url = result.get("url")
        artwork = result.get("artwork")
        author_name = result.get("author", {}).get("name")
        author_url = result.get("author", {}).get("url")
        
        response_text = f"*{title}*\n[Watch on YouTube Music]({url})\n\n"
        response_text += f"Author: [{author_name}]({author_url})"
        
        keyboard = [
            [InlineKeyboardButton("Watch on YouTube Music", url=url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_photo(photo=artwork, caption=response_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text('No Result Found')


application.add_handler(CommandHandler('song', search))
