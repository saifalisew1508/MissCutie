import asyncio
import time
import os
import json
import wget
import textwrap

from tswift import Song
from MissCutie import application
from MissCutie.modules.disable import DisableAbleCommandHandler
from telegram import Update
from telegram import Bot, Update, Message, Chat
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

try:
    from youtubesearchpython import SearchVideos
    from yt_dlp import YoutubeDL

except:
    os.system("pip install pip install youtube-search-python")
    os.system("pip install pip install yt_dlp")
    from youtubesearchpython import SearchVideos
    from yt_dlp import YoutubeDL


async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = message.text.split(" ", 1)

    if len(args) == 1:
        await message.reply_text('Provide Song Name also like `/song on my way`!')
        return
    urlissed = args[1]

    pablo = await bot.send_message(
        chat.id, textwrap.dedent(
            f"`Getting {urlissed} From Youtube Servers. Please Wait.`")
    )

    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    mio[0]["duration"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    thums = mio[0]["channel"]
    url = mo
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    sedlyf = wget.download(kekme)
    opts = {
        "format": "bestaudio",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "720",
            }
        ],
        "outtmpl": "%(id)s.mp3",
        "quiet": True,
        "logtostderr": False,
    }

    try:
        is_downloading = True
        with YoutubeDL(opts) as ytdl:
            infoo = await asyncio.to_thread(ytdl.extract_info, url, False)
            duration = round(infoo["duration"] / 60)

            if duration > 10:
                await pablo.edit_text(
                    f"❌ Videos longer than 10 minute(s) aren't allowed, the provided video is {duration} minute(s)"
                )
                is_downloading = False
                return
            ytdl_data = await asyncio.to_thread(ytdl.extract_info, url, download=True)

    except Exception as e:
        await pablo.edit_text(f"*Failed To Download* \n*Error :* `{str(e)}`")
        is_downloading = False
        return
    c_time = time.time()
    capy = textwrap.dedent(
        f"*Song Name :* `{thum}` \n*Requested For :* `{urlissed}` \n*Channel :* `{thums}` \n*Link :* `{mo}`")
    file_stark = f"{ytdl_data['id']}.mp3"
    await bot.send_audio(
        chat.id,
        audio=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        title=str(ytdl_data["title"]),
        performer=str(ytdl_data["uploader"]),
        thumb=sedlyf,
        caption=capy,
        parse_mode=ParseMode.MARKDOWN,

    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)


async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = message.text.split(" ", 1)

    if len(args) == 1:
        await message.reply_text('Provide video Name also like `/video on my way`!')
        return
    urlissed = args[1]

    pablo = await bot.send_message(
        message.chat.id, textwrap.dedent(
            f"`Getting {urlissed} From Youtube Servers. Please Wait.`")
    )
    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    thums = mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }

    try:
        is_downloading = True
        with YoutubeDL(opts) as ytdl:
            infoo = await asyncio.to_thread(ytdl.extract_info, url, False)
            duration = round(infoo["duration"] / 60)

            if duration > 10:
                await pablo.edit_text(
                    f"❌ Videos longer than 10 minute(s) aren't allowed, the provided video is {duration} minute(s)"
                )
                is_downloading = False
                return
            ytdl_data = await asyncio.to_thread(ytdl.extract_info, url, download=True)

    except Exception as e:
        await pablo.edit_text(f"*Failed To Download* \n*Error :* `{str(e)}`")
        is_downloading = False
        return

    c_time = time.time()
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = textwrap.dedent(
        f"*Video Name ➠* `{thum}` \n*Requested For :* `{urlissed}` \n*Channel :* `{thums}` \n*Link :* `{mo}`")
    await bot.send_video(
        chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        # file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        parse_mode=ParseMode.MARKDOWN,
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)



__mod_name__ = "Music"


SONG_HANDLER = DisableAbleCommandHandler("song", music, block=False)
VIDEO_HANDLER = DisableAbleCommandHandler("video", video, block=False)

application.add_handler(SONG_HANDLER)
application.add_handler(VIDEO_HANDLER)
