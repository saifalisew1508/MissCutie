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
from telegram.ext import filters, ContextTypes, CommandHandler, MessageHandler, Application
from telegram.constants import ChatAction, ParseMode
from telegram import Update, InputMediaPhoto
from datetime import datetime


# Ensure OPENAI_API_KEY is fetched from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

# LexicaAi Art
class Lexica:
    def __init__(self, query, negativePrompt="", guidanceScale: int = 7, portrait: bool = True, cookie=None):
        self.query = query
        self.negativePrompt = negativePrompt
        self.guidanceScale = guidanceScale
        self.portrait = portrait
        self.cookie = cookie

    def images(self):
        try:
            response = httpx.post("https://lexica.art/api/infinite-prompts", json={
                "text": self.query,
                "searchMode": "images",
                "source": "search",
                "model": "lexica-aperture-v3.5"
            })
            response.raise_for_status()
            prompts = [f"https://image.lexica.art/full_jpg/{ids['id']}" for ids in response.json().get("images", [])]
            return prompts
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        return []

# ChatGPT response 
def chat_gpt(prompt):
    OpenAI.api_key = OPENAI_API_KEY
    client = OpenAI()
    MODEL = "gpt-3.5-turbo"
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"An error occurred with OpenAI API: {e}")
        return "An error occurred while processing your request."

# ChatGPT Response Using openai
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a prompt for ChatGPT.")
        return

    prompt = ' '.join(context.args)
    chat = update.effective_chat.id
    await context.bot.send_chat_action(chat, ChatAction.TYPING)
    response = chat_gpt(prompt)
    await update.message.reply_text(
        text=f"*Query:* {prompt}\n\n*Response:* {response}",
        parse_mode=ParseMode.MARKDOWN
    )

# LexicaAi Image Generator
async def ai_img_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("What should I imagine? Give some prompt along with the command.")
        return

    prompt = ' '.join(context.args)
    x = await update.message.reply_text("Processing with your Prompt...")
    await context.bot.send_chat_action(update.message.chat_id, ChatAction.UPLOAD_PHOTO)
    try:
        lex = Lexica(query=prompt).images()
        if not lex:
            await x.edit_text("Failed to get images.")
            return

        k = random.sample(lex, min(len(lex), 4))
        result = [InputMediaPhoto(image) for image in k]
        await context.bot.send_media_group(
            chat_id=update.message.chat_id,
            media=result,
            reply_to_message_id=update.message.message_id,
        )
        await asyncio.sleep(10)  # Introduce a small delay to allow other tasks to run
        await x.delete()
    except Exception as e:
        logger.error(f"An error occurred while fetching images: {e}")
        await x.edit_text("Failed to get images.")

application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

application.add_handler(CommandHandler("ask", gpt, block=False))
application.add_handler(CommandHandler("imagine", ai_img_search, block=False))
