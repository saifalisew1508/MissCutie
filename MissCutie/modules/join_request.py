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
from telegram.constants import ParseMode, ChatMemberStatus
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.helpers import mention_html

from MissCutie import application
from MissCutie.modules.helper_funcs.chat_status import check_admin
from MissCutie.modules.log_channel import loggable
from MissCutie.modules.sql.join_request import enable_join_request, disable_features, join_request_status, enable_auto_approve, auto_approve_status, migrate_chat


@check_admin(permission="can_invite_users", is_both=True)
@loggable
async def set_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user = update.effective_user

    if len(args) > 0:
        s = args[0].lower()

        if s in ["yes", "on", "true"]:
            enable_join_request(chat.id)
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
            disable_features(chat.id)
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
            join_request_status(chat.id), html.escape(chat.title)))
    return


@check_admin(permission="can_invite_users", is_both=True)
@loggable
async def set_auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user = update.effective_user

    if len(args) > 0:
        s = args[0].lower()

        if s in ["yes", "on", "true"]:
            enable_auto_approve(chat.id)
            await message.reply_html(
                "Enabled auto-approve for join requests in {}".format(html.escape(chat.title)))
            log_message = (
                f"#AUTOAPPROVE\n"
                f"Enabled\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}"
            )
            return log_message

        elif s in ["off", "no", "false"]:
            disable_features(chat.id)
            await message.reply_html(
                "Disabled auto-approve for join requests in {}".format(html.escape(chat.title)))
            log_message = (
                f"#AUTOAPPROVE\n"
                f"Disabled\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}"
            )
            return log_message

        else:
            await message.reply_text("Unrecognized arguments {}".format(s))
            return

    await message.reply_html(
        "Auto-approve for join requests is currently <b><i>{}</i></b> in <code>{}</code>\n\n"
        "When this setting is on, new join requests will be automatically approved.".format(
            auto_approve_status(chat.id), html.escape(chat.title)))
    return


async def chat_join_req(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    user = update.chat_join_request.from_user
    chat = update.chat_join_request.chat
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Approve", callback_data=f"cb_approve={user.id}"
                ),
                InlineKeyboardButton(
                    "❌ Decline", callback_data=f"cb_decline={user.id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🚫 Ban", callback_data=f"cb_ban={user.id}"
                ),
            ],
        ],
    )


    # Check if auto-approve is enabled
    if auto_approve_status(chat.id) and auto_approve_status(chat.id):
        await bot.approve_chat_join_request(chat.id, user.id)
        await bot.send_message(
            chat.id,
            "{} has been automatically approved and joined {}".format(
                mention_html(user.id, user.first_name), chat.title or "this chat"
            ),
            parse_mode=ParseMode.HTML,
        )
        return

    await bot.send_message(
        chat.id,
        "{} wants to join {}".format(
            mention_html(user.id, user.first_name), chat.title or "this chat"
        ),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )



@loggable
async def approve_joinReq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    match = re.match(r"cb_approve=(.+)", query.data)

    user_id = match.group(1)

    try:
        # Check if the user is an admin or owner
        user_status = await bot.get_chat_member(chat.id, user.id)
        if user_status.status == ChatMemberStatus.OWNER:
            # If the user is an owner, allow the operation without checking invite permission
            pass
        elif user_status.status != ChatMemberStatus.ADMINISTRATOR:
            await bot.answer_callback_query(query.id, "You are not authorized to approve join requests.", show_alert=True)
            return

        # Check if the user has the "invite users" permission
        if user_status.status != ChatMemberStatus.OWNER and not user_status.can_invite_users:
            await bot.answer_callback_query(query.id, "You don't have the permission to invite users.", show_alert=True)
            return

        await bot.approve_chat_join_request(chat.id, user_id)
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
        error_message = str(e)
        if "Hide_requester_missing" in error_message:
            await update.effective_message.edit_text("This user has already been declined by admins manually.")
        elif "User_already_participant" in error_message:
            await update.effective_message.edit_text("This user has already been approved by admins manually.")
        else:
            await update.effective_message.edit_text(error_message)
        pass



