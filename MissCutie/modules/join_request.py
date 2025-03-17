import html
import re
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    ContextTypes,
)

from MissCutie import application
from Database.sql.join_request import (
    enable_join_request,
    disable_features,
    join_request_status,
    enable_auto_approve,
    auto_approve_status,
    migrate_chat,
)
from telegram.helpers import mention_html


async def set_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    if args:
        choice = args[0].lower()
        if choice in ["on", "yes", "true"]:
            enable_join_request(chat.id)
            await update.message.reply_html(
                f"✅ Join request system enabled in <b>{html.escape(chat.title)}</b>."
            )
        elif choice in ["off", "no", "false"]:
            disable_features(chat.id)
            await update.message.reply_html(
                f"❌ Join request system disabled in <b>{html.escape(chat.title)}</b>."
            )
        else:
            await update.message.reply_text("⚠ Unrecognized argument. Use /joinrequest on|off")
        return

    current_status = join_request_status(chat.id)
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Enable", callback_data="join_enable"),
                InlineKeyboardButton("Disable", callback_data="join_disable")
            ]
        ]
    )
    await update.message.reply_html(
        f"Join request system is currently <b>{current_status}</b> in <code>{html.escape(chat.title)}</code>.",
        reply_markup=keyboard
    )


async def set_auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    args = context.args

    if args:
        choice = args[0].lower()
        if choice in ["on", "yes", "true"]:
            enable_auto_approve(chat.id)
            await update.message.reply_html(
                f"✅ Auto-approve enabled in <b>{html.escape(chat.title)}</b>."
            )
        elif choice in ["off", "no", "false"]:
            disable_features(chat.id)
            await update.message.reply_html(
                f"❌ Auto-approve disabled in <b>{html.escape(chat.title)}</b>."
            )
        else:
            await update.message.reply_text("⚠ Unrecognized argument. Use /autoapprove on|off")
        return

    current_status = auto_approve_status(chat.id)
    await update.message.reply_html(
        f"Auto-approve is currently <b>{current_status}</b> in <code>{html.escape(chat.title)}</code>."
    )


async def join_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    chat = update.chat_join_request.chat

    if auto_approve_status(chat.id):
        await context.bot.approve_chat_join_request(chat.id, user.id)
        await context.bot.send_message(
            chat.id,
            f"{mention_html(user.id, user.first_name)} has been auto-approved to join {chat.title}.",
            parse_mode=ParseMode.HTML
        )
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve:{user.id}"),
            InlineKeyboardButton("❌ Decline", callback_data=f"decline:{user.id}"),
            InlineKeyboardButton("🚫 Ban", callback_data=f"ban:{user.id}")
        ]
    ])
    await context.bot.send_message(
        chat.id,
        f"{mention_html(user.id, user.first_name)} requested to join {chat.title}.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat = update.effective_chat
    user = update.effective_user
    await query.answer()

    action, target_user_id = data.split(":")
    target_user_id = int(target_user_id)

    admin_status = await context.bot.get_chat_member(chat.id, user.id)
    if admin_status.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await query.answer("Only admins can manage requests.", show_alert=True)
        return

    if action == "approve":
        await context.bot.approve_chat_join_request(chat.id, target_user_id)
        await query.edit_message_text(
            f"✅ User <code>{target_user_id}</code> approved by {mention_html(user.id, user.first_name)}.",
            parse_mode=ParseMode.HTML,
        )
    elif action == "decline":
        await context.bot.decline_chat_join_request(chat.id, target_user_id)
        await query.edit_message_text(
            f"❌ User <code>{target_user_id}</code> declined by {mention_html(user.id, user.first_name)}.",
            parse_mode=ParseMode.HTML,
        )
    elif action == "ban":
        await context.bot.decline_chat_join_request(chat.id, target_user_id)
        await context.bot.ban_chat_member(chat.id, target_user_id)
        await query.edit_message_text(
            f"🚫 User <code>{target_user_id}</code> was banned by {mention_html(user.id, user.first_name)}.",
            parse_mode=ParseMode.HTML,
        )


async def inline_button_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    if query.data == "join_enable":
        enable_join_request(chat.id)
        await query.answer("Join request system enabled.")
        await query.edit_message_text(f"✅ Join request system enabled in {chat.title}.")
    elif query.data == "join_disable":
        disable_features(chat.id)
        await query.answer("Join request system disabled.")
        await query.edit_message_text(f"❌ Join request system disabled in {chat.title}.")


def __migrate__(old_chat_id, new_chat_id):
    migrate_chat(old_chat_id, new_chat_id)


# Register Handlers
application.add_handler(CommandHandler("joinrequest", set_requests))
application.add_handler(CommandHandler("autoapprove", set_auto_approve))
application.add_handler(ChatJoinRequestHandler(join_request_handler))
application.add_handler(CallbackQueryHandler(button_handler, pattern="^(approve|decline|ban):"))
application.add_handler(CallbackQueryHandler(inline_button_toggle, pattern="^(join_enable|join_disable)$"))


# Help Text & Module Info
__help__ = """
➠ This module helps admins manage join requests more efficiently by offering approval/decline options with inline buttons.

➠ *Admin commands:*

» /joinrequest <on/off>: Enable or disable the join request approval system.
» /autoapprove <on/off>: Automatically approve all join requests without needing manual approval.

When enabled, the bot will show a menu with Approve/Decline/Ban buttons for each incoming join request.
"""

__mod_name__ = "Join Requests"
__command_list__ = ["joinrequest", "autoapprove"]