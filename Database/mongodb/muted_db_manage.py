from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from MissCutie.modules.helper_funcs.chat_status import check_admin
from MissCutie.modules.helper_funcs.alternate import typing_action
from Database.mongodb import muted_db
from io import BytesIO

__mod_name__ = "Muted DB"
__command_list__ = ["mutelist"]
__help__ = """
/mutelist - Download list of muted users stored by the bot (MongoDB-based)
Note: Manually unmuted users may still appear in this list.
"""

@typing_action
@check_admin
async def mutelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    muted = await muted_db.get_muted_users(chat_id)
    if not muted:
        await update.message.reply_text("No muted users found in database.")
        return
    text = "\n".join([f"{user['name']} | {user['user_id']}" for user in muted])
    text += "\n\nNote: Manually unmuted users may still appear in this list."
    file = BytesIO(text.encode("utf-8"))
    file.name = "muted_users_list.txt"
    await update.message.reply_document(file, caption="Muted Users List")

mutelist_handler = CommandHandler("mutelist", mutelist)