@loggable
async def decline_joinReq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    match = re.match(r"cb_decline=(.+)", query.data)

    user_id = match.group(1)
    
    try:
        # Check if the user is an admin or owner
        user_status = await bot.get_chat_member(chat.id, user.id)
        if user_status.status == ChatMemberStatus.OWNER:
            # If the user is an owner, allow the operation without checking invite permission
            pass
        elif user_status.status != ChatMemberStatus.ADMINISTRATOR:    
            await bot.answer_callback_query(query.id, "You are not authorized to approve join requests.", show_alert=True)
            return

        # Check if the user has the "invite users" permission
        if user_status.status != ChatMemberStatus.OWNER and not user_status.can_invite_users:
            await bot.answer_callback_query(query.id, "You don't have the permission to invite users.", show_alert=True)
            return

        
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
        error_message = str(e)
        if "Hide_requester_missing" in error_message:
            await update.effective_message.edit_text("This user has already been declined by admins manually.")
        elif "User_already_participant" in error_message:
            await update.effective_message.edit_text("This user has already been approved by admins manually.")
        else:
            await update.effective_message.edit_text(error_message)
        pass



@loggable
async def ban_joinReq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    match = re.match(r"cb_ban=(.+)", query.data)

    if not match:
        return

    user_id = match.group(1)

    try:
        # Check if the user is an admin or owner
        user_status = await bot.get_chat_member(chat.id, user.id)
        if user_status.status == ChatMemberStatus.OWNER:
            # If the user is an owner, allow the operation without checking invite permission
            pass
        elif user_status.status != ChatMemberStatus.ADMINISTRATOR:    
            await bot.answer_callback_query(query.id, "You are not authorized to approve join requests.", show_alert=True)
            return

        # Check if the user has the "restrict users" permission
        if user_status.status != ChatMemberStatus.OWNER and not user_status.can_restrict_members:
            await bot.answer_callback_query(query.id, "You don't have the permission to invite users.", show_alert=True)
            return
            

        await bot.decline_chat_join_request(chat.id, user_id)
        await bot.ban_chat_member(chat.id, user_id)
        joined_user = await bot.get_chat_member(chat.id, user_id)
        joined_mention = mention_html(user_id, html.escape(joined_user.user.first_name))
        admin_mention = mention_html(user.id, html.escape(user.first_name))
        await update.effective_message.edit_text(
            f"{joined_mention}'s join request was banned by {admin_mention}.",
            parse_mode="HTML",
        )
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#JOIN_REQUEST_BANNED\n"
            f"Banned\n"
            f"<b>Admin:</b> {admin_mention}\n"
            f"<b>User:</b> {joined_mention}\n"
        )
        return logmsg
    except Exception as e:
        error_message = str(e)
        if "Hide_requester_missing" in error_message:
            await update.effective_message.edit_text("This user has already been declined by admins manually.")
        elif "User_already_participant" in error_message:
            await update.effective_message.edit_text("This user has already been approved by admins manually.")
        else:
            await update.effective_message.edit_text(error_message)
        pass



def __migrate__(old_chat_id, new_chat_id):
    migrate_chat(old_chat_id, new_chat_id)


application.add_handler(CommandHandler('joinrequest', set_requests))
application.add_handler(CommandHandler('autoapprove', set_auto_approve))  # Added handler for the V3.0 new command
application.add_handler(ChatJoinRequestHandler(callback=chat_join_req, block=False))
application.add_handler(CallbackQueryHandler(callback=approve_joinReq, pattern=r"cb_approve="))
application.add_handler(CallbackQueryHandler(callback=decline_joinReq, pattern=r"cb_decline="))
application.add_handler(CallbackQueryHandler(callback=ban_joinReq, pattern=r"cb_ban="))
