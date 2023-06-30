import os
from datetime import datetime
from requests import get, post
from telethon.tl import functions
from MissCutie import telethn
from MissCutie.events import register
from MissCutie.modules.mongo.nsfw_mongo import approved_users
from MissCutie.utils.permissions import is_register_admin


def progress(current, total):
    """ Calculate and return the download progress with given arguments. """
    print(f"Downloaded {current} of {total}\nCompleted {(current / total) * 100}")


@register(pattern=r"^/getqr$")
async def parseqr(event):
    """ For .getqr command, get QR Code content from the replied photo. """
    if event.fwd_from:
        return

    if event.is_group:
        if not await is_register_admin(event.input_chat, event.message.sender_id):
            return

    start = datetime.now()
    downloaded_file_name = await telethn.download_media(event.reply_to_msg_id, progress_callback=progress)
    url = "https://api.qrserver.com/v1/read-qr-code/?outputformat=json"
    with open(downloaded_file_name, "rb") as file:
        files = {"file": file}
        resp = post(url, files=files).json()
    qr_contents = resp[0]["symbol"][0]["data"]
    os.remove(downloaded_file_name)
    end = datetime.now()
    duration = (end - start).seconds
    await event.reply(f"Obtained QRCode contents in {duration} seconds.\n{qr_contents}")


@register(pattern=r"^/makeqr(?: |$)([\s\S]*)")
async def makeqr(event):
    """ For .makeqr command, make a QR Code containing the given content. """
    if event.fwd_from:
        return

    if event.is_group:
        if not await is_register_admin(event.input_chat, event.message.sender_id):
            return

    start = datetime.now()
    input_str = event.pattern_match.group(1)
    message = "SYNTAX: `/makeqr <long text to include>`"
    reply_msg_id = None
    if input_str:
        message = input_str
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        reply_msg_id = previous_message.id
        if previous_message.media:
            downloaded_file_name = await telethn.download_media(previous_message, progress_callback=progress)
            with open(downloaded_file_name, "rb") as file:
                m_list = file.readlines()
            message = ""
            for media in m_list:
                message += media.decode("UTF-8") + "\r\n"
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message

    url = "https://api.qrserver.com/v1/create-qr-code/?data={}&size=200x200&charset-source=UTF-8&charset-target=UTF-8&ecc=L&color=0-0-0&bgcolor=255-255-255&margin=1&qzone=0&format=jpg"
    resp = get(url.format(message), stream=True)
    required_file_name = "temp_qr.webp"
    with open(required_file_name, "w+b") as file:
        for chunk in resp.iter_content(chunk_size=128):
            file.write(chunk)
    await telethn.send_file(event.chat_id, required_file_name, reply_to=reply_msg_id, progress_callback=progress)
    os.remove(required_file_name)
    duration = (datetime.now() - start).seconds
    await event.reply(f"Created QRCode in {duration} seconds")


__help__ = """
- /getqr - Get QR Code content from a replied photo.
- /makeqr <text> - Make a QR Code containing the given text.
"""

__mod_name__ = "QR Code"

__command_list__ = ["getqr", "makeqr"]
__handlers__ = [register]
