import logging
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, Filters, run_async
from telegram.error import ChatMigrated, Unauthorized

from MissCutie import OWNER_ID, BOT_ID, BOT_NAME, BOT_USERNAME
from MissCutie.modules.sql import forceSubscribe_sql as sql

@run_async
def on_unmute_request(update, context):
    user_id = update.callback_query.from_user.id
    chat_id = update.callback_query.message.chat_id
    chat_db = sql.fs_settings(chat_id)

    if chat_db:
        channel = chat_db.channel
        chat_member = context.bot.get_chat_member(chat_id, user_id)

        if chat_member.restricted_by:
            if chat_member.restricted_by.id == BOT_ID:
                try:
                    context.bot.get_chat_member(channel, user_id)
                    context.bot.unban_chat_member(chat_id, user_id)
                    update.callback_query.message.delete()
                except Unauthorized:
                    context.bot.answer_callback_query(
                        update.callback_query.id,
                        text=f"❗ Join our @{channel} channel and press 'UnMute Me' button.",
                        show_alert=True,
                    )
            else:
                context.bot.answer_callback_query(
                    update.callback_query.id,
                    text="❗ You have been muted by admins due to some other reason.",
                    show_alert=True,
                )
        else:
            if (
                not context.bot.get_chat_member(chat_id, BOT_ID).status
                == "administrator"
            ):
                context.bot.send_message(
                    chat_id,
                    f"❗ **{update.callback_query.from_user.mention} is trying to UnMute himself but I can't unmute him because I am not an admin in this chat. Add me as an admin again.**\n__#Leaving this chat...__",
                )
            else:
                context.bot.answer_callback_query(
                    update.callback_query.id,
                    text="❗ Warning! Don't press the button when you can talk.",
                    show_alert=True,
                )

@run_async
def check_member(update, context):
    chat_id = update.message.chat_id
    chat_db = sql.fs_settings(chat_id)

    if chat_db:
        user_id = update.message.from_user.id

        if (
            not context.bot.get_chat_member(chat_id, user_id).status
            in ("administrator", "creator")
            and user_id not in OWNER_ID
        ):
            channel = chat_db.channel

            try:
                context.bot.get_chat_member(channel, user_id)
            except Unauthorized:
                try:
                    sent_message = update.message.reply_text(
                        f"Welcome {update.message.from_user.mention} 🙏 \n **You haven't joined our @{channel} Channel yet** 😭 \n \nPlease Join [Our Channel](https://t.me/{channel}) and hit the **UNMUTE ME** Button. \n \n ",
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "Join Channel",
                                        url=f"https://t.me/{channel}",
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "UnMute Me", callback_data="onUnMuteRequest"
                                    )
                                ],
                            ]
                        ),
                    )
                    context.bot.restrict_chat_member(
                        chat_id, user_id, can_send_messages=False
                    )
                except Unauthorized:
                    sent_message.edit_text(
                        "❗ **MissCutie is not admin here..**\n__Give me ban permissions and retry.. \n#Ending FSub...__"
                    )
            except Unauthorized:
                context.bot.send_message(
                    chat_id,
                    text=f"❗ **I am not an admin of @{channel} channel.**\n__Give me admin of that channel and retry.\n#Ending FSub...__",
                )

def config(update, context):
    user = context.bot.get_chat_member(update.message.chat_id, update.message.from_user.id)

    if user.status == "creator" or user.user.id in OWNER_ID:
        chat_id = update.message.chat_id

        if len(context.args) > 0:
            input_str = context.args[0]
            input_str = input_str.replace("@", "")

            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                update.message.reply_text("❌ **Force Subscribe is Disabled Successfully.**")
            elif input_str.lower() == "clear":
                sent_message = update.message.reply_text(
                    "**Unmuting all members who are muted by me...**"
                )
                try:
                    for chat_member in context.bot.get_chat_members(
                        update.message.chat_id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == BOT_ID:
                            context.bot.unban_chat_member(
                                chat_id, chat_member.user.id
                            )
                            time.sleep(1)
                    sent_message.edit_text(
                        "✅ **UnMuted all members who are muted by me.**"
                    )
                except Unauthorized:
                    sent_message.edit_text(
                        "❗ **I am not an admin in this chat.**\n__I can't unmute members because I am not an admin in this chat. Make me admin with ban user permission.__"
                    )
            else:
                try:
                    context.bot.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    update.message.reply_text(
                        f"✅ **Force Subscribe is Enabled**\n__Force Subscribe is enabled, all the group members have to subscribe to this [channel](https://t.me/{input_str}) in order to send messages in this group.__",
                        disable_web_page_preview=True,
                    )
                except Unauthorized:
                    update.message.reply_text(
                        f"❗ **Not an Admin in the Channel**\n__I am not an admin in the [channel](https://t.me/{input_str}). Add me as an admin in order to enable ForceSubscribe.__",
                        disable_web_page_preview=True,
                    )
                except Exception as err:
                    update.message.reply_text(f"❗ **ERROR:** ```{err}```")
        else:
            if sql.fs_settings(chat_id):
                update.message.reply_text(
                    f"✅ **Force Subscribe is enabled in this chat.**\n__For this [Channel](https://t.me/{sql.fs_settings(chat_id).channel})__",
                    disable_web_page_preview=True,
                )
            else:
                update.message.reply_text("❌ **Force Subscribe is disabled in this chat.**")
    else:
        update.message.reply_text(
            "❗ **Group Creator Required**\n__You have to be the group creator to do that.__"
        )

def get_help(chat):
    # Assuming gs is a function from MissCutie.modules.language
    return gs(chat, "force_subscribe")

# Define your handlers
on_unmute_request_handler = CallbackQueryHandler(on_unmute_request, pattern='^onUnMuteRequest$')
check_member_handler = MessageHandler(Filters.text & ~Filters.private, check_member)
config_handler = CommandHandler(["forcesubscribe", "fsub"], config, pass_args=True)

# Add handlers to your updater
updater.add_handler(on_unmute_request_handler)
updater.add_handler(check_member_handler)
updater.add_handler(config_handler)

__mod_name__ = "Force Subscribe"
