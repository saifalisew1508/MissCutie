'''

from MissCutie import telethn
from telethon import TelegramClient, events, types, functions
from telethon.errors import MessageNotModifiedError
from telethon.utils import pack_bot_file_id
from telethon.tl.types import MessageMediaDocument
from telethon.extensions import markdown
from telethon.nsfw import check_nsfw

# Setup your Telethon client here

NSFW_THRESHOLD = 0.5  # Set the NSFW score threshold

@telethn.on(events.NewMessage())
async def handle_new_message(event):
    if event.media:
        if isinstance(event.media, MessageMediaDocument):
            document = event.media.document
            if document.mime_type.startswith('image/') or document.mime_type.startswith('video/'):
                file_id = pack_bot_file_id(document.id, document.access_hash)
                file = await telethn.download_media(document, file='.')
                nsfw_score = await check_nsfw(file)
                if nsfw_score >= NSFW_THRESHOLD:
                    await event.delete()
                    await telethn.send_message(event.chat_id, f"NSFW content detected and deleted. NSFW score: {nsfw_score}")
                    


'''
