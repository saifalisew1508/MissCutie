from telethon import TelegramClient, events, sync
from MissCutie import telethn
import re



# Define a regex pattern to match any messages containing NSFW content
pattern = re.compile(r'.*\b(nsfw|nudity|porn|sex)\b.*', re.IGNORECASE)

# Define a function to handle incoming messages
@telethn.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    message = event.message
    if message.media and message.media.photo:
        # If the message contains a photo, check if it matches the filter
        if re.match(pattern, message.message):
            # If the message matches the filter, delete it and warn the user
            await message.delete()
            await telethn.send_message(chat, f"Sorry, {event.sender.first_name}, NSFW content is not allowed in this group!")
    elif message.message:
        # If the message contains text, check if it matches the filter
        if re.match(pattern, message.message):
            # If the message matches the filter, delete it and warn the user
            await message.delete()
            await telethn.send_message(chat, f"Sorry, {event.sender.first_name}, NSFW content is not allowed in this group!")

# Start the client
client.run_until_disconnected()
