from pyrogram import filters
from MissCutie import DEV_USERS, arq, pbot
from MissCutie.utils.errors import capture_err
from MissCutie.utils.permissions import adminsOnly
from MissCutie.modules.mongo.nsfw_mongo import is_nsfw_on, nsfw_off, nsfw_on


async def get_file_id_from_message(message):
    file_id = None
    if isinstance(message, types.Message):
        file_types = ["document", "photo", "sticker", "animation", "video"]
        for file_type in file_types:
            file_attr = getattr(message, file_type, None)
            if file_attr:
                if file_type == "document" and int(file_attr.file_size) > 3145728:
                    continue
                file_id = file_attr.file_id
                break
    return file_id


@pbot.on_message(
    (
        filters.document
        | filters.photo
        | filters.sticker
        | filters.animation
        | filters.video
    )
    & ~filters.private,
    group=8,
)
@capture_err
async def detect_nsfw(_, message):
    if not await is_nsfw_on(message.chat.id):
        return
    if not message.from_user:
        return
    file_id = await get_file_id_from_message(message)
    if not file_id:
        return
    try:
        file_info = await pbot.get_file(file_id)
        file_path = await pbot.download_media(file_info.file_path)
        results = await arq.nsfw_scan(file=file_path)
        if not results.ok:
            return
        results = results.result
        os.remove(file_path)
        nsfw = results.is_nsfw
        if message.from_user.id in DEV_USERS:
            return
        if not nsfw:
            return
        await message.delete()
        await message.reply_text(
            f"""
            **NSFW Image Detected & Deleted Successfully!**
            --------------------------------------------
            **User:** {message.from_user.mention} [`{message.from_user.id}`]
            **Safe:** `{results.neutral} %`
            **Porn:** `{results.porn} %`
            **Adult:** `{results.sexy} %`
            **Hentai:** `{results.hentai} %`
            **Drawings:** `{results.drawings} %`
            --------------------------------------------
            __Powered by @BotXNews__
            """
        )
    except Exception:
        return


@pbot.on_message(filters.command(["nsfwscan", "nsfwscan@MissCutieRobot"]))
@capture_err
async def nsfw_scan_command(_, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to an image/document/sticker/animation to scan it.")
        return
    reply = message.reply_to_message
    if (
        not reply.document
        and not reply.photo
        and not reply.sticker
        and not reply.animation
        and not reply.video
    ):
        await message.reply_text("Reply to an image/document/sticker/animation to scan it.")
        return
    m = await message.reply_text("Scanning")
    file_id = await get_file_id_from_message(reply)
    if not file_id:
        return await m.edit("Something wrong happened.")
    try:
        file_info = await pbot.get_file(file_id)
        file_path = await pbot.download_media(file_info.file_path)
        results = await arq.nsfw_scan(file=file_path)
        os.remove(file_path)
        if not results.ok:
            return await m.edit(results.result)
        results = results.result
        await m.edit(
            f"""
            **Neutral:** `{results.neutral} %`
            **Porn:** `{results.porn} %`
            **Hentai:** `{results.hentai} %`
            **Sexy:** `{results.sexy} %`
            **Drawings:** `{results.drawings} %`
            **NSFW:** `{results.is_nsfw}`
            """
        )
    except Exception:
        return


@pbot.on_message(
    filters.command(["antinsfw", "antinsfw@MissCutieRobot"]) & ~filters.private
)
@adminsOnly("can_change_info")
async def nsfw_enable_disable(_, message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /antinsfw [on/off]")
        return
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status in ("on", "yes"):
        await nsfw_on(chat_id)
        await message.reply_text("Enabled AntiNSFW System. I will Delete Messages Containing Inappropriate Content.")
    elif status in ("off", "no"):
        await nsfw_off(chat_id)
        await message.reply_text("Disabled AntiNSFW System.")
    else:
        await message.reply_text("Unknown Suffix, Use /antinsfw [on/off]")
