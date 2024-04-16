import math
import os
import textwrap
import urllib.request as urllib
from html import escape
from urllib.parse import quote as urlquote

import cv2
import ffmpeg
from bs4 import BeautifulSoup
from cloudscraper import CloudScraper
from PIL import Image, ImageDraw, ImageFont
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler
from MissCutie.modules.disable import DisableAbleCommandHandler
from telegram.helpers import mention_html
from telegram.error import TelegramError, BadRequest
from telegram import InputSticker

from MissCutie import application
from MissCutie import telethn as bot
from MissCutie.events import register as crazy

combot_stickers_url = "https://combot.org/telegram/stickers?q="


async def convert_gif(input):

    vid = cv2.VideoCapture(input)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)

    # check height and width to scale
    if width > height:
        width = 512
        height = -1
    elif height > width:
        height = 512
        width = -1
    elif width == height:
        width = 512
        height = 512

    converted_name = "kangsticker.webm"

    (
        ffmpeg.input(input)
        .filter("fps", fps=30, round="up")
        .filter("scale", width=width, height=height)
        .trim(start="00:00:00", end="00:00:03", duration="3")
        .output(
            converted_name,
            vcodec="libvpx-vp9",
            **{
                #'vf': 'scale=512:-1',
                "crf": "30"
            },
        )
        .overwrite_output()
        .run()
    )

    return converted_name


async def stickerid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        await update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", The Sticker ID to you are Replying is :\n<code>"
            + escape(msg.reply_to_message.sticker.file_id)
            + "</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please Reply to Sticker to get its ID",
            parse_mode=ParseMode.HTML,
        )


scraper = CloudScraper()


async def get_cbs_data(query, page, user_id):
    # returns (text, buttons)
    text = scraper.get(f"{combot_stickers_url}{urlquote(query)}&page={page}").text
    soup = BeautifulSoup(text, "lxml")
    div = soup.find("div", class_="page__container")
    packs = div.find_all("a", class_="sticker-pack__btn")
    titles = div.find_all("div", "sticker-pack__title")
    has_prev_page = has_next_page = None
    highlighted_page = div.find("a", class_="pagination__link is-active")
    if highlighted_page is not None and user_id is not None:
        highlighted_page = highlighted_page.parent
        has_prev_page = highlighted_page.previous_sibling.previous_sibling is not None
        has_next_page = highlighted_page.next_sibling.next_sibling is not None
    buttons = []
    if has_prev_page:
        buttons.append(
            InlineKeyboardButton(text="⟨", callback_data=f"cbs_{page - 1}_{user_id}")
        )
    if has_next_page:
        buttons.append(
            InlineKeyboardButton(text="⟩", callback_data=f"cbs_{page + 1}_{user_id}")
        )
    buttons = InlineKeyboardMarkup([buttons]) if buttons else None
    text = f"Sticker for <code>{escape(query)}</code>:\nPage: {page}"
    if packs and titles:
        for pack, title in zip(packs, titles):
            link = pack["href"]
            text += f"\n• <a href='{link}'>{escape(title.get_text())}</a>"
    elif page == 1:
        text = "No Result Found, Try a Different Term"
    else:
        text += "\n\n\Ok, So there is Nothing"
    return text, buttons


async def cb_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    query = " ".join(msg.text.split()[1:])
    if not query:
        await msg.reply_text("Provide some term, So that I can search the Sticker-Pack")
        return
    if len(query) > 50:
        await msg.reply_text("provide a Search Query under 50 characters")
        return
    if msg.from_user:
        user_id = msg.from_user.id
    else:
        user_id = None
    text, buttons = await get_cbs_data(query, 1, user_id)
    await msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=buttons)


async def cbs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, page, user_id = query.data.split("_", 2)
    if int(user_id) != query.from_user.id:
        await query.answer("ɴᴏᴛ ғᴏʀ ʏᴏᴜ", cache_time=60 * 60)
        return
    search_query = query.message.text.split("\n", 1)[0].split(maxsplit=2)[2][:-1]
    text, buttons = await get_cbs_data(search_query, int(page), query.from_user.id)
    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=buttons)
    await query.answer()


