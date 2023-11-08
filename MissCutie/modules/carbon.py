from pyrogram import filters

from MissCutie import pyroclient
from MissCutie.utils.errors import capture_err
from MissCutie.utils.functions import make_carbon


@pyroclient.on_message(filters.command("carbon"))
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
             return await message.reply_text("Reply to a TEXT.message or give me some text\n Example : /carbon <@MissCutieRobot/>.") 
     m = await message.reply_text("Keep Patience Carbon Generating for your text\n Example : /carbon <@MissCutieRobot/>") 
     carbon = await make_carbon(txt) 
     await m.edit_text("Sending Carbon Generated image to you") 
     await pyroclient.send_photo( 
         message.chat.id, 
         photo=carbon, 
         caption=f"» Requested By :  {message.from_user.mention}", 
     ) 
     await m.delete() 
     carbon.close()
