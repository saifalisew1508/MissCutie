import openai
import telethon
from telethon import TelegramClient, events
import asyncio


from MissCutie import telethn, BOT_NAME

# Your OpenAI API key
openai.api_key = "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"


# Your GPT model ID
model_id = "text-davinci-003"

# The maximum number of tokens to generate
max_tokens = 1000

# Register the event handler for incoming messages
@telethn.on(events.NewMessage(pattern="^[!/]chat ?(.*)"))
async def handle_new_message(event):
    if event.is_reply:
        replied = await event.get_reply_message()
        sender = replied.sender
    # Generate a response using GPT
    response = await generate_response(event.message.text)
    # Send the response back to the user
    await telethn.send_message(event.message.peer_id, response)

async def generate_response(prompt):
    # Call the OpenAI API to generate a response
    completions = openai.Completion.create(
        engine=model_id,
        prompt=prompt,
        max_tokens=max_tokens,
    )
    message = completions.choices[0].text
    return message




__help__ = f"""
*{BOT_NAME} has an ChatGPT & KukiChat whic provides you a seemingless chatting experience :*
 
➥ /chat *:* ask Your Queries

 ➥ /chatbot *:* Shows chatbot control panel
"""

__mod_name__ = "ChatGPT"
