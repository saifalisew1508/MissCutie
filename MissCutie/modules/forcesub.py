import logging

from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import RPCError
from pyrogram.errors.exceptions import (
    ChannelPrivate,
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MissCutie import BOT_ID, DEV_USERS, pbot
from MissCutie.modules.sql import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
def _onUnMuteRequest(client: Client, cb):
    try:
        user_id = cb.from_user.id
        chat_id = cb.message.chat.id
    except AttributeError:
        return
    if chat_db := sql.fs_settings(chat_id):
        channel = chat_db.channel
        try:
            chat_member = client.get_chat_member(chat_id, user_id)
        except RPCError:
            return
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == BOT_ID:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f"❗ Join our @{channel} channel and press 'UnMute Me' button.",
                        show_alert=True,
                    )
                except ChannelPrivate:
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()

            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ You have been muted by admins due to some other reason.",
                    show_alert=True,
                )
        elif client.get_chat_member(chat_id, BOT_ID).status != "administrator":
            client.send_message(
                chat_id,
                f"❗ **{cb.from_user.mention} is trying to UnMute himself but I can't unmute him because I am not an admin in this chat. Add me as admin again.**\n__#Leaving this chat...__",
            )

        else:
            client.answer_callback_query(
                cb.id,
                text="❗ Warning! Don't press the button when you can talk.",
                show_alert=True,
            )


@pbot.on_edited_message(filters.text & ~filters.private, group=1)
def _check_member(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_db := sql.fs_settings(chat_id):
        try:
            user_id = message.from_user.id
        except AttributeError:
            return
        try:
            if client.get_chat_member(chat_id, user_id).status not in ("administrator", "creator"):
                channel = chat_db.channel
                try:
                    client.get_chat_member(channel, user_id)
                except UserNotParticipant:
                    try:
                        sent_message = message.reply_text(
                            f"Welcome {message.from_user.mention} 🙏 \n **You haven't joined our @{channel} Channel yet** 😭 \n \nPlease Join [Our Channel](https://telegram.dog/{channel}) and hit the **UNMUTE ME** Button. \n \n ",
                            disable_web_page_preview=True,
                            reply_markup=InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton(
                                        "Join Channel",
                                        url=f"https://telegram.dog/{channel}",
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "UnMute Me",
                                        callback_data="onUnMuteRequest",
                                    )
                                ],
                            ]),
                        )

                        client.restrict_chat_member(
                            chat_id, user_id, ChatPermissions(can_send_messages=False)
                        )
                    except ChatAdminRequired:
                        sent_message.edit(
                            "❗ **I am not admin here..**\n__Give me ban permissions and retry.. \n#Ending FSub...__"
                        )
                    except RPCError:
                        return

                except ChatAdminRequired:
                    client.send_message(
                        chat_id,
                        text=f"❗ **I am not an admin of @{channel} channel.**\n__Give me admin of that channel and retry.\n#Ending FSub...__",
                    )
                except ChannelPrivate:
                    return
        except AttributeError:
            return


@pbot.on_message(filters.command(["forcesubscribe", "forcesub", "forcesub@MissCutieRobot", "forcesubscribe@MissCutieRobot"]) & ~filters.private)
def config(client: Client, message):
    chat_id = message.chat.id
    if len(message.command) > 1:
        input_str = message.command[1]
        input_str = input_str.replace("@", "")
        if input_str.lower() in ("off", "no", "disable"):
            sql.disapprove(chat_id)
            message.reply_text("❌ **Force Subscribe is Disabled Successfully.**")
        elif input_str.lower() == "clear":
            sent_message = message.reply_text(
                "**Unmuting all members who are muted by me...**"
            )
            try:
                for chat_member in client.get_chat_members(message.chat.id, filter="restricted"):
                    if chat_member.restricted_by.id == BOT_ID:
                        client.unban_chat_member(chat_id, chat_member.user.id)
                        time.sleep(1)
                sent_message.edit("✅ **Unmuted all members who are muted by me.**")
            except ChatAdminRequired:
                sent_message.edit(
                    "❗ **I am not an admin in this chat.**\n__I can't unmute members because I am not an admin in this chat. Make me admin with ban user permission.__"
                )
        else:
            try:
                client.get_chat_member(input_str, "me")
                sql.add_channel(chat_id, input_str)
                message.reply_text(
                    f"✅ **Force Subscribe is Enabled**\n__Force Subscribe is enabled. All the group members have to subscribe to this [channel](https://telegram.dog/{input_str}) in order to send messages in this group.__",
                    disable_web_page_preview=True,
                )
            except UserNotParticipant:
                message.reply_text(
                    f"❗ **Not an Admin in the Channel**\n__I am not an admin in the [channel](https://telegram.dog/{input_str}). Add me as an admin in order to enable ForceSubscribe.__",
                    disable_web_page_preview=True,
                )
            except (UsernameNotOccupied, PeerIdInvalid):
                message.reply_text("❗ **Invalid Channel Username.**")
            except Exception as err:
                message.reply_text(f"❗ **ERROR:** ```{err}```")
    elif sql.fs_settings(chat_id):
        message.reply_text(
            f"✅ **Force Subscribe is enabled in this chat.**\n__For this [Channel](https://telegram.dog/{sql.fs_settings(chat_id).channel})__",
            disable_web_page_preview=True,
        )
    else:
        message.reply_text("❌ **Force Subscribe is disabled in this chat.**")


__help__ = """
*Force Subscribe*:
- @MissCutieRobot can mute members who are not subscribed to your channel until they subscribe.
- When enabled, I will mute unsubscribed members and show them an unmute button. When they press the button, I will unmute them.

*Setup*:
1) First of all, add me in the group as an admin with ban users permission and add me as an admin in the channel as well.
   Note: Only the creator of the group can set me up, and I will not allow force subscribe again if not done so.

*Commands*:
➥ /forcesubscribe: Get the current settings.
➥ /forcesubscribe <no/off/disable>: Turn off ForceSubscribe.
➥ /forcesubscribe <channel username>: Turn on and set up the channel.
➥ /forcesubscribe clear: Unmute all members who are muted by me.

Note: /forcesub is an alias of /forcesubscribe.
"""
__mod_name__ = "ForceSub"
