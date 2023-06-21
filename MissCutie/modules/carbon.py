from pyrogram import filters

from MissCutie import pbot
from MissCutie.utils.errors import capture_err
from MissCutie.utils.functions import make_carbon


@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message): 
     if message.reply_to_message: 
         if message.reply_to_message.text: 
             txt = message.reply_to_message.text 
         else: 
             return await message.reply_text("Reply to a TEXT_Message or give some text") 
     else: 
         try: 
             txt = message.text.split(None, 1)[1] 
         except IndexError: 
             return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ.") 
     m = await message.reply_text("Keep Patience Carbon Generating for your text") 
     carbon = await make_carbon(txt) 
     await m.edit_text("Sending Carbon Generated image to you") 
     await pbot.send_photo( 
         message.chat.id, 
         photo=carbon, 
         caption=f"» Requested By :  {message.from_user.mention}", 
     ) 
     await m.delete() 
     carbon.close()


__mod_name__ = "Carbon"

__help__ = """

make a carbon to given text and sending to you.

➥ /carbon *:* Reply any text
 """
