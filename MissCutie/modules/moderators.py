import html
import contextlib
import MissCutie.modules.sql.moderators_sql as sql

from MissCutie import dispatcher
from MissCutie.modules.disable import DisableAbleCommandHandler
from MissCutie.modules.helper_funcs.chat_status import user_admin
from MissCutie.modules.helper_funcs.extraction import extract_user
from MissCutie.modules.log_channel import gloggable


from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.helpers import mention_html


@gloggable
@user_admin
async def mod(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    with contextlib.suppress(BadRequest):
        member = await chat.get_member(user_id)

    if member.status in ("administrator", "creator"):
        await message.reply_text("No need to Modertor an Admin!")
        return ""
    if sql.is_modd(message.chat_id, user_id):
        await message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) is already moderator in {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.mod(message.chat_id, user_id)
    await message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) has been moderator in {chat_title}",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#MODERATOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}")

    return log_message


@gloggable
@user_admin
async def dismod(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = await chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status in ("administrator", "creator"):
        await update.effective_message.reply_text("This Is User Admin")
        return ""
    if not sql.is_modd(message.chat_id, user_id):
        await message.reply_text(
            f"{member.user['first_name']} isn't moderator yet!")
        return ""
    sql.dismod(message.chat_id, user_id)
    await message.reply_text(
        f"{member.user['first_name']} is no longer moderator in {chat_title}.")
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNMODERTOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}")

    return log_message


@user_admin
async def modd(update: Update):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "The following users are Moderator.\n"
    modd_users = sql.list_modd(message.chat_id)
    for i in modd_users:
        member = chat.get_member(int(i.user_id))
        msg += f"{member.user['first_name']}\n"
    if msg.endswith("moderator.\n"):
        await message.reply_text(f"No users are Moderator in {chat_title}.")
        return ""
    await message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def modr(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = await chat.get_member(user_id)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    if sql.is_modd(message.chat_id, user_id):
        await message.reply_text(
            f"{member.user['first_name']} is an moderator user.")
    else:
        await message.reply_text(
            f"{member.user['first_name']} is not an moderator user.")


__mod_name__ = "Moderation"

dispatcher.add_handler(DisableAbleCommandHandler("addmod", mod))
dispatcher.add_handler(DisableAbleCommandHandler("rmmod", dismod))
dispatcher.add_handler(DisableAbleCommandHandler("modlist", modd))
dispatcher.add_handler(DisableAbleCommandHandler("modcheck", modr))



__help__ = """
Sometimes, you don't trust but want to make user manager of your group then you can make him/her moderator.
Maybe not enough to make them admin, but you might be ok with ban, mute, and warn not.
That's what modcheck are for - mod of trustworthy users to allow to manage your group.

*Admins commands*:

➥ /modcheck: Check a user's modcheck status in this chat.
➥ /mod: mod of a user can ban, mute, and warn.
➥ /unmod: Unmod of a user. They will now can't ban, mute and warn anyone.
➥ /modlist: List all mod users.
"""

__command_list__ = [
    "addmod",
    "rmmod",
    "modlist",
    "modcheck",
]
