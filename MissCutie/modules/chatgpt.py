import os
import openai
import logging
from telegram.ext import filters, ContextTypes, CommandHandler, MessageHandler
from telegram import Update
from datetime import datetime
from MissCutie import application, OPENAI_API_KEY




async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    if user_message in ["hi", "hello", "coé", "oi"]:
        await update.message.reply_text(f"Hello, how can I help you?")
    if user_message in ["time?", "time", "hora"]:
        await update.message.reply_text(f" TIME - {datetime.now()}")
    # return f"You sent the following: {user_message}"


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text)
    question = str(update.message.text[5:].capitalize())
    print(f"QUESTION: {question}")
    response = chatGPT_message(question)
    await update.message.reply_text(
        f"Question: {question}.\n"
        f"Answer: {response['choices'][0]['message']['content']}"
    )


def chatGPT_message(question):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"{question}"},
        ]
    )
    return response


application.add_handler(CommandHandler("gpt", gpt))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
