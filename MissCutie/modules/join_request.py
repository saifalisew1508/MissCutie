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



@check_admin(permission="can_invite_users", is_both=True)
@loggable
async def set_requests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user = update.effective_user

    if len(args) > 0:
        s = args[0].lower()

        if s in ["yes", "on", "true"]:
            enable_join_req(chat.id)
            await message.reply_html(
                "Enabled join request menu in {}\nI will send a button menu to approve/decline new requests".format(
                    html.escape(chat.title)))
            log_message = (
                f"#JOINREQUESTS\n"
                f"Enabled\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}"
            )
            return log_message

        elif s in ["off", "no", "false"]:
            disable_join_req(chat.id)
            await message.reply_html(
                "Disabled join request menu in {}\nI will no longer send a button menu to approve/decline new requests".format(
                    html.escape(chat.title)))
            log_message = (
                f"#JOINREQUESTS\n"
                f"Disabled\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}"
            )
            return log_message

        else:
            await message.reply_text("Unrecognized arguments {}".format(s))
            return

    await message.reply_html(
        "Join requests setting is currently <b><i>{}</i></b> in <code>{}</code>\n\n"
        "When this setting is on, I will send a message with Approve/Decline buttons on every join request".format(
            join_req_status(chat.id), html.escape(chat.title)))
    return



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
        await bot.approve_chat_join_request(chat.id, user_id)  # Await here
        joined_user = await bot.get_chat_member(chat.id, user_id)
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
        await bot.decline_chat_join_request(chat.id, user_id)  # Await here
        joined_user = await bot.get_chat_member(chat.id, user_id)
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



@loggable
@check_admin(permission="can_invite_users", is_both=True)
async def approve_all_join_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat = update.effective_chat
    try:
        join_requests = await bot.get_chat_members(chat.id)
        for join_request in join_requests:
            if join_request.status == 'kicked' or join_request.status == 'left':
                continue
            user_id = join_request.user.id
            try:
                await bot.approve_chat_join_request(chat.id, user_id)
                joined_mention = mention_html(user_id, html.escape(join_request.user.first_name))
                admin_mention = mention_html(update.effective_user.id, html.escape(update.effective_user.first_name))
                await update.message.reply_text(
                    f"{joined_mention}'s join request was approved by {admin_mention}.",
                    parse_mode="HTML"
                )
                logmsg = (
                    f"<b>{html.escape(chat.title)}:</b>\n"
                    f"#JOIN_REQUEST\n"
                    f"Approved\n"
                    f"<b>Admin:</b> {admin_mention}\n"
                    f"<b>User:</b> {joined_mention}\n"
                )
                print(logmsg)  # Adjust logging or storage as needed
            except Exception as e:
                await update.message.reply_text(str(e))

        await update.message.reply_text("All pending join requests have been approved.")
    except Exception as e:
        await update.message.reply_text(str(e))

approve_all_handler = CommandHandler('approveall', approve_all_join_requests)

application.add_handler(ChatJoinRequestHandler(callback=chat_join_req, block=False))
application.add_handler(CallbackQueryHandler(callback=approve_joinReq, pattern=r"cb_approve="))
application.add_handler(CallbackQueryHandler(callback=decline_joinReq, pattern=r"cb_decline="))
application.add_handler(approve_all_handler)
