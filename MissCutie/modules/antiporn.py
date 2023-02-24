from telethon import TelegramClient, events, utils
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import os
from MissCutie import telethn



# Define the NSFW detector function
def detect_nsfw(message):
    # Check if the message contains a photo or a document
    if isinstance(message.media, MessageMediaPhoto) or isinstance(message.media, MessageMediaDocument):
        # Download the media and save it to a file
        media = client.download_media(message.media, file=os.path.basename(message.file.name))
        # Use a NSFW detection library to check if the media contains NSFW content
        # For example, you can use the NSFW model provided by TensorFlow Hub:
        # https://tfhub.dev/google/collections/nsfw/1
        # If the media is NSFW, delete the message
        if nsfw_score > threshold:
            client.delete_messages(message.chat_id, message.id)

# Define the message handler function
@telethn.on(events.NewMessage())
async def handle_new_message(event):
    message = event.message
    detect_nsfw(message)

