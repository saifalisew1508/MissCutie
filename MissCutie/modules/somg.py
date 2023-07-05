import os
import re
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaVideo,
    Message,
)
from pyrogram.errors import MessageNotModified

import youtube_dl

from MissCutie.utils.formatters import convert_bytes
from MissCutie.utils.inline.song import song_markup
from MissCutie.utils.platforms.Youtube import YouTubeAPI
from MissCutie import pbot as app


SONG_DOWNLOAD_DURATION = "180" # Set your desired value
SONG_DOWNLOAD_DURATION_LIMIT = "180" # Set your desired value

YouTube = YouTubeAPI()



@app.on_message(
    filters.command("yt")
    & filters.group
    & ~filters.edited
)
async def song_command_group(client, message: Message):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="↗️ Open Private Chat",
                    url=f"https://t.me/{app.username}?start=song",
                ),
            ]
        ]
    )
    await message.reply_text("You can download Music or Video from YouTube only in private chat. Please start me in private chat.", reply_markup=upl)


@app.on_message(
    filters.command("yt")
    & filters.private
    & ~filters.edited
)
async def song_command_private(client, message: Message):
    await message.delete()
    url = await YouTube.url(message)
    if url:
        if not await YouTube.exists(url):
            return await message.reply_text("Not a valid YouTube Link")
        mystic = await message.reply_text("🔄 Processing Query... Please Wait!")
        (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        ) = await YouTube.details(url)
        if str(duration_min) == "None":
            return await mystic.edit_text("Live Link Detected. I am not able to download live YouTube videos. ")
        if int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
            return await mystic.edit_text(
                "**Duration Limit Exceeded**\n\n**Allowed Duration: **{0} minute(s)\n**Received Duration:** {1} hour(s)".format(
                    SONG_DOWNLOAD_DURATION, duration_min
                )
            )
        buttons = song_markup(vidid)
        await mystic.delete()
        return await message.reply_photo(
            thumbnail,
            caption="**🔗Title:**- {0}\n\nSelect the type in which you want to download.".format(title),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        if len(message.command) < 2:
            return await message.reply_text("**Usage:**\n\n/yt [Music Name] or [YouTube Link]")
    mystic = await message.reply_text("🔄 Processing Query... Please Wait!")
    query = message.text.split(None, 1)[1]
    try:
        (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        ) = await YouTube.details(query)
    except:
        return await mystic.edit_text("Failed to Process Query!")
    if str(duration_min) == "None":
        return await mystic.edit_text("Live Link Detected. I am not able to download live YouTube videos. ")
    if int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
        return await mystic.edit_text(
            "**Duration Limit Exceeded**\n\n**Allowed Duration: **{0} minute(s)\n**Received Duration:** {1} hour(s)".format(
                SONG_DOWNLOAD_DURATION, duration_min
            )
        )
    buttons = song_markup(vidid)
    await mystic.delete()
    await message.reply_photo(
        thumbnail,
        caption="**🔗Title:**- {0}\n\nSelect the type in which you want to download.".format(title),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@app.on_callback_query(
    filters.regex(pattern=r"audio|video")
)
async def song_type_selection(client, callback_query):
    await callback_query.answer()
    if callback_query.matches[0].group(0) == "audio":
        await callback_query.edit_message_text("**Processing Request... Please Wait!**")
    else:
        await callback_query.edit_message_text("**Processing Request... Please Wait!**\n\n🌟 Made By @MissCutieOfficial 🌟")
    song_type = callback_query.matches[0].group(0)
    video_id = callback_query.matches[0].group(1)
    title = callback_query.matches[0].group(2)
    if song_type == "audio":
        ytdl_format_options = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": "%(id)s.mp3",
            "quiet": True,
            "logtostderr": False,
        }
        try:
            with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
                ydl.download(["https://www.youtube.com/watch?v=" + video_id])
        except Exception as e:
            return await callback_query.edit_message_text(str(e))
        f = open(video_id + ".mp3", "rb")
        await callback_query.edit_message_text("**Uploading...**")
        try:
            await callback_query.edit_message_media(
                media=InputMediaAudio(
                    media=f,
                    duration=duration_sec,
                    title=title,
                    performer=title,
                )
            )
        except MessageNotModified:
            return
        await callback_query.edit_message_caption(
            caption=f"**Title:** {title}\n**Duration:** {duration_min}:{duration_sec}\n**Size:** {convert_bytes(os.path.getsize(video_id + '.mp3'))}"
        )
        os.remove(video_id + ".mp3")
    else:
        await callback_query.edit_message_text("**Downloading Video...**")
        ytdl_format_options = {
            "format": "best",
            "outtmpl": "%(id)s.%(ext)s",
            "quiet": True,
            "logtostderr": False,
        }
        try:
            with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
                ydl.download(["https://www.youtube.com/watch?v=" + video_id])
        except Exception as e:
            return await callback_query.edit_message_text(str(e))
        f = video_id + ".mp4"
        await callback_query.edit_message_text("**Uploading Video...**")
        try:
            await callback_query.edit_message_media(
                media=InputMediaVideo(
                    media=f,
                    duration=duration_sec,
                    width=1280,
                    height=720,
                    supports_streaming=True,
                )
            )
        except MessageNotModified:
            return
        await callback_query.edit_message_caption(
            caption=f"**Title:** {title}\n**Duration:** {duration_min}:{duration_sec}\n**Size:** {convert_bytes(os.path.getsize(f))}"
        )
        os.remove(f)


@app.on_callback_query(
    filters.regex(pattern=r"song_back")
)
async def songs_back_helper(client, callback_query):
    await callback_query.answer()
    await callback_query.edit_message_text("**Processing Request... Please Wait!**")
    buttons = song_markup()
    await callback_query.edit_message_text("**Select the type in which you want to download.**", reply_markup=InlineKeyboardMarkup(buttons))

