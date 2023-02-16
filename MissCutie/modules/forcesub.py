import logging
import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from MissCutie import BOT_USERNAME as asau
from MissCutie import DRAGONS as SUDO_USERS
from MissCutie import pbot
from MissCutie.modules.sql import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    if chat_db := sql.fs_settings(chat_id):
        channel = chat_db.channel
        chat_member = client.get_chat_member(chat_id, user_id)
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == (client.get_me()).id:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                    # if cb.message.reply_to_message.from_user.id == user_id:
                    # cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f"❗ join our @{channel} channel and press 'unmute me button.",
                        show_alert=True,
                    )
            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ You have been muted by Admins due to some other reason.",
                    show_alert=True,
                )
        elif (
            client.get_chat_member(chat_id, (client.get_me()).id).status
            == "administrator"
        ):
            client.answer_callback_query(
                cb.id,
                text="❗ Warning ! don't press the button when you can talk.",
                show_alert=True,
            )

        else:
            client.send_message(
                chat_id,
                f"❗ **{cb.from_user.mention} is trying to unmute him/her-self but i can't unmute him/her because i am not an admin in this chat add me as admin again.\n",
            )


@pbot.on_message(filters.text & ~filters.private, group=1)
def _check_member(client, message):
    chat_id = message.chat.id
    if chat_db := sql.fs_settings(chat_id):
        user_id = message.from_user.id
        if (
            client.get_chat_member(chat_id, user_id).status
            not in ("administrator", "creator")
            and user_id not in SUDO_USERS
        ):
            channel = chat_db.channel
            try:
                client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                try:
                    sent_message = message.reply_text(
                        f"welcome {message.from_user.mention} 🙏 \n **you haven't joined our @{channel} channel yet**👷 \n \nplease join [our channel](https://t.me/{channel}) and hit the **unmute me** button. \n \n ",
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "join channel",
                                        url=f"https://t.me/{channel}",
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "unmute me",
                                        callback_data="onUnMuteRequest",
                                    )
                                ],
                            ]
                        ),
                    )

                    client.restrict_chat_member(
                        chat_id, user_id, ChatPermissions(can_send_messages=False)
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "😕 **i am not admin here..**\n__give me Ban permissions and retry.. \n#ending fsub...."
                    )

            except ChatAdminRequired:
                client.send_message(
                    chat_id,
                    text=f"😕 **I not an admin of @{channel} channel.**\n__give me admin of that channel and retry.\n#ending fsub....",
                )


@pbot.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator" or user.user.id in SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "")
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                message.reply_text("❌ **force subscribe is disabled successfully.**")
            elif input_str.lower() in ("clear"):
                sent_message = message.reply_text(
                    "**unmuting all members who are muted By me ...**"
                )
                try:
                    for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == (client.get_me()).id:
                            client.unban_chat_member(chat_id, chat_member.user.id)
                            time.sleep(1)
                    sent_message.edit("✅ **unmuted all members who are muted By me.**")
                except ChatAdminRequired:
                    sent_message.edit(
                        "😕 **I am not an admin in this chat.**\n__I can't unmute members because i am not an admin in this chat make me admin with Ban user permission.__"
                    )
            else:
                try:
                    client.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    message.reply_text(
                        f"✅ **force subscribe is enabled**\n__force subscribe is enabled, all the group members have to subscribe this [channel](https://t.me/{input_str}) in order to send messages in this group.",
                        disable_web_page_preview=True,
                    )
                except UserNotParticipant:
                    message.reply_text(
                        f"😕 **not an admin in the channel**\n__I am not an admin in the [channel](https://t.me/{input_str}). add me as a admin in order to enable forcesubscribe.",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    message.reply_text("❗ **invalid channel username.**")
                except Exception as err:
                    message.reply_text(f"❗ **error:** ```{err}```")
        elif sql.fs_settings(chat_id):
            message.reply_text(
                f"✅ **force subscribe is enabled in this chat.**\n__for this [channel](https://t.me/{sql.fs_settings(chat_id).channel})__",
                disable_web_page_preview=True,
            )
        else:
            message.reply_text("❌ **force subscribe is disabled in this chat.**")
    else:
        message.reply_text(
            "❗ **group creator reǫuired**\n__you have to be the group creator to do that.__"
        )


__help__ = f"""
*force subscribe:*
➥ *Abg can mute members who are not subscribed your channel until they subscribe*
➥ `when enabled i will mute unsubscribed members and show them a unmute button. when they pressed the button i will unmute them`
➥ *setup*
*only creator*
➥ [add me in your group as admin](https://t.me/{asau}?startgroup=new)
➥ [add me in your channel as admin](https://t.me/{asau}?startgroup=new)
 
*commmands*
➥ /fsub channel username - `to turn on and 𝚜𝚎𝚝𝚞𝚙 the channel.`
  💡*do this first...*
➥ /fsub - `to get the current settings.`
➥ /fsub disable - `to turn of forcesubscribe..`
  💡`if you disable fsub`, `you need to set again for working` /fsub channel username
  
➥ /fsub clear - `to unmute all members who muted By me.`
"""
__mod_name__ = "F-sub"

