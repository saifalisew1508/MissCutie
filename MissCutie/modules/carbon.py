from pyrogram import filters

from MissCutie import pbot
from MissCutie.utils.errors import capture_err
from MissCutie.utils.functions import make_carbon


@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if not message.reply_to_message:
        return await message.reply_text("`Reply to a text to generate Carbon.`")
    if not message.reply_to_message.text:
        return await message.reply_text("`Reply to a text to generate Carbon.`")
    m = await message.reply_text("😴`Generating Carbon...`")
    carbon = await make_carbon(message.reply_to_message.text)
    await m.edit("`Uploading Carbon Photo...`")
    await pbot.send_photo(message.chat.id, carbon)
    await m.delete()
    carbon.close()


__mod_name__ = "Carbon"

__help__ = """

make a carbon to given text and sending to you.

➥ /carbon *:* Reply any text
 """
