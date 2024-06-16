import os
import requests
import YouTubeMusicAPI
from MissCutie import application
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        
        # Download the song
        song_data = requests.get(url)
        download_path = f"./download/{title}.mp3"
        
        with open(download_path, "wb") as file:
            file.write(song_data.content)
        
        # Send the downloaded audio file with the artwork as the thumbnail
        response_text = f"*{title}*\n[Watch on YouTube Music]({url})\n\n"
        response_text += f"Author: [{author_name}]({author_url})"
        
        await update.message.reply_audio(
            audio=open(download_path, 'rb'),
            title=title,
            caption=response_text,
            thumb=artwork,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text('No Result Found')


application.add_handler(CommandHandler('song', search))
