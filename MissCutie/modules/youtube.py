"""

import os
import requests
import wget
import yt_dlp
from pyrogram import filters
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL

from MissCutie import pbot as bot

# Constants
YDL_OPTS = {
    "format": "best",
    "keepvideo": True,
    "prefer_ffmpeg": False,
    "geo_bypass": True,
    "outtmpl": "%(title)s.%(ext)s",
    "quite": True,
}


@bot.on_message(filters.command("video"))
async def vsong(client, message):
    query = " ".join(message.command[1:])
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        message.from_user.mention
    except Exception as e:
        print(e)
        return

    try:
        msg = await message.reply("Video in progress 💫")
        with YoutubeDL(YDL_OPTS) as ytdl:
            ytdl_data = ytdl.extract_info(link, download=True)
            file_name = ytdl.prepare_filename(ytdl_data)
    except Exception as e:
        return await msg.edit(f"🚫 Error: {e}")

    preview = wget.download(thumbnail)
    await msg.edit("Process complete...\nNow uploading...")
    title = ytdl_data["title"]
    await message.reply_video(
        file_name,
        duration=int(ytdl_data["duration"]),
        thumb=preview,
        caption=f"{title}\nRequested by {message.from_user.mention}",
    )

    await msg.delete()
    try:
        os.remove(file_name)
    except Exception as e:
        print(e)


@bot.on_message(filters.command("song"))
def download_song(_, message):
    query = " ".join(message.command[1:])
    print(query)
    m = message.reply("🔄 Searching....")
    ydl_ops = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]

    except Exception as e:
        m.edit(
            "⚠️ No results were found. Make sure you typed the information correctly"
        )
        print(str(e))
        return

    m.edit("📥 Downloading...")
    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(float(dur_arr[i])) * secmul
            secmul *= 60
        m.edit("📤 Uploading...")

        message.reply_audio(
            audio_file,
            thumb=thumb_name,
            title=title,
            caption=f"{title}\nRequested by {message.from_user.mention}",
            duration=dur,
        )
        m.delete()
    except Exception as e:
        m.edit(" - An error occurred!")
        print(e)

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

"""
