# import os
# import openai
# import logging
# from telegram.ext import filters, ContextTypes, CommandHandler, MessageHandler
# from telegram import Update
# from datetime import datetime
# from MissCutie import application, OPENAI_API_KEY
# 
# 
# 
# 
# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_message = update.message.text.lower()
#     if user_message in ["hi", "hello", "coé", "oi"]:
#         await update.message.reply_text(f"Hello, how can I help you?")
#     if user_message in ["time?", "time", "hora"]:
#         await update.message.reply_text(f" TIME - {datetime.now()}")
#       return f"You sent the following: {user_message}"
# 
# 
# async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print(update.message.text)
#     question = str(update.message.text[5:].capitalize())
#     print(f"QUESTION: {question}")
#     response = chatGPT_message(question)
#     await update.message.reply_text(
#         f"Question: {question}.\n"
#         f"Answer: {response['choices'][0]['message']['content']}"
#     )
# 
# 
# def chatGPT_message(question):
#     openai.api_key = OPENAI_API_KEY
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "user", "content": f"{question}"},
#         ]
#     )
#     return response
# 
# 
# application.add_handler(CommandHandler("ask", gpt, block=False))
# application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message, block=False))

import uuid
import time 
import json 
import httpx
import random
import string
import requests
from io import BytesIO
from pyrogram import enums
from random import sample
from urllib.parse import quote
from json import JSONDecodeError
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto

from MissCutie import pbot
from MissCutie.utils.errors import capture_err
from SafoneAPI import SafoneAPI

#Lexica Art thing ...
class Lexica:
    def __init__(self, query, negativePrompt="", guidanceScale: int = 7, portrait: bool = True, cookie=None):
        self.query = query
        self.negativePrompt = negativePrompt
        self.guidanceScale = guidanceScale
        self.portrait = portrait
        self.cookie = cookie

    def images(self):
        response = httpx.post("https://lexica.art/api/infinite-prompts", json={
            "text": self.query,
            "searchMode": "images",
            "source": "search",
            "model": "lexica-aperture-v2"
        })

        prompts = [f"https://image.lexica.art/full_jpg/{ids['id']}" for ids in response.json()["images"]]

        return prompts

    def _generate_random_string(self, length):
        chars = string.ascii_letters + string.digits
        result_str = ''.join(random.choice(chars) for _ in range(length))

        return result_str

#Generate gpt response...

@pbot.on_message(filters.command(['gpt', 'askgpt', 'chatgpt']))
@capture_err
async def chatgpt(c, m):
    try:
        query = m.text.split(None, 1)[1]
    except:
        await m.reply_text(
            "i didn't get this"
        )
        return
    query = quote(query)
    await c.send_chat_action(m.chat.id, enums.ChatAction.TYPING)
    api = SafoneAPI()
    resp = await api.chatgpt(query)
    response = resp.message
    await c.send_message(m.chat.id, response, reply_to_message_id=m.id)
    await c.send_chat_action(m.chat.id, enums.ChatAction.CANCEL)

@pbot.on_message(filters.command(["imagine"]))
@capture_err
async def ai_img_search(c,m):
  try:
    prompt= m.text.split(None, 1)[1]
  except IndexError:
    await m.reply_text("`What should i imagine??\nGive some prompt along with the command`")
    return
  x = await m.reply_text("`Processing...`")
  try:
    lex = Lexica(query=prompt).images()
    k = sample(lex, 4)
    result = [InputMediaPhoto(image) for image in k]
    await c.send_media_group(
              chat_id=m.chat.id,
              media=result,
              reply_to_message_id=m.id,
          )
    await x.delete()
  except:
    await x.edit("`Failed to get images`")
