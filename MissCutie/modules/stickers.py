import os
import urllib.request as urllib
from html import escape
import math

from httpx import AsyncClient
from bs4 import BeautifulSoup as bs
from PIL import Image
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      Update, User, Message)
from telegram.error import TelegramError, BadRequest
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.helpers import mention_html
from MissCutie import LOGGER, application
from MissCutie.modules.disable import DisableAbleCommandHandler
from MissCutie.modules.helper_funcs.misc import convert_gif

combot_stickers_url = "https://combot.org/telegram/stickers?q="


async def stickerid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker and not msg.reply_to_message.forum_topic_created:
        await update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", The sticker id you are replying is :\n <code>"
            + escape(msg.reply_to_message.sticker.file_id)
            + "</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please reply to sticker message to get id sticker",
            parse_mode=ParseMode.HTML,
        )


async def cb_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    split = msg.text.split(" ", 1)
    if len(split) == 1:
        await msg.reply_text("Provide some name to search for pack.")
        return
    async with AsyncClient() as client:
        r = await client.get(combot_stickers_url + split[1])
    text = r.text
    soup = bs(text, "lxml")
    results = soup.find_all("a", {"class": "sticker-pack__btn"})
    titles = soup.find_all("div", "sticker-pack__title")
    if not results:
        await msg.reply_text("No results found :(.")
        return
    reply = f"Stickers for *{split[1]}*:"
    for result, title in zip(results, titles):
        link = result["href"]
        reply += f"\n• [{title.get_text()}]({link})"
    await msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


async def getsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        new_file = await bot.get_file(file_id)
        await new_file.download_to_drive(f"sticker_{user.id}.png")
        await bot.send_document(
            chat.id, 
            document=open(f"sticker_{user.id}.png", "rb"),
            reply_to_message_id=msg.message_id,
            message_thread_id=msg.message_thread_id if chat.is_forum else None
        )
        os.remove(f"sticker_{user.id}.png")
    else:
        await update.effective_message.reply_text(
            "Please reply to a sticker for me to upload its PNG.",
        )


async def kang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    if msg.reply_to_message and msg.reply_to_message.sticker and not msg.reply_to_message.forum_topic_created:
        sticker_emoji = msg.reply_to_message.sticker.emoji
        file_id = msg.reply_to_message.sticker.file_id
        new_file = await context.bot.get_file(file_id)
        await new_file.download_to_drive(f"kangsticker_{user.id}.png")
        packname = f"kang_{user.id}"
        try:
            await context.bot.add_sticker_to_set(
                user_id=user.id,
                name=packname,
                png_sticker=open(f"kangsticker_{user.id}.png", "rb"),
                emojis=sticker_emoji,
            )
            await msg.reply_text(
                f"Sticker Successfully added to [pack](t.me/addstickers/{packname})"
                + f"\nEmoji is: {sticker_emoji}",
                parse_mode=ParseMode.MARKDOWN
            )
        except TelegramError as e:
            await msg.reply_text(
                f"Failed to add sticker to pack. Reason: {str(e)}"
            )
        os.remove(f"kangsticker_{user.id}.png")
    else:
        await update.effective_message.reply_text(
            "Please reply to a sticker for me to kang it.",
        )


async def kang_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user

    if msg.reply_to_message and not msg.reply_to_message.forum_topic_created:
        if msg.reply_to_message.video and msg.reply_to_message.video.mime_type == "video/mp4":
            file_id = msg.reply_to_message.video.file_id
            new_file = await context.bot.get_file(file_id)
            await new_file.download_to_drive(f"kangsticker_{user.id}.mp4")
        elif msg.reply_to_message.animation:
            file_id = msg.reply_to_message.animation.file_id
            new_file = await context.bot.get_file(file_id)
            await new_file.download_to_drive(f"kang_{user.id}.mp4")
            convert_gif(f"kang_{user.id}.mp4")
        else:
            await msg.reply_text("Sorry, I can only kang videos and GIFs.")

        is_animated = False
        is_video = False
        is_gif = False
        if msg.reply_to_message.video:
            is_video = True
        elif msg.reply_to_message.animation:
            is_gif = True

        packname = "video" + str(user.id) + "_by_" + context.bot.username
        packname_found = 0
        max_stickers = 120

        while packname_found == 0:
            try:
                stickerset = await context.bot.get_sticker_set(packname)
                if len(stickerset.stickers) >= max_stickers:
                    packnum += 1
                    packname = (
                        "animated"
                        + str(packnum)
                        + "_"
                        + str(user.id)
                        + "_by_"
                        + context.bot.username
                    )

                else:
                    packname_found = 1
            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    packname_found = 1

        try:
            if is_video:
                await context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    tgs_sticker=open(f"kangsticker_{user.id}.mp4", "rb"),
                    emojis=sticker_emoji,
                )
            elif is_gif:
                await context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    tgs_sticker=open(f"kang_{user.id}.mp4", "rb"),
                    emojis=sticker_emoji,
                )
            await msg.reply_text(
                f"Sticker Successfully added to [pack](t.me/addstickers/{packname})"
                + f"\nEmoji is: {sticker_emoji}",
                parse_mode=ParseMode.MARKDOWN
            )
        except TelegramError as e:
            await msg.reply_text(
                f"Failed to add sticker to pack. Reason: {str(e)}"
            )

        if is_gif:
            os.remove(f"kang_{user.id}.mp4")
        os.remove(f"kangsticker_{user.id}.mp4")
    else:
        await msg.reply_text(
            "Please reply to a video or GIF for me to kang it.",
        )


async def math_eval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user

    if msg.reply_to_message and not msg.reply_to_message.forum_topic_created:
        expression = msg.reply_to_message.text
        try:
            result = eval(expression)
            await msg.reply_text(
                f"Expression: {expression}\nResult: {result}",
            )
        except Exception as e:
            await msg.reply_text(
                f"Error evaluating expression: {str(e)}",
            )
    else:
        await msg.reply_text(
            "Please reply to a message containing a mathematical expression for me to evaluate.",
        )


STICKERID_HANDLER = DisableAbleCommandHandler("stickerid", stickerid, block=False)
CB_STICKER_HANDLER = DisableAbleCommandHandler("cbsticker", cb_sticker, block=False)
GETSTICKER_HANDLER = DisableAbleCommandHandler("getsticker", getsticker, block=False)
KANG_HANDLER = DisableAbleCommandHandler("kang", kang, block=False)
KANG_VIDEO_HANDLER = DisableAbleCommandHandler("kangvideo", kang_video, block=False)
MATH_EVAL_HANDLER = DisableAbleCommandHandler("matheval", math_eval, block=False)

application.add_handler(STICKERID_HANDLER)
application.add_handler(CB_STICKER_HANDLER)
application.add_handler(GETSTICKER_HANDLER)
application.add_handler(KANG_HANDLER)
application.add_handler(KANG_VIDEO_HANDLER)
application.add_handler(MATH_EVAL_HANDLER)



__help__ = """
 ➥ /stickerid*:* reply to a sticker to me to tell you its file ID.
 ➥ /getsticker*:* reply to a sticker to me to upload its raw PNG file.
 ➥ /delstcker*:* reply to a sticker to delete it from the pack, I can delete what I made only.
 ➥ /kang*:* reply to sticker (animated/static/video) or image or gif to kang into your own pack.
 ➥ /stickers*:* Find stickers for given term on combot sticker catalogue
"""

__mod_name__ = "Stickers"
