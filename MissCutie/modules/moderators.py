import html
import contextlib
import MissCutie.modules.sql.moderators_sql as sql

from MissCutie import application
from MissCutie.modules.disable import DisableAbleCommandHandler
from MissCutie.modules.helper_funcs.chat_status import check_admin
from MissCutie.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from MissCutie.modules.log_channel import loggable
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatMemberStatus, ChatID, ChatType
from telegram.error import BadRequest
from telegram.helpers import mention_html


@loggable
@check_admin(permission="can_promote_members", is_both=True)
async def mod(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = await extract_user(message, context, args)
    member = await chat.get_member(user_id)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""

    try:
        user_member = await chat.get_member(user_id)
    except:
        return

    if user_member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
        await message.reply_text("No need to Modertor an Admin!")
        return ""
    if sql.is_modd(message.chat_id, user_id):
        await message.reply_text(
            f"[{member.user.first_name}](tg://user?id={member.user.id}) is already moderator in {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.mod(message.chat_id, user_id)
    await message.reply_text(
        f"[{member.user.first_name}](tg://user?id={member.user.id}) has been moderator in {chat_title}",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#MODERATOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}")

    return log_message


@loggable
@check_admin(permission="can_promote_members", is_both=True)
async def dismod(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = await extract_user(message, context, args)
    member = await chat.get_member(user_id)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        user_member = await chat.get_member(user_id)
    except:
        return

    if user_member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
        await update.effective_message.reply_text("This Is User Admin")
        return ""
    if not sql.is_modd(message.chat_id, user_id):
        await message.reply_text(
            f"[{member.user.first_name}](tg://user?id={member.user.id}) isn't moderator yet!")
        return ""
    sql.dismod(message.chat_id, user_id)
    await message.reply_text(
        f"{member.user.first_name} is no longer moderator in {chat_title}.")
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNMODERTOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}")

    return log_message


@check_admin(permission="can_promote_members", is_both=True)
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


async def modr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = await extract_user(message, context, args)
    member = await chat.get_member(user_id)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    if sql.is_modd(message.chat_id, user_id):
        await message.reply_text(
            f"{member.user.first_name} is a moderator user.")
    else:
        await message.reply_text(
            f"{member.user.first_name} is not a moderator user.")

        

ADD_MOD_HANDLER = DisableAbleCommandHandler("addmod", mod, block=False)
REMOVE_MOD_HANDLER = DisableAbleCommandHandler("remmod", dismod, block=False)
MOD_LIST_HANDLER = DisableAbleCommandHandler("modlist", modd, block=False)
CHECK_MOD_HANDLER = DisableAbleCommandHandler("modcheck", modr, block=False)


application.add_handler(ADD_MOD_HANDLER)
application.add_handler(REMOVE_MOD_HANDLER)
application.add_handler(MOD_LIST_HANDLER)
application.add_handler(CHECK_MOD_HANDLER)

__command_list__ = [
    "addmod",
    "rmmod",
    "modlist",
    "modcheck",
]

__mod_name__ = "Moderators"

from MissCutie.modules.language import gs
def get_help(chat):
    return gs(chat, "moderators_help")
