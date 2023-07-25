import os
import re
import math
import time
import wget
import aiohttp
import asyncio
import logging
import requests
from pathlib import Path
from pySmartDL import SmartDL
from datetime import datetime
from urllib.error import HTTPError
from pyrogram import Client, filters
from urllib.parse import unquote_plus
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup


from MissCutie import pbot
from MissCutie.utils.errors import capture_err


DOWN_PATH = "./downloads"

def humanbytes(size: float) -> str:
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    Dic_powerN = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + "B"

def time_formatter(milliseconds: int) -> str:
    """Time Formatter"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + " day(s), ") if days else "")
        + ((str(hours) + " hour(s), ") if hours else "")
        + ((str(minutes) + " minute(s), ") if minutes else "")
        + ((str(seconds) + " second(s), ") if seconds else "")
        + ((str(milliseconds) + " millisecond(s), ") if milliseconds else "")
    )
    return tmp[:-2]


async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = time_formatter(milliseconds=elapsed_time)
        estimated_total_time = time_formatter(milliseconds=estimated_total_time)

        progress = "`[{0}{1}]` \n".format(
            "".join(["#" for i in range(math.floor(percentage / 5))]),
            "".join(["-" for i in range(20 - math.floor(percentage / 5))]),
        )

        ok = "`{0}%` \n".format(round(percentage, 2))

        tmp = (
            ok
            + progress
            + "\n★ Done: `{0}` \n★  Total: `{1}` \n★  Speed `{2}/s` \n★ Time left: `{3}`".format(
                humanbytes(current),
                humanbytes(total),
                humanbytes(speed),
                estimated_total_time if estimated_total_time != "" else "0 s",
            )
        )
        try:
            await message.edit(
                text="**{}** {}".format(ud_type, tmp)
            )
        except BaseException:
            pass

async def download_video(quality, url, filename):
    html = requests.get(url).content.decode("utf-8")
    video_url = re.search(rf'{quality.lower()}_src:"(.+?)"', html).group(1)
    file_size_request = requests.get(video_url, stream=True)
    total_size = int(file_size_request.headers["Content-Length"])
    block_size = 1024
    with open(filename, "wb") as f:
        for data in file_size_request.iter_content(block_size):
            f.write(data)
    logging.info("Video Downloaded Successfully!")


async def download_from_url(url, dl_loc, message):
    try:
        dl = SmartDL(url, dl_loc, progress_bar=False)
        dl.start(blocking=False)
        while not dl.isFinished():
            total_length = dl.filesize or 0
            downloaded = dl.get_dl_size()
            percentage = dl.get_progress() * 100
            speed = dl.get_speed(human=True)
            estimated_total_time = dl.get_eta(human=True)
            progress = "`[{0}{1}]` \n".format(
                "".join(["#" for i in range(math.floor(percentage / 5))]),
                "".join(["-" for i in range(20 - math.floor(percentage / 5))]),
            )
            ok = "`{0}%` \n".format(round(percentage, 2))
            tmp = (
                ok
                + progress
                + "\n>> DONE: `{0}` \n>> TOTAL: `{1}` \n>> SPEED: `{2}` \n>> TIME LEFT: `{3}`".format(
                    humanbytes(downloaded),
                    humanbytes(total_length),
                    speed.title(),
                    estimated_total_time.title(),
                )
            )
            try:
                await message.edit(
                    text="**{}** {}".format("DOWNLOADING...", tmp),
                )
            except BaseException:
                pass
            await asyncio.sleep(5)
        if dl.isSuccessful():
            return True, dl.get_dest()
        return False, dl.get_errors()
    except HTTPError as error:
        return False, error
    except Exception as error:
        try:
            await message.edit("DOWNLOADING...\nNOTE: KEEP YOUR PATIENT!")
            f_name = wget.download(url, dl_loc)
            return True, f_name
        except HTTPError:
            return False, error

@pbot.on_message(filters.command(["urlupload"]))
@capture_err
async def url_upload(c, m):
    if (
      m.reply_to_message
      and not m.reply_to_message.text
      or not m.reply_to_message
      and not m.text.split(None, 1)[1]
      ):
        return await m.reply_text(
          "Reply to an URL link or Give URL link with this command!"
          )
    if m.reply_to_message:
        link = m.reply_to_message.text
    else:
        link = m.text.split(None, 1)[1]

    msg = await m.reply_text("Processing ...", quote=True)
    if "http" not in link:
        return await msg.edit("This is not a direct download link LMAO!")

    if "|" in link:
        link, filename = link.split("|")
        link = link.strip()
        filename = filename.strip()
    else:
        link = link.strip()
        filename = unquote_plus(os.path.basename(link))
    tmp_directory_for_each_user = DOWN_PATH + "/" + str(m.from_user.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user, exist_ok=True)
    dl_loc = os.path.join(tmp_directory_for_each_user, filename)
    ok, file_path = await download_from_url(link, dl_loc, msg)
    if ok is False:
        return await msg.edit(f"ErRoR...\n```{file_path}```")
    try:
        path = Path(file_path)
    except IndexError:
        return await msg.edit("Downloading Filed!")
    if path.exists():
        start = time.time()
        await msg.edit("Downloaded Succesfully!")
        if path.is_file() and path.stat().st_size < 2097152000:
            await c.send_document(
                chat_id=m.chat.id,
                document=str(path),
                thumb="MissCutie/utils/images/thumb.jpg",
                caption="Url Uploaded Using @MissCutieRobot",
                force_document=False,
                progress=progress_for_pyrogram,
                progress_args=("**Please Wait Uploading...**", msg, start),
            )
            await msg.delete()
        else:
            await msg.edit("Max Upload File Size Allowed 2GB, Do You Think I Will Upload it Fool ?")
        path.unlink(missing_ok=True)
