from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from MissCutie.modules.helper_funcs.chat_status import check_admin
from MissCutie.modules.helper_funcs.alternate import typing_action
from io import BytesIO

__mod_name__ = "Ban & Mute"
__command_list__ = ["ban", "unban", "mute", "unmute", "banlist", "ghost"]
__help__ = """
/ban - Ban a user from the group (reply or mention)
/unban - Unban a user (reply or mention)
/mute - Mute a user (reply or mention)
/unmute - Unmute a user (reply or mention)
/banlist or /ghost - Download list of banned users in .txt file
"""

banned_users = {}
muted_users = {}

@typing_action
@check_admin
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to ban.")
        return
    await context.bot.ban_chat_member(chat.id, target.id)
    banned_users.setdefault(str(chat.id), []).append(f"{target.first_name} | {target.id}")
    await update.message.reply_text(f"Banned {target.first_name}.")

@typing_action
@check_admin
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to unban.")
        return
    await context.bot.unban_chat_member(chat.id, target.id)
    await update.message.reply_text(f"Unbanned {target.first_name}.")

@typing_action
@check_admin
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to mute.")
        return
    await context.bot.restrict_chat_member(chat.id, target.id, permissions={})
    muted_users.setdefault(str(chat.id), []).append(f"{target.first_name} | {target.id}")
    await update.message.reply_text(f"Muted {target.first_name}.")

@typing_action
@check_admin
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to unmute.")
        return
    await context.bot.restrict_chat_member(chat.id, target.id, permissions=context.bot.defaults.permissions)
    await update.message.reply_text(f"Unmuted {target.first_name}.")

@typing_action
@check_admin
async def banlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    users = banned_users.get(chat_id, [])
    if not users:
        await update.message.reply_text("No banned users found.")
        return
    text = "\n".join(users)
    file = BytesIO(text.encode("utf-8"))
    file.name = "banned_users.txt"
    await update.message.reply_document(file, caption="Banned Users List")

ban_handler = CommandHandler(["ban"], ban)
unban_handler = CommandHandler(["unban"], unban)
mute_handler = CommandHandler(["mute"], mute)
unmute_handler = CommandHandler(["unmute"], unmute)
banlist_handler = CommandHandler(["banlist", "ghost"], banlist)