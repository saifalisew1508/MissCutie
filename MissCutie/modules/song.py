from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import youtube_dl
from MissCutie import pbot as app



def download_audio(url, quality):
    ydl_opts = {
        'format': f'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'outtmpl': '%(title)s.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        ydl.download([url])

    return video_title


def download_video(url, quality):
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
        'outtmpl': '%(title)s.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        ydl.download([url])

    return video_title


@app.on_message(filters.command("song", prefixes="/"))
async def handle_song_command(client, message):
    song_name = message.text.split(" ", 1)[1]
    chat_id = message.chat.id

    # Send a message asking for the user's choice (audio or video)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Audio", callback_data=f"audio|{song_name}"),
            InlineKeyboardButton("Video", callback_data=f"video|{song_name}")
        ]
    ])

    await app.send_message(chat_id, "Select your preferred option:", reply_markup=keyboard)


@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    query = callback_query.data
    chat_id = callback_query.message.chat.id

    if query.startswith("audio"):
        option, song_name = query.split("|")
        # Ask for the audio quality
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("High", callback_data=f"audio_quality|{song_name}|high"),
                InlineKeyboardButton("Medium", callback_data=f"audio_quality|{song_name}|medium"),
                InlineKeyboardButton("Low", callback_data=f"audio_quality|{song_name}|low")
            ]
        ])

        await app.edit_message_text(chat_id, callback_query.message.message_id, "Select audio quality:", reply_markup=keyboard)

    elif query.startswith("video"):
        option, song_name = query.split("|")
        # Ask for the video quality
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("HD", callback_data=f"video_quality|{song_name}|hd"),
                InlineKeyboardButton("SD", callback_data=f"video_quality|{song_name}|sd"),
                InlineKeyboardButton("Low", callback_data=f"video_quality|{song_name}|low")
            ]
        ])

        await app.edit_message_text(chat_id, callback_query.message.message_id, "Select video quality:", reply_markup=keyboard)

    elif query.startswith("audio_quality"):
        option, song_name, quality = query.split("|")
        url = f"https://www.youtube.com/results?search_query={song_name}"
        video_title = download_audio(url, quality)
        await app.send_audio(chat_id, audio=f"{video_title}.mp3", title=video_title)

    elif query.startswith("video_quality"):
        option, song_name, quality = query.split("|")
        url = f"https://www.youtube.com/results?search_query={song_name}"
        video_title = download_video(url, quality)
        await app.send_video(chat_id, video=f"{video_title}.mp4", caption=video_title)









__help__ = """
/song {name}, bot send You asked Song in That chat!
/video {name}, bot send You asked Yt video In That chat!
"""


__mod_name__ = "YouTube"
