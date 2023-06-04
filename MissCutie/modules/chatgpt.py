from io import *

import openai
from kynaylibs.nan.utils.http import *
from pyrogram import filters
from pyrogram.types import *

from MissCutie import OPENAI_API, pbot, BOT_NAME


class OpenAi:
    def text(self):
        openai.api_key = OPENAI_API
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"<b>Q: <code>{self}</code>\nA:</b>",
            temperature=0,
            max_tokens=500,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        return response.choices[0].text

    def photo(self):
        openai.api_key = OPENAI_API
        response = openai.Image.create(prompt=self, n=1, size="1024x1024")
        return response["data"][0]["url"]


@pbot.on_message(filters.me & filters.command(["ai", "ask"]))
async def ai(client, message):
    if len(message.command) == 1:
        return await message.edit_text(
            f"Type <code>/ai [question]</code> to use OpenAI"
        )
    msg = await message.edit_text("`Processing...`")
    biji = message.text.split(None, 1)[1]
    try:
        response = OpenAi.text(biji)
        await msg.edit_text(f"**Q:** {biji}\n\n**A:** {response}")
    except Exception as e:
        await msg.edit_text(f"**There is an error!!\n`{e}`**")


@pbot.on_message(filters.me & filters.command(["img"]))
async def img(client, message):
    if len(message.command) == 1:
        return await eor(
            message, f"Type <code>/img [question]</code> to use OpenAI"
        )
    try:
        biji = message.text.split(None, 1)[1]
        response = OpenAi.photo(biji)
        await pbot.send_photo(message.chat.id, response)
    except Exception as e:
        await message.edit(f"**There is an error!!\n`{e}`**")
        # await msg.delete()


__help__ = f"""
*{BOT_NAME} has an ChatGPT & KukiChat whic provides you a seemingless chatting experience :*
 
    Command: /ai [query]
 ➥ Explanation: To ask a question to AI

    Command: /img [query]
 ➥ Explanation: To search for images to AI

 ➥ /chatbot *:* Shows chatbot control panel
"""

__mod_name__ = "ChatGPT"