async def getsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = update.effective_message
    chat_id = update.effective_chat.id
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        with BytesIO() as file:
            file.name = "sticker.png"
            new_file = await bot.get_file(file_id)
            await new_file.download(out=file)
            file.seek(0)
            await bot.send_document(chat_id, document=file)
    else:
        await update.effective_message.reply_text(
            "Please reply a sticker to upload its PNG.",
        )


async def kang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    args = context.args
    packnum = 0
    packname = "a" + str(user.id) + "_by_" + context.bot.username
    packname_found = 0
    max_stickers = 120

    while packname_found == 0:
        try:
            stickerset = await context.bot.get_sticker_set(packname)
            if len(stickerset.stickers) >= max_stickers:
                packnum += 1
                packname = (
                    "a"
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

    kangsticker = "kangsticker.png"
    is_animated = False
    is_video = False
    # convert gif method
    is_gif = False
    file_id = ""

    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            if msg.reply_to_message.sticker.is_animated:
                is_animated = True
            elif msg.reply_to_message.sticker.is_video:
                is_video = True
            file_id = msg.reply_to_message.sticker.file_id
        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif (
            await msg.reply_to_message.document
            and not msg.reply_to_message.document.mime_type == "video/mp4"
        ):
            file_id = await msg.reply_to_message.document.file_id
        elif msg.reply_to_message.animation:
            file_id = await msg.reply_to_message.animation.file_id
            is_gif = True
        else:
            await msg.reply_text("Sorry, But I can't Kang this!")
        kang_file = await context.bot.get_file(file_id)
        if not is_animated and not (is_video or is_gif):
            await kang_file.download_to_drive("kangsticker.png")
        elif is_animated:
            await kang_file.download_to_drive("kangsticker.tgs")
        elif is_video and not is_gif:
            await kang_file.download_to_drive("kangsticker.webm")
        elif is_gif:
            await kang_file.download_to_drive("kang.mp4")
            convert_gif("kang.mp4")

        if args:
            sticker_emoji = str(args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🙂"

        adding_process = await msg.reply_text(
            "<b>Please Wait...</b>",
            parse_mode=ParseMode.HTML,
        )

        if not is_animated and not (is_video or is_gif):
            try:
                im = Image.open(kangsticker)
                maxsize = (512, 512)
                if (im.width and im.height) < 512:
                    size1 = im.width
                    size2 = im.height
                    if im.width > im.height:
                        scale = 512 / size1
                        size1new = 512
                        size2new = size2 * scale
                    else:
                        scale = 512 / size2
                        size1new = size1 * scale
                        size2new = 512
                    size1new = math.floor(size1new)
                    size2new = math.floor(size2new)
                    sizenew = (size1new, size2new)
                    im = im.resize(sizenew)
                else:
                    im.thumbnail(maxsize)
                if not msg.reply_to_message.sticker:
                    im.save(kangsticker, "PNG")
                await context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    sticker=InputSticker(
                        sticker=open("kangsticker.png", "rb"),
                        emoji_list=(sticker_emoji)
                    )
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Sticker Pack", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                await adding_process.edit_text(
                    f"<b>Your Sticker has been Successfully Added</b>"
                    f"\nEmoji 👉 : {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )

            except OSError as e:
                print(e)
                return

            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    await makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        sticker=open("kangsticker.png", "rb"),
                        is_png_sticker=True
                    )
                    await adding_process.delete()
                elif e.message == "Sticker_png_dimensions":
                    im.save(kangsticker, "PNG")
                    adding_process = await msg.reply_text(
                        "<b>Wait for a Moment...</b>",
                        parse_mode=ParseMode.HTML,
                    )
                    await context.bot.add_sticker_to_set(
                        user_id=user.id,
                        name=packname,
                        sticker=InputSticker(
                            sticker=open("kangsticker.png", "rb"),
                            emoji_list=(sticker_emoji)
                       )
                    )
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Sticker Pack", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    await adding_process.edit_text(
                        f"<b>Your Sticker has been Successfully Added</b>"
                        f"\nEmoji 👉 : {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                elif e.message == "Invalid sticker emojis":
                    await msg.reply_text("Invalid emoji(s).")
                elif e.message == "Stickers_too_much":
                    await msg.reply_text("Max packsize reached. Press F to pay respecc.")
                elif e.message == "Internal Server Error: sticker set not found (500)":
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Sticker Pack", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    await msg.reply_text(
                        f"<b>Your Sticker has been Successfully Added</b>"
                        f"\nEmoji 👉 : {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                print(e)

        elif is_animated:
            packname = "animated" + str(user.id) + "_by_" + context.bot.username
            packname_found = 0
            max_stickers = 50
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
                await context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    sticker=InputSticker(
                    sticker=open("kangsticker.tgs", "rb"),
                    emoji_list=(sticker_emoji)
                 )
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Sticker Pack", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                await adding_process.edit_text(
                    f"<b>Your Sticker has been Successfully Added</b>"
                    f"\nEmoji 👉 : {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    await makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        sticker=open("kangsticker.tgs", "rb"),
                        is_tgs_sticker=True
                    )
                    await adding_process.delete()
                elif e.message == "Invalid sticker emojis":
                    await msg.reply_text("Invalid emoji(s).")
                elif e.message == "Internal Server Error: sticker set not found (500)":
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Sticker Pack", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    await adding_process.edit_text(
                        f"<b>Your Sticker has been Successfully Added</b>"
                        f"\nEmoji 👉 : {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                print(e)

        elif is_video or is_gif:
            packname = "video" + str(user.id) + "_by_" + context.bot.username
            packname_found = 0
            max_stickers = 50
            while packname_found == 0:
                try:
                    stickerset = await context.bot.get_sticker_set(packname)
                    if len(stickerset.stickers) >= max_stickers:
                        packnum += 1
                        packname = (
                            "video"
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
                await context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    sticker=InputSticker(
                    sticker=open("kangsticker.webm", "rb"),
                    emoji_list=(sticker_emoji)
                 )
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Sticker Pack", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                await adding_process.edit_text(
                    f"<b>Your Sticker has been Successfully Added</b>"
                    f"\nEmoji 👉 : {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    await makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        sticker=open("kangsticker.webm", "rb"),
                        is_webm_sticker=True
                    )
                    await adding_process.delete()
                elif e.message == "Invalid sticker emojis":
                    await msg.reply_text("Invalid emoji(s).")
                elif e.message == "Internal Server Error: sticker set not found (500)":
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Sticker Pack", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    await adding_process.edit_text(
                        f"<b>Your Sticker has been Successfully Added</b>"
                        f"\nEmoji : {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                print(e)

    elif args:
        try:
            try:
                urlemoji = msg.text.split(" ")
                png_sticker = urlemoji[1]
                sticker_emoji = urlemoji[2]
            except IndexError:
                sticker_emoji = "🙃"
            urllib.urlretrieve(png_sticker, kangsticker)
            im = Image.open(kangsticker)
            maxsize = (512, 512)
            if (im.width and im.height) < 512:
                size1 = im.width
                size2 = im.height
                if im.width > im.height:
                    scale = 512 / size1
                    size1new = 512
                    size2new = size2 * scale
                else:
                    scale = 512 / size2
                    size1new = size1 * scale
                    size2new = 512
                size1new = math.floor(size1new)
                size2new = math.floor(size2new)
                sizenew = (size1new, size2new)
                im = im.resize(sizenew)
            else:
                im.thumbnail(maxsize)
            im.save(kangsticker, "PNG")
            await msg.reply_photo(photo=open("kangsticker.png", "rb"))
            await context.bot.add_sticker_to_set(
                user_id=user.id,
                name=packname,
                sticker=InputSticker(
                    sticker=open("kangsticker.png", "rb"),
                    emoji_list=(sticker_emoji)
                 )
            )
            edited_keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Sticker Pack", url=f"t.me/addstickers/{packname}"
                        )
                    ]
                ]
            )
            await adding_process.edit_text(
                f"<b>Your Sticker has been Successfully Added</b>"
                f"\nEmoji 👉 : {sticker_emoji}",
                reply_markup=edited_keyboard,
                parse_mode=ParseMode.HTML,
            )
        except OSError as e:
            await msg.reply_text("Sorry, I can't Kang that")
            print(e)
            return
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                await makepack_internal(
                    update,
                    context,
                    msg,
                    user,
                    sticker_emoji,
                    packname,
                    packnum,
                    sticker=open("kangsticker.png", "rb"),
                    is_png_sticker=True
                )
                await adding_process.delete()
            elif e.message == "Sticker_png_dimensions":
                im.save(kangsticker, "png")
                await context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    sticker=InputSticker(
                    sticker=open("kangsticker.png", "rb"),
                    emoji_list=(sticker_emoji)
                    )
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Sticker Pack", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                await adding_process.edit_text(
                    f"<b>Your Sticker has been Successfully Added</b>"
                    f"\nEmoji 👉 : {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            elif e.message == "Invalid sticker emojis":
                await msg.reply_text("Invalid emoji(s).")
            elif e.message == "Stickers_too_much":
                await msg.reply_text("Max packsize reached. Press F to pay respect.")
            elif e.message == "Internal Server Error: sticker set not found (500)":
                await msg.reply_text(
                    f"<b>Your Sticker has been Successfully Added</b>"
                    f"\nEmoji 👉 : {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            print(e)
    else:
        packs_text = "*Please reply to a Sticker or Image to Kang it!*\n"
        if packnum > 0:
            firstpackname = "a" + str(user.id) + "_by_" + context.bot.username
            for i in range(0, packnum + 1):
                if i == 0:
                    packs = f"t.me/addstickers/{firstpackname}"
                else:
                    packs = f"t.me/addstickers/{packname}"
        else:
            packs = f"t.me/addstickers/{packname}"

        edited_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Sticker Pack", url=f"{packs}"),
                ],
            ]
        )
        await msg.reply_text(
            packs_text, reply_markup=edited_keyboard, parse_mode=ParseMode.MARKDOWN
        )
    try:
        if os.path.isfile("kangsticker.png"):
            os.remove("kangsticker.png")
        elif os.path.isfile("kangsticker.tgs"):
            os.remove("kangsticker.tgs")
        elif os.path.isfile("kangsticker.webm"):
            os.remove("kangsticker.webm")
        elif os.path.isfile("kang.mp4"):
            os.remove("kang.mp4")
    except:
        pass


