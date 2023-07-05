import os
import sys
import re

import yt_dlp
from pykeyboard import InlineKeyboard
from pyrogram import filters
from pyrogram.types import (InlineKeyboardButton,
                            InlineKeyboardMarkup,
                            InputMediaAudio,
                            ChatAction,
                            InputMediaVideo,
                            Message)

from MissCutie import pbot as app, BOT_USERNAME
from MissCutie.utils.formatters import convert_bytes
from MissCutie.utils.inline.song import song_markup
from MissCutie.utils.youtube import YouTubeAPI


SONG_DOWNLOAD_DURATION = 360

def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60**i
        for i, x in enumerate(reversed(stringt.split(":")))
    )
  
SONG_DOWNLOAD_DURATION_LIMIT = int(
    time_to_seconds(f"{SONG_DOWNLOAD_DURATION}:00")
)

YouTube = YouTubeAPI()

@app.on_message(
    filters.command("yt")
    & filters.group
)
async def song_commad_group(client, message: Message):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="↗️ Open Private Chat",
                    url=f"https://t.me/{BOT_USERNAME}?start=song",
                ),
            ]
        ]
    )
    await message.reply_text("You can download Music or Video from YouTube only in private chat. Please start me in private chat.", reply_markup=upl)


# Song Module


@app.on_message(
    filters.command("yt")
    & filters.private
)
async def song_commad_private(client, message: Message):
    await message.delete()
    url = await YouTube.url(message)
    if url:
        if not await YouTube.exists(url):
            return await message.reply_text("Not a valid Youtube Link")
        mystic = await message.reply_text("🔄 Processing Query... Please Wait!")
        (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        ) = await YouTube.details(url)
        if str(duration_min) == "None":
            return await mystic.edit_text("Live Link Detected. I am not able to download live youtube videos. ")
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
            return await message.reply_text("**Usage:**\n\n/song [Music Name] or [Youtube Link]")
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
        return await mystic.edit_text("Live Link Detected. I am not able to download live youtube videos. ")
    if int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
        return await mystic.edit_text(
            "**Duration Limit Exceeded**\n\n**Allowed Duration: **{0} minute(s)\n**Received Duration:** {1} hour(s)".format(SONG_DOWNLOAD_DURATION, duration_min)
        )
    buttons = song_markup(vidid)
    await mystic.delete()
    return await message.reply_photo(
        thumbnail,
        caption="**🔗Title:**- {0}\n\nSelect the type in which you want to download.".format(title),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@app.on_callback_query(
    filters.regex(pattern=r"song_back")
)
async def songs_back_helper(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    stype, vidid = callback_request.split("|")
    buttons = song_markup(vidid)
    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(
    filters.regex(pattern=r"song_helper")
)
async def song_helper_cb(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    stype, vidid = callback_request.split("|")
    try:
        await CallbackQuery.answer("Getting Formats.. \n\nPlease Wait..", show_alert=True)
    except:
        pass
    if stype == "audio":
        try:
            formats_available, link = await YouTube.formats(
                vidid, True
            )
        except:
            return await CallbackQuery.edit_message_text("Failed to get available formats for the video. Please try any other track.")
        keyboard = InlineKeyboard()
        done = []
        for x in formats_available:
            check = x["format"]
            if "audio" in check:
                if x["filesize"] is None:
                    continue
                form = x["format_note"].title()
                if form not in done:
                    done.append(form)
                else:
                    continue
                sz = convert_bytes(x["filesize"])
                fom = x["format_id"]
                keyboard.row(
                    InlineKeyboardButton(
                        text=f"{form} Quality Audio = {sz}",
                        callback_data=f"song_download {stype}|{fom}|{vidid}",
                    ),
                )
    else:
        try:
            formats_available, link = await YouTube.formats(
                vidid, True
            )
        except Exception as e:
            print(e)
            return await CallbackQuery.edit_message_text("Failed to get available formats for the video. Please try any other track.")
        keyboard = InlineKeyboard()
        # AVC Formats Only [ YUKKI MUSIC BOT ]
        done = [160, 133, 134, 135, 136, 137, 298, 299, 264, 304, 266]
        for x in formats_available:
            check = x["format"]
            if x["filesize"] is None:
                continue
            if int(x["format_id"]) not in done:
                continue
            sz = convert_bytes(x["filesize"])
            ap = check.split("-")[1]
            to = f"{ap} = {sz}"
            keyboard.row(
                InlineKeyboardButton(
                    text=to,
                    callback_data=f"song_download {stype}|{x['format_id']}|{vidid}",
                )
            )

    keyboard.row(
        InlineKeyboardButton(
            text="⬅ Back",
            callback_data=f"song_back {stype}|{vidid}",
        ),
        InlineKeyboardButton(text="🗑 Close", callback_data="close"),
    )
    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=keyboard
    )


# Downloading Songs Here




# ...

@app.on_callback_query(filters.regex(pattern=r"song_download"))
async def song_download_cb(client, CallbackQuery):
    try:
        await CallbackQuery.answer("Downloading")
    except:
        pass
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    stype, format_id, vidid = callback_request.split("|")
    mystic = await CallbackQuery.edit_message_text("Download Started\n\nDownloading speed could be slow. Please hold on..")
    yturl = f"https://www.youtube.com/watch?v={vidid}"
    with yt_dlp.YoutubeDL({"quiet": True}) as ytdl:
        x = ytdl.extract_info(yturl, download=False)
    title = (x["title"]).title()
    title = re.sub("\W+", " ", title)
    thumb_image_path = await CallbackQuery.message.download()
    if stype == "video":
        thumb_image_path = await CallbackQuery.message.download()
        width = CallbackQuery.message.photo.width
        height = CallbackQuery.message.photo.height
        try:
            file_path = await YouTube.download(
                yturl,
                mystic,
                songvideo=True,
                format_id=format_id,
                title=title,
            )
        except Exception as e:
            return await mystic.edit_text("Failed to download song from Youtube-DL\n\n**Reason:** {0}".format(e))
        duration = x["duration"]
        med = InputMediaVideo(
            media=file_path,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb_image_path,
            caption=title,
            supports_streaming=True,
        )
        await mystic.edit_text("Uploading Started\n\nUploading speed could be slow. Please hold on..")
        await app.send_chat_action(
            chat_id=CallbackQuery.message.chat.id,
            action=ChatAction.UPLOAD_VIDEO,
        )
        try:
            await CallbackQuery.edit_message_media(media=med)
        except Exception as e:
            print(e)
            return await mystic.edit_text("Failed to upload on Telegram from servers.")
        os.remove(file_path)
    elif stype == "audio":
        try:
            filename = await YouTube.download(
                yturl,
                mystic,
                songaudio=True,
                format_id=format_id,
                title=title,
            )
        except Exception as e:
            return await mystic.edit_text("Failed to download song from Youtube-DL\n\n**Reason:** {0}".format(e))
        med = InputMediaAudio(
            media=filename,
            caption=title,
            thumb=thumb_image_path,
            title=title,
            performer=x["uploader"],
        )
        await mystic.edit_text("Uploading Started\n\nUploading speed could be slow. Please hold on..")
        await app.send_chat_action(
            chat_id=CallbackQuery.message.chat.id,
            action=ChatAction.UPLOAD_AUDIO,
        )
        try:
            await CallbackQuery.edit_message_media(media=med)
        except Exception as e:
            print(e)
            return await mystic.edit_text("Failed to upload on Telegram from servers.")
        os.remove(filename)
    os.remove(thumb_image_path)
