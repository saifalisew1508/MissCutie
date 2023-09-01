from typing import List
from telegram.constants import ParseMode
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from MissCutie import application
from MissCutie.modules.helper_funcs.chat_status import user_not_admin, check_admin, can_delete
from MissCutie.modules.helper_funcs.extraction import extract_text
from MissCutie.modules.sql import antiarabic_sql as sql

ANTIARABIC_GROUPS = 12


@check_admin(is_user=True)
async def antiarabic_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    msg = update.effective_message

    if chat.type != chat.PRIVATE:
        if len(args) >= 1:
            if args[0].lower() in ("yes", "on", "true"):
                await sql.set_chat_setting(chat.id, True)
                await msg.reply_text("Turned on AntiArabic! Messages sent by any non-admin which contains arabic text will be deleted.")

            elif args[0].lower() in ("no", "off", "false"):
                await sql.set_chat_setting(chat.id, False)
                await msg.reply_text("Turned off AntiArabic! Messages containing arabic text won't be deleted.")
        else:
            await msg.reply_text("</antiarabic on/off> to turn on or turn off AntiArabic Mode.")


@user_not_admin
async def antiarabic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    msg = update.effective_message
    to_match = extract_text(msg)
    user = update.effective_user

    if not sql.chat_antiarabic(chat.id):
        return

    if not user or user.id == 777000:  # ignore channels and Telegram
        return

    if not to_match:
        return

    if chat.type != chat.PRIVATE:
        for c in to_match:
            if ('\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F'
                    or '\u08A0' <= c <= '\u08FF' or '\uFB50' <= c <= '\uFDFF'
                    or '\uFE70' <= c <= '\uFEFF'
                    or '\U00010E60' <= c <= '\U00010E7F'
                    or '\U0001EE00' <= c <= '\U0001EEFF'):
                if can_delete(chat, bot.id):
                    await update.effective_message.delete()


async def migrate_chat(old_chat_id, new_chat_id):
    await sql.migrate_chat(old_chat_id, new_chat_id)


__help__ = """
Here is some help for the AntiArabicScript module:
AntiArabicScript module is used to delete messages containing characters from one of the following automatically:

• Arabic
• Arabic Supplement
• Arabic Extended-A
• Arabic Presentation Forms-A
• Arabic Presentation Forms-B
• Rumi Numeral Symbols
• Arabic Mathematical Alphabetic Symbol

NOTE: AntiArabicScript module doesn't affect messages sent by admins.

Admin only:
 - `/antiarabic` `<on/off>`*:* turn antiarabic module on/off ( off by default )
"""
__mod_name__ = "Anti Arabic"

SETTING_HANDLER = CommandHandler("antiarabic", antiarabic_setting, block=False)
MessageHandler(
    (filters.TEXT | filters.COMMAND | filters.Sticker.ALL | filters.PHOTO) & filters.ChatType.GROUPS,
    antiarabic,
    block=False
)

application.add_handler(SETTING_HANDLER)
application.add_handler(ANTI_ARABIC, group=ANTIARABIC_GROUPS)
