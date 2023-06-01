from telethon import TelegramClient, events
from openai import ChatCompletionClient
import asyncio


from MissCutie import telethn, BOT_NAME

# Your OpenAI API key
chatgpt = ChatCompletionClient(api_key='4rde2g7cprXOamWae3eMT3BlbkFJQ5yINbloY7KISJuN2DC7')


# Register the event handler for incoming messages
@telethn.on(events.NewMessage(pattern="^[!/]chat ?(.*)"))
async def handle_new_message(event):
    if not event.is_private:
        return

    message = event.message.message
    sender_id = event.sender_id

    # Process the message using ChatGPT
    response = chatgpt.complete(message, sender_id=sender_id)

    # Send the response back to the user
    await event.respond(response.choices[0].text)




__help__ = f"""
*{BOT_NAME} has an ChatGPT & KukiChat whic provides you a seemingless chatting experience :*
 
 ➥ /chat *:* ask Your Queries

 ➥ /chatbot *:* Shows chatbot control panel
"""

__mod_name__ = "ChatGPT"
