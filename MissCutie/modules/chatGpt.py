import openai
from telethon import Telegramtelethn, events
from MissCutie import telethn, BOT_NAME

# Set up your OpenAI API credentials
openai.api_key = '4rde2g7cprXOamWae3eMT3BlbkFJQ5yINbloY7KISJuN2DC7'



# Define the event handler for incoming messages
@telethn.on(events.NewMessage(pattern='/ask', incoming=True))
async def handle_ask_command(event):
    if not event.is_private:
        return

    message = event.message.message
    sender_id = event.sender_id

    # Extract the question from the message
    question = message.replace('/ask', '').strip()

    if question:
        # Process the question using OpenAI GPT-3
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ],
            conversation_id=str(sender_id)
        )

        # Extract the generated response from the OpenAI API
        answer = response.choices[0].message.content

        # Send the response back to the user
        await event.respond(answer)
    else:
        # If no question is provided, send a help message
        help_message = "Please provide a question. Usage: /ask [your question]"
        await event.respond(help_message)


__help__ = f"""
*{BOT_NAME} has an ChatGPT & KukiChat whic provides you a seemingless chatting experience :*
 
 ➥ /chat *:* ask Your Queries

 ➥ /chatbot *:* Shows chatbot control panel
"""

__mod_name__ = "ChatGPT"