async def makepack_internal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    msg,
    user,
    emoji,
    packname,
    packnum,
    sticker,
    is_png_sticker=None,
    is_tgs_sticker=None,
    is_webm_sticker=None
):
    name = user.first_name
    name = name[:50]
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Sticker Pack", url=f"t.me/addstickers/{packname}")]]
    )
    try:
        extra_version = ""
        if packnum > 0:
            extra_version = " " + str(packnum)
        if is_png_sticker:
            sticker_pack_name = (
                f"{name}'s sticker pack (@{context.bot.username})" + extra_version
            )
            success = await context.bot.create_new_sticker_set(
                user_id=user.id,
                name=packname,
                title=sticker_pack_name,
                stickers=[InputSticker(
                    sticker=sticker,
                    emoji_list=(emoji)
                 )],
                sticker_format="static"
            )
        if is_tgs_sticker:
            sticker_pack_name = (
                f"{name}'s animated pack (@{context.bot.username})" + extra_version
            )
            success = await context.bot.create_new_sticker_set(
                user.id,
                packname,
                sticker_pack_name,
                stickers=[InputSticker(
                    sticker=sticker,
                    emoji_list=(emoji)
                 )],
                sticker_format="animated"
            )
        if is_webm_sticker:
            sticker_pack_name = (
                f"{name}'s video pack (@{context.bot.username})" + extra_version
            )
            success = await context.bot.create_new_sticker_set(
                user.id,
                packname,
                sticker_pack_name,
                stickers=[InputSticker(
                    sticker=sticker,
                    emoji_list=(emoji)
                 )],
                sticker_format="video"
            )

    except TelegramError as e:
        print(e)
        if e.message == "Sticker set name is already occupied":
            await msg.reply_text(
                "<b>Your Sticker Pack is already created!</b>"
                "\n\n<b>Send /stickers to find any sticker pack.</b>",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
        elif e.message == "Peer_id_invalid" or "bot was blocked by the user":
            await msg.reply_text(
                f"{context.bot.first_name} was blocked by you.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Unblock", url=f"t.me/{context.bot.username}"
                            )
                        ]
                    ]
                ),
            )
        elif e.message == "Internal Server Error: created sticker set not found (500)":
            await msg.reply_text(
                "<b>Your Sticker Pack has been created!</b>"
                "\n\n<b>Send /stickers to find sticker pack.</b>",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
        return

    if success:
        await msg.reply_text(
            "<b>Your Sticker Pack has been created!</b>"
            "\n\n<b>Send /stickers to find sticker pack.</b>",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        await msg.reply_text("Failed to create sticker pack. Possibly due to blek mejik.")


async def getsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = update.effective_message
    chat_id = update.effective_chat.id
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        new_file = await bot.get_file(file_id)
        await new_file.download_to_drive("sticker.png")
        await bot.send_document(chat_id, document=open("sticker.png", "rb"))
        os.remove("sticker.png")
    else:
        await update.effective_message.reply_text(
            "Please reply to a sticker for me to upload its PNG."
        )


async def getvidsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = update.effective_message
    chat_id = update.effective_chat.id
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        new_file = bot.get_file(file_id)
        new_file.download("sticker.mp4")
        bot.send_video(chat_id, video=open("sticker.mp4", "rb"))
        os.remove("sticker.mp4")
    else:
        await update.effective_message.reply_text(
            "Please reply to a video sticker to upload its MP4."
        )


async def delsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        context.bot.delete_sticker_from_set(file_id)
        await msg.reply_text("Deleted!")
    else:
        await update.effective_message.reply_text(
            "Please reply to sticker message to del sticker"
        )
            


async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = update.effective_message
    chat_id = update.effective_chat.id

    if msg.reply_to_message and msg.reply_to_message.sticker and msg.reply_to_message.sticker.is_video:
        sticker_file_id = msg.reply_to_message.sticker.file_id
        sticker_file = bot.get_file(sticker_file_id)
        sticker_file.download("sticker.mp4")

        video_file = await bot.convert_file(sticker_file, "video")
        bot.send_video(chat_id, video=video_file)

        os.remove("sticker.mp4")
    else:
        await update.effective_message.reply_text(
            "Please reply to a video sticker for me to get its video."
        )


__mod_name__ = "Stickers"

from MissCutie.modules.language import gs

def get_help(chat):
    return gs(chat, "stickers_help")


STICKERID_HANDLER = DisableAbleCommandHandler("stickerid", stickerid, block=False)
GETSTICKER_HANDLER = DisableAbleCommandHandler("getsticker", getsticker, block=False)
GETVIDSTICKER_HANDLER = DisableAbleCommandHandler("getvidsticker", getvidsticker, block=False)
KANG_HANDLER = DisableAbleCommandHandler("kang", kang, admin_ok=True, block=False)
DEL_HANDLER = DisableAbleCommandHandler("delsticker", delsticker, block=False)
STICKERS_HANDLER = DisableAbleCommandHandler("stickers", cb_sticker, block=False)
VIDEO_HANDLER = DisableAbleCommandHandler("getvideo", video, block=False)
CBSCALLBACK_HANDLER = CallbackQueryHandler(cbs_callback, pattern="cbs_", block=False)

application.add_handler(VIDEO_HANDLER)
application.add_handler(CBSCALLBACK_HANDLER)
application.add_handler(STICKERS_HANDLER)
application.add_handler(STICKERID_HANDLER)
application.add_handler(GETSTICKER_HANDLER)
application.add_handler(GETVIDSTICKER_HANDLER)
application.add_handler(KANG_HANDLER)
application.add_handler(DEL_HANDLER)
