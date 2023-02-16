import asyncio
from platform import python_version as pyver

from pyrogram import __version__ as pver
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram import __version__ as lver
from telethon import __version__ as tver

from MissCutie import SUPPORT_CHAT, pbot,BOT_USERNAME, OWNER_ID

PHOTO = [
    "https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg",
    "https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg",
    "https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg",
    "https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg",
    "https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg",
]

saif = [
    [
        InlineKeyboardButton(text="Owner", url=f"https://t.me/PrinceXofficial"),
        InlineKeyboardButton(text="Support", url=f"https://t.me/{SUPPORT_CHAT}"),
    ],
    [
        InlineKeyboardButton(
            text="Add Me Your Group",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
        ),
    ],
]

lol = "https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg"


@pbot.on_message(filters.command("alive"))
async def restart(client, m: Message):
    await m.delete()
    accha = await m.reply("🤫")
    await asyncio.sleep(1.5)
    await accha.edit("🥱")
    await asyncio.sleep(1.5)
    await accha.edit("⏳️")
    await asyncio.sleep(1.5)
    await accha.edit("aliving..")
    await asyncio.sleep(0.5)
    await accha.edit("aliving...")
    await accha.delete()
    await asyncio.sleep(0.5)
    await m.reply_photo(
        lol,
        caption=f"""**Hey, i am [MissCutie](f"t.me/{BOT_USERNAME}")**
  ➥ **My Owner :** @PrinceXofficial
  
  ➥ **Library Version :** `{lver}`
  
  ➥ **Telethon Version :** `{tver}`
  
  ➥ **Pyrogran Version :** `{pver}`
  
  ➥ **Python Version :** `{pyver()}`
""",
        reply_markup=InlineKeyboardMarkup(saif),
    )
