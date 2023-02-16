from datetime import datetime

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from MissCutie import OWNER_ID as owner_id
from MissCutie import SUPPORT_CHAT as log
from MissCutie import pbot as Client
from MissCutie.utils.errors import capture_err


def content(msg: Message) -> [None, str]:
    text_to_return = msg.text

    if msg.text is None:
        return None
    if " " in text_to_return:
        try:
            return msg.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None


@Client.on_message(filters.command("bug"))
@capture_err
async def bug(_, msg: Message):
    if msg.chat.username:
        chat_username = f"@{msg.chat.username}/`{msg.chat.id}`"
    else:
        chat_username = f"Private Group/`{msg.chat.id}`"

    bugs = content(msg)
    user_id = msg.from_user.id
    mention = (
        "[" + msg.from_user.first_name + "](tg://user?id=" + str(msg.from_user.id) + ")"
    )
    datetimes_fmt = "%d-%m-%Y"
    datetimes = datetime.utcnow().strftime(datetimes_fmt)

    thumb = "https://telegra.ph/file/ce00e06eeeec173a51ba5.mp4"

    bug_report = f"""
**#bug : ** **tg://user?id={owner_id}**

**reported By : ** **{mention}**
**user id : ** **{user_id}**
**chat : ** **{chat_username}**

**bug : ** **{bugs}**

**event stamp : ** **{datetimes}**"""

    if msg.chat.type == "private":
        await msg.reply_text("<b>➥ This command only for groups.</b>")
        return

    if user_id == owner_id:
        if bugs:
            await msg.reply_text(
                "<b>➥ Are you comedy me 🤣?, You are owner of the bot.</b>",
            )
            return
        else:
            await msg.reply_text("LuL OWNER!")
    elif user_id != owner_id:
        if bugs:
            await msg.reply_text(
                f"<b>Bug report : {bugs}</b>\n\n"
                "<b>➥ Bug successfully reported at support chat !</b>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("• Close •", callback_data=f"close_reply")]]
                ),
            )
            await Client.send_photo(
                log,
                photo=thumb,
                caption=f"{bug_report}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("• View Bug •", url=f"{msg.link}")],
                        [
                            InlineKeyboardButton(
                                "• close •", callback_data="close_send_photo"
                            )
                        ],
                    ]
                ),
            )
        else:
            await msg.reply_text(
                f"<b>➥ No Bug To Report !</b>",
            )


@Client.on_callback_query(filters.regex("close_reply"))
async def close_reply(msg, CallbackQuery):
    await CallbackQuery.message.delete()


@Client.on_callback_query(filters.regex("close_send_photo"))
async def close_send_photo(_, CallbackQuery):
    is_Admin = await Client.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not is_Admin.can_delete_messages:
        return await CallbackQuery.answer(
            "You haven't right to close this.", show_alert=True
        )
    else:
        await CallbackQuery.message.delete()


__help__ = """
*For reporting any bug*
 ➥ /bug *:* To rport a bug at support chat.
"""
__mod_name__ = "Bugs"
