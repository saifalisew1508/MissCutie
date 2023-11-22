import uuid
import time
import json
import httpx
import random
import string
import urllib.parse
import asyncio
from io import BytesIO
import os
# import openai
import logging
from telegram.ext import filters, ContextTypes, CommandHandler, MessageHandler
from telegram.constants import ChatAction
from telegram import Update, InputMediaPhoto
from datetime import datetime
from MissCutie import application
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

async def chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = context.args[0] if context.args else None
    if not query:
        await update.message.reply_text("I didn't get this")
        return

    query = urllib.parse.quote(query)
    await context.bot.send_chat_action(update.message.chat_id, ChatAction.TYPING)
    api = SafoneAPI()
    resp = await api.chatgpt(query)
    response = resp.message
    await update.message.reply_text(response)

async def ai_img_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        prompt = context.args[0]
    except IndexError:
        await update.message.reply_text("What should I imagine?\nGive some prompt along with the command")
        return

    x = await update.message.reply_text("Processing...")
    try:
        lex = Lexica(query=prompt).images()
        k = random.sample(lex, 4)
        result = [InputMediaPhoto(image) for image in k]
        await context.bot.send_media_group(
            chat_id=update.message.chat_id,
            media=result,
            reply_to_message_id=update.message.message_id,
        )
        await asyncio.sleep(0)  # Introduce a small delay to allow other tasks to run
        await x.delete()
    except:
        await x.edit("Failed to get images")


application.add_handler(CommandHandler("ask", chatgpt, block=False))
application.add_handler(CommandHandler("imagine", ai_img_search, block=False))
# application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message, block=False))
