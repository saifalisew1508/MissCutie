from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, ContextTypes, CallbackQueryHandler
from datetime import datetime
import html
import asyncio
from MissCutie import application, OWNER_ID
from telegram.helpers import mention_html
from Database.mongodb.copyright import (
    enable_anticopyright,
    disable_anticopyright,
    is_anticopyright_enabled,
)

# =================== HANDLE MESSAGES ====================
async def handle_message(update: Update, context: CallbackContext) -> None:
    message = update.message
    chat = update.effective_chat
    chat_id = message.chat_id

    # Check bot delete permission
    bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
    can_delete = bot_member.can_delete_messages

    if is_anticopyright_enabled(chat_id):
        if not can_delete:
            disable_anticopyright(chat_id)
            try:
                await context.bot.send_message(
                    chat_id,
                    f"⚠️ Anticopyright auto-disabled because I lost <b>delete messages</b> permission.",
                    parse_mode="HTML",
                )
            except Exception as e:
                context.bot.logger.warning(f"Failed to warn about permission: {e}")
            return

        if message.edit_date:
            try:
                await message.delete()
            except Exception as e:
                context.bot.logger.error(f"Error deleting edited message: {e}")
        elif message.sticker:
            try:
                await message.delete()
            except Exception as e:
                context.bot.logger.error(f"Error deleting sticker: {e}")
        elif message.video and (datetime.now().timestamp() - message.date.timestamp() > 120):
            try:
                await message.delete()
            except Exception as e:
                context.bot.logger.error(f"Error deleting old video: {e}")

    else:
        if message.edit_date:
            if any([message.photo, message.video, message.document, message.audio]):
                if can_delete:
                    try:
                        await message.delete()
                    except Exception as e:
                        context.bot.logger.error(f"Error deleting edited media: {e}")
            elif message.text or message.caption:
                if can_delete:
                    try:
                        await asyncio.sleep(60)
                        await message.delete()
                    except Exception as e:
                        context.bot.logger.error(f"Error deleting edited text after 60s: {e}")

# =================== COMMAND HANDLER ====================
async def set_anticopyright(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
    can_delete = bot_member.can_delete_messages

    if args:
        s = args[0].lower()
        if s in ["yes", "on", "true"]:
            if not can_delete:
                await message.reply_html(
                    f"⚠️ I can't enable anticopyright in <b>{html.escape(chat.title)}</b>.\n"
                    "Please give me <b>delete messages</b> permission first."
                )
                return

            enable_anticopyright(chat.id)
            await message.reply_html(
                f"✅ Anticopyright has been <b>enabled</b> in <b>{html.escape(chat.title)}</b>.\n"
                "I will delete <b>edited messages, stickers</b>, and <b>videos after 2 minutes</b>."
            )
            return

        elif s in ["no", "off", "false"]:
            disable_anticopyright(chat.id)
            await message.reply_html(
                f"❌ Anticopyright has been <b>disabled</b> in <b>{html.escape(chat.title)}</b>."
            )
            return

        else:
            await message.reply_text(f"Unrecognized argument: <code>{s}</code>")
            return

    # No args: Show status with inline buttons
    status = is_anticopyright_enabled(chat.id)
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✅ Turn OFF", callback_data="anticopy_off")
        ]] if status else [[
            InlineKeyboardButton("🔒 Turn ON", callback_data="anticopy_on")
        ]]
    )

    await message.reply_html(
        f"Anticopyright is currently <b>{'enabled' if status else 'disabled'}</b> in <b>{html.escape(chat.title)}</b>.\n\n"
        "➤ When enabled: I delete <b>edited messages, stickers</b>, and <b>videos after 2 minutes</b>.\n"
        "➤ When disabled: I delete <b>edited media instantly</b> and <b>text after 60 seconds</b>.",
        reply_markup=keyboard
    )

# =================== CALLBACK HANDLER ====================
async def anticopy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat = update.effective_chat
    user = update.effective_user
    bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
    can_delete = bot_member.can_delete_messages

    if query.data == "anticopy_on":
        if not can_delete:
            await query.edit_message_text(
                f"⚠️ I can't enable anticopyright in <b>{html.escape(chat.title)}</b>.\n"
                "Please give me <b>delete messages</b> permission first.",
                parse_mode="HTML"
            )
            return

        enable_anticopyright(chat.id)
        await query.edit_message_text(
            f"✅ Anticopyright has been <b>enabled</b> in <b>{html.escape(chat.title)}</b>.",
            parse_mode="HTML"
        )

    elif query.data == "anticopy_off":
        disable_anticopyright(chat.id)
        await query.edit_message_text(
            f"❌ Anticopyright has been <b>disabled</b> in <b>{html.escape(chat.title)}</b>.",
            parse_mode="HTML"
        )


__help__ = """
➠ This feature protects your group from unwanted edits and media forwarding.

➠ When enabled, I will delete:
 • Edited messages
 • Stickers
 • Videos after 2 minutes

➠ If disabled, I will still delete:
 • Edited media immediately
 • Edited text after 60 seconds

➠ *Admin commands:*

» /anticopyright - Show current status and get inline buttons to toggle.
» /anticopyright on - Enable copyright protection.
» /anticopyright off - Disable copyright protection.

➠ Make sure I have *Delete Messages* permission or I will disable the protection automatically.
"""

__mod_name__ = "COPYRIGHT"
__command_list__ = ["anticopyright"]


# =================== HANDLER REGISTRATION ====================
application.add_handler(CommandHandler("anticopyright", set_anticopyright))
application.add_handler(CallbackQueryHandler(anticopy_callback, pattern="^anticopy_"))
application.add_handler(MessageHandler(Filters.all, handle_message))