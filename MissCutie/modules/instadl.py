import os 
import io
import wget
import subprocess
from pyrogram import Client, filters
from requests import JSONDecodeError, get

from MissCutie import pbot
from MissCutie.utils.errors import capture_err
from pyrogram.types import InputMedia, InputMediaPhoto, InputMediaVideo, InputMediaDocument, InlineKeyboardButton, InlineKeyboardMarkup









@pbot.on_message(filters.command(["instadl", "insdl", "insta", "instadownload"]))
@capture_err
async def idgl(c, m):
    try:
        url = m.text.split(None, 1)[1]
    except IndexError:
        url = None
    if not url:
        await m.reply_text("`Pass a URL along with the command`")
        return
    if url:
        msg = await m.reply_text("Downloading...................................................................................................................................")
        rdata = get(f"https://igdownloader.onrender.com/dl?key=naveen&url={url}").json()
        data = rdata["urls"]
        try:
              ismediagroup = bool(len(data) > 1)
              if not ismediagroup:
                      await m.reply_video(data[0], caption=rdata["caption"]) if "mp4" in data[0] else await m.reply_photo(data[0], caption=rdata["caption"])
              else:
                    files = []
                    for ind, x in enumerate(data):
                            if "mp4" in data[ind]:
                               files.append(InputMediaVideo(x, caption=rdata["caption"] if ind == 0 else ""))
                            else:
                               files.append(InputMediaPhoto(x, caption=rdata["caption"] if ind == 0 else ""))

                    await c.send_media_group(m.chat.id, files)
                    await msg.delete()
        except:
          for i in data:
            await m.reply_video(i)
