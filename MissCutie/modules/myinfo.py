import asyncio
import datetime
import re
from datetime import datetime

from telethon import custom, events

from MissCutie import telethn as bot
from MissCutie import telethn as tgbot
from MissCutie.events import register
from MissCutie import BOT_NAME

edit_time = 5
""" =======================𝑴𝒊𝒔𝒔𝑪𝒖𝒕𝒊𝒆 𝑹𝒐𝒃𝒐𝒕====================== """
file2 = "https://graph.org/file/eec70867b0bbef60d6fc1.jpg"

""" =======================𝑴𝒊𝒔𝒔𝑪𝒖𝒕𝒊𝒆 𝑹𝒐𝒃𝒐𝒕====================== """


@register(pattern="/myinfo")
async def proboyx(event):
    await event.get_chat()
    datetime.utcnow()
    firstname = event.sender.first_name
    button = [[custom.Button.inline("Information", data="informations")]]
    on = await bot.send_file(
        event.chat_id,
        file=file2,
        caption=f"Hey {firstname}, \nClick on the button below to get info about you \n\n**Note :** Start Bot in PM first",
        buttons=button,
    )


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"information")))
async def callback_query_handler(event):
    try:
        boy = event.sender_id
        PRO = await bot.get_entity(boy)
        LILIE = "Powered By @MissCutie_Support\n\n"
        LILIE += f"First Name: {PRO.first_name} \n"
        LILIE += f"Last Name: {PRO.last_name}\n"
        LILIE += f"You Bot : {PRO.bot} \n"
        LILIE += f"Restricted : {PRO.restricted} \n"
        LILIE += f"User ID: {boy}\n"
        LILIE += f"Username : {PRO.username}\n"
        await event.answer(LILIE, alert=True)
    except Exception as e:
        await event.reply(f"{e}")

