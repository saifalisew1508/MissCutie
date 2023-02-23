from platform import python_version as y

from pyrogram import __version__ as z
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import __version__ as o
from telethon import __version__ as s

from MissCutie import OWNER_ID, BOT_NAME, dispatcher
from MissCutie import pbot as client

saif = "https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg"


@client.on_message(filters.command(["repo", "source"]))
async def repo(client, message):
    await message.reply_photo(
        photo=saif,
        caption=f"""**Hey {message.from_user.mention()},\n\ni am [{dispatcher.bot.first_name}](t.me/{dispatcher.bot.username})**

**➥ My Developer :** @PrinceXofficial
**➥ Python Version :** `{y()}`
**➥ Library Version :** `{o}` 
**➥ Telethon Version :** `{s}` 
**➥ Pyrogram Version :** `{z}`

**{BOT_NAME} source is now public and now you can make your own bot.**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Developer",
                        url="t.me/PrinceXofficial",
                    ),
                    InlineKeyboardButton(
                        "Source",
                        url="https://github.com/saifalisew1508/MissCutieRobot",
                    ),
                ]
            ]
        ),
    )


__mod_name__ = "Repo"
_help__ = """ /repo to get repo 
             /Source to get repo
"""
