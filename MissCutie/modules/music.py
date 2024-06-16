from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import YouTubeMusicAPI



def search(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('Please provide a search query.')
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
        
        update.message.reply_photo(photo=artwork, caption=response_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        update.message.reply_text('No Result Found')
