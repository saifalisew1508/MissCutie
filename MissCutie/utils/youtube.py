import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.types import Message
from youtubesearchpython import VideosSearch

from MissCutie.utils.formatters import time_to_seconds


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in errorz.decode("utf-8").lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == "url":
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == "text_link":
                        return entity.url
        return None if offset in (None,) else text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration_min = result["duration"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return duration_min, duration_sec

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        cmd = f'yt-dlp -g -f "bestvideo+bestaudio/best" --no-playlist {link}'
        return await shell_cmd(cmd)

    async def playlist(self, link: str):
        cmd = f'yt-dlp -j --flat-playlist {link}'
        res = await shell_cmd(cmd)
        playlist_items = []
        if res:
            data = res.split("\n")
            for line in data:
                try:
                    line = line.replace("'", '"')
                    data_ = json.loads(line)
                    vidid = data_["id"]
                    duration = int(time_to_seconds(data_["duration"]))
                    title = data_["title"]
                    playlist_items.append([vidid, duration, title])
                except Exception:
                    continue
        return playlist_items

    async def track(self, link: str):
        cmd = f'yt-dlp -j --no-playlist {link}'
        res = await shell_cmd(cmd)
        title = ""
        duration = ""
        thumbnail = ""
        link = ""
        if res:
            try:
                data = json.loads(res)
                title = data["title"]
                duration = data["duration"]
                thumbnail = data["thumbnails"][0]["url"].split("?")[0]
                link = data["webpage_url"]
            except Exception:
                pass
        return title, duration, thumbnail, link

    async def formats(self, link: str):
        cmd = f'yt-dlp -F {link}'
        res = await shell_cmd(cmd)
        formats = []
        if res:
            data = res.split("\n")
            for line in data:
                try:
                    line = line.replace("'", '"')
                    data_ = json.loads(line)
                    format_id = data_["format_id"]
                    extension = data_["ext"]
                    format_note = data_["format_note"]
                    formats.append([format_id, extension, format_note])
                except Exception:
                    continue
        return formats

    async def slider(self, link: str, number: int):
        results = VideosSearch(link, limit=number)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def download(self, link: str, quality: str, file_name: str):
        if "&" in link:
            link = link.split("&")[0]
        cmd = f'yt-dlp -f "{quality}" -o "{file_name}.%(ext)s" {link}'
        return await shell_cmd(cmd)
