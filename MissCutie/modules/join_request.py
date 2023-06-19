import re
import html

from telegram.ext import (
    ChatJoinRequestHandler,
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    filters,
    MessageHandler,
)
from telegram.constants import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.helpers import mention_html


from MissCutie import application
from MissCutie.modules.helper_funcs.chat_status import check_admin
from MissCutie.modules.log_channel import loggable


async def chat_join_req(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    user = update.chat_join_request.from_user
    chat = update.chat_join_request.chat
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                            "✅ Approve", callback_data="cb_approve={}".format(user.id)
                    ),
                    InlineKeyboardButton(
                            "❌ Decline", callback_data="cb_decline={}".format(user.id)
                    ),
                ]
            ]
    )
    await bot.send_message(
            chat.id,
            "{} wants to join {}".format(
                    mention_html(user.id, user.first_name), chat.title or "this chat"
            ),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
    )


@check_admin(permission="can_invite_users", is_both=True)
@loggable
async def approve_joinReq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    match = re.match(r"cb_approve=(.+)", query.data)

    user_id = match.group(1)
    try:
        bot.approve_chat_join_request(chat.id, user_id)
        joined_user = await bot.get_chat_member(chat.id, user_id)  # Await here
        joined_mention = mention_html(user_id, html.escape(joined_user.user.first_name))
        admin_mention = mention_html(user.id, html.escape(user.first_name))
        await update.effective_message.edit_text(
                f"{joined_mention}'s join request was approved by {admin_mention}.",
                parse_mode="HTML",
        )
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#JOIN_REQUEST\n"
            f"Approved\n"
            f"<b>Admin:</b> {admin_mention}\n"
            f"<b>User:</b> {joined_mention}\n"
        )
        return logmsg
    except Exception as e:
        await update.effective_message.edit_text(str(e))
        pass


@check_admin(permission="can_invite_users", is_both=True)
@loggable
async def decline_joinReq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    match = re.match(r"cb_decline=(.+)", query.data)

    user_id = match.group(1)
    try:
        bot.decline_chat_join_request(chat.id, user_id)
        joined_user = await bot.get_chat_member(chat.id, user_id)  # Await here
        joined_mention = mention_html(user_id, html.escape(joined_user.user.first_name))
        admin_mention = mention_html(user.id, html.escape(user.first_name))
        await update.effective_message.edit_text(
                f"{joined_mention}'s join request was declined by {admin_mention}.",
                parse_mode="HTML",
        )
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#JOIN_REQUEST\n"
            f"Declined\n"
            f"<b>Admin:</b> {admin_mention}\n"
            f"<b>User:</b> {joined_mention}\n"
        )
        return logmsg
    except Exception as e:
        await update.effective_message.edit_text(str(e))
        pass



application.add_handler(ChatJoinRequestHandler(callback=chat_join_req, block=False))
application.add_handler(CallbackQueryHandler(callback=approve_joinReq, pattern=r"cb_approve="))
application.add_handler(CallbackQueryHandler(callback=decline_joinReq, pattern=r"cb_decline="))
