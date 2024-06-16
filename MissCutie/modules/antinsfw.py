from os import remove

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import MessageEntityType

from Database.mongodb.toggle_mongo import is_nsfw_on, nsfw_off, nsfw_on
from MissCutie import BOT_USERNAME, DRAGONS
from MissCutie.utils.state import arq
from MissCutie.utils.admins import can_restrict
from MissCutie.utils.errors import capture_err


async def get_file_id_from_message(message):
    file_id = None
    if message.document:
        if int(message.document.file_size) > 3145728:
            return
        mime_type = message.document.mime_type
        if mime_type not in ("image/png", "image/jpeg"):
            return
        file_id = message.document.file_id

    if message.sticker:
        if message.sticker.is_animated:
            if not message.sticker.thumb:
                return
            file_id = message.sticker.thumb.file_id
        else:
            file_id = message.sticker.file_id

    if message.photo:
        file_id = message.photo[-1].file_id

    if message.animation:
        if not message.animation.thumb:
            return
        file_id = message.animation.thumb.file_id

    if message.video:
        if not message.video.thumb:
            return
        file_id = message.video.thumb.file_id
    return file_id


@capture_err
async def detect_nsfw(update: Update, context: CallbackContext):
    message = update.effective_message
    if not await is_nsfw_on(message.chat_id):
        return
    if not message.from_user:
        return
    file_id = await get_file_id_from_message(message)
    if not file_id:
        return
    file = await context.bot.get_file(file_id)
    file_path = file.file_path
    file.download(custom_path=file_path)
    
    try:
        results = await arq.nsfw_scan(file=file_path)
    except Exception:
        return
    if not results.ok:
        return
    results = results.result
    remove(file_path)
    nsfw = results.is_nsfw
    if message.from_user.id in DRAGONS:
        return
    if not nsfw:
        return
    try:
        await message.delete()
    except Exception:
        return
    await message.reply_text(
        f"""
**🔞 NSFW Image Detected & Deleted Successfully!**

**✪ User:** {message.from_user.mention_html()} [`{message.from_user.id}`]
**✪ Safe:** `{results.neutral} %`
**✪ Porn:** `{results.porn} %`
**✪ Adult:** `{results.sexy} %`
**✪ Hentai:** `{results.hentai} %`
**✪ Drawings:** `{results.drawings} %`
""",
        parse_mode="HTML"
    )


@capture_err
async def nsfw_scan_command(update: Update, context: CallbackContext):
    message = update.effective_message
    if not message.reply_to_message:
        await message.reply_text(
            "Reply to an image/document/sticker/animation to scan it."
        )
        return
    reply = message.reply_to_message
    if (
        not reply.document
        and not reply.photo
        and not reply.sticker
        and not reply.animation
        and not reply.video
    ):
        await message.reply_text(
            "Reply to an image/document/sticker/animation to scan it."
        )
        return
    m = await message.reply_text("Scanning")
    file_id = await get_file_id_from_message(reply)
    if not file_id:
        return await m.edit_text("Something wrong happened.")
    file = await context.bot.get_file(file_id)
    file_path = file.file_path
    file.download(custom_path=file_path)
    
    try:
        results = await arq.nsfw_scan(file=file_path)
    except Exception:
        return
    remove(file_path)
    if not results.ok:
        return await m.edit_text(results.result)
    results = results.result
    await m.edit_text(
        f"""
**➢ Neutral:** `{results.neutral} %`
**➢ Porn:** `{results.porn} %`
**➢ Hentai:** `{results.hentai} %`
**➢ Sexy:** `{results.sexy} %`
**➢ Drawings:** `{results.drawings} %`
**➢ NSFW:** `{results.is_nsfw}`
"""
    )


@can_restrict
async def nsfw_enable_disable(update: Update, context: CallbackContext):
    message = update.effective_message
    if len(context.args) != 1:
        await message.reply_text("Usage: /antinsfw [on/off]")
        return
    status = context.args[0].strip().lower()
    chat_id = message.chat_id
    if status in ("on", "yes"):
        if await is_nsfw_on(chat_id):
            await message.reply_text("Antinsfw is already enabled.")
            return
        await nsfw_on(chat_id)
        await message.reply_text(
            "Enabled AntiNSFW System. I will Delete Messages Containing Inappropriate Content."
        )
    elif status in ("off", "no"):
        if not await is_nsfw_on(chat_id):
            await message.reply_text("Antinsfw is already disabled.")
            return
        await nsfw_off(chat_id)
        await message.reply_text("Disabled AntiNSFW System.")
    else:
        await message.reply_text("Unknown Suffix, Use /antinsfw [on/off]")
