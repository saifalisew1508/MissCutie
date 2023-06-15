"""
from pyrogram import filters, Client
from pyrogram.errors import UserAlreadyParticipant, UserIsBlocked
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest

from MissCutie import app
from MissCutie.utils.ratelimiter import ratelimiter
from MissCutie.utils.errors import capture_err


@capture_err
@app.on_chat_join_request(filters.group)
async def approve_join_chat(c: Client, m: ChatJoinRequest):
    try:
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Approve", callback_data=f"approve_{m.chat.id}"),
                    InlineKeyboardButton(text="Reject", callback_data=f"declined_{m.chat.id}"),
                ]
            ]
        )
        await c.send_message(
            m.chat.id,
            "New Join Request",
            disable_web_page_preview=True,
            reply_markup=markup,
        )
    except UserIsBlocked:
        await m.decline()


@app.on_callback_query(filters.regex(r"^approve"))
@ratelimiter
async def approve_chat(c, q):
    i, chat = q.data.split("_")
    try:
        await q.message.edit("Yeayy, selamat kamu bisa bergabung di Channel Reborn...")
        await c.approve_chat_join_request(chat, q.from_user.id)
    except UserAlreadyParticipant:
        await q.message.edit("Kamu sudah di acc join grup, jadi ga perlu menekan button.")
    except Exception as err:
        await q.message.edit(err)


@app.on_callback_query(filters.regex(r"^declined"))
@ratelimiter
async def decline_chat(c, q):
    i, chat = q.data.split("_")
    try:
        await q.message.edit("Yahh, kamu ditolak join channel. Biasakan rajin membaca yahhh..")
        await c.decline_chat_join_request(chat, q.from_user.id)
    except UserAlreadyParticipant:
        await q.message.edit("Kamu sudah di acc join grup, jadi ga perlu menekan button.")
    except Exception as err:
        await q.message.edit(err)
"""
