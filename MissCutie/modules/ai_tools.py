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
import logging
from openai import OpenAI
from telegram.ext import filters, ContextTypes, CommandHandler, MessageHandler
from telegram.constants import ChatAction
from telegram import Update, InputMediaPhoto
from datetime import datetime
from MissCutie import application, OPENAI_API_KEY


# LexicaAi Art
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
            "model": "lexica-aperture-v3.5"
        })

        prompts = [f"https://image.lexica.art/full_jpg/{ids['id']}" for ids in response.json()["images"]]

        return prompts

# ChatGPT response 
def chat_gpt(prompt):
    OpenAI.api_key = OPENAI_API_KEY
    client = OpenAI()
    MODEL = "gpt-3.5-turbo"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": f"{prompt}"}
        ]
    )
    return response.choices[0].message.content.strip()


# ChatGPT Response Using openai
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = context.args[0]
    chat = update.effective_chat.id
    await context.bot.send_chat_action(update.message.chat_id, ChatAction.TYPING)
    response = chat_gpt(prompt)
    await update.message.reply_text(
        text=f"*Query:* {prompt}\n\n*Response:* {response}",
        parse_mode=ParseMode.MARKDOWN
    )
    
# LexicaAi Image Generator
async def ai_img_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        prompt = context.args[0]
    except IndexError:
        await update.message.reply_text("What should I imagine? Give some prompt along with the command")
        return

    x = await update.message.reply_text("Processing with your Promot...")
    await context.bot.send_chat_action(update.message.chat_id, ChatAction.UPLOAD_PHOTO)
    try:
        lex = Lexica(query=prompt).images()
        k = random.sample(lex, 4)
        result = [InputMediaPhoto(image) for image in k]
        await context.bot.send_chat_action(update.message.chat_id, ChatAction.UPLOAD_PHOTO)
        await context.bot.send_media_group(
            chat_id=update.message.chat_id,
            media=result,
            reply_to_message_id=update.message.message_id,
        )
        await asyncio.sleep(10)  # Introduce a small delay to allow other tasks to run
        await x.delete()
    except:
        await x.edit("Failed to get images")


application.add_handler(CommandHandler("ask", gpt, block=False))
application.add_handler(CommandHandler("imagine", ai_img_search, block=False))
