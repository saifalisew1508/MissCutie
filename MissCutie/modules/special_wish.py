from telethon import Button

from MissCutie import telethn as tbot
from MissCutie.events import register

MORNING_PHOTO = "https://te.legra.ph/file/7a18675abd9b75230735d.mp4"
NIGHT_PHOTO = "https://te.legra.ph/file/4e959d8f074bef7061463.mp4"
MORNING_QUOTE = f" Welcome this beautiful morning with a smile on your face. I hope you'll have a great day today. Wishing you a very good morning! {event.sender.first_name}"
NIGHT_QUOTE = f"Good night I hope tomorrow is the best day in your life. {event.sender.first_name}"


BUTTON = [
    [
        InlineKeyboardButton(
            text="Contact Me",
            url=f"https://t.me/MissCutieRobot",
        ),
    ],
]


@register(pattern=("Good morning"))
async def awake(event):
    await tbot.send_file(event.chat_id, MORNING_PHOTO, caption=MORNING_QUOTE, buttons=BUTTON)



@register(pattern=("Good Night"))
async def awake(event):
    await tbot.send_file(event.chat_id, NIGHT_PHOTO, caption=NIGHT_QUOTE, buttons=BUTTON)
