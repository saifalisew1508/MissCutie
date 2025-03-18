import asyncio
import contextlib
import importlib
import json
import re
import time
import traceback
from platform import python_version
from random import choice

import psutil
import pyrogram
import telegram
import telethon
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import (
    BadRequest,
    ChatMigrated,
    Forbidden,
    NetworkError,
    TelegramError,
    TimedOut,
)
from telegram.ext import (
    ApplicationHandlerStop,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown

from strings.buttons import *
from strings.messages import *
from MissCutie import *
from MissCutie.plugins import ALL_MODULES
from MissCutie.plugins.helper_funcs.chat_status import is_user_admin
from MissCutie.plugins.helper_funcs.misc import paginate_modules


PYTHON_VERSION = python_version()
PTB_VERSION = telegram.__version__
PYROGRAM_VERSION = pyrogram.__version__
TELETHON_VERSION = telethon.__version__

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("MissCutie.plugins." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module



async def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    await application.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    message = update.effective_message
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                await send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                await send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="🔙", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower() == "markdownhelp":
                IMPORTED["exᴛʀᴀs"].markdown_help_sender(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = application.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                await IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            chat = update.effective_chat
            await update.effective_message.reply_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(PM_START_BUTTON).format(escape_markdown(first_name), escape_markdown(context.bot.first_name)),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False,
            )
    else:
        await update.effective_message.reply_text(
            "Hello! I'm currently running on {} version {}.\n\n"
            "<b>Uptime:</b> <code>{}</code>\n"
            "<b>Python Version:</b> <code>v{}</code>\n"
            "<b>Telethon Version:</b> <code>v{}</code>\n"
            "<b>Pyrogram Version:</b> <code>v{}</code>\n"
            "<b>Python Telegram Bot Version:</b> <code>v{}</code>\n"
            "<b>Telegram Bot API Version:</b> <code>v{}</code>".format(
                BOT_NAME, BOT_VERSION, uptime, PYTHON_VERSION, TELETHON_VERSION, PYRO_VERSION, PTB_VERSION, BOT_API_VERSION,
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Developer 🧑‍💻",
                            url="tg://user?id={}".format(OWNER_ID),
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Need help?",
                            url="t.me/{}?start=help".format(context.bot.username),
                        ),
                    ],
                ],
            ),
        )


async def saif_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uptime = get_readable_time((time.time() - StartTime))
    first_name = update.effective_user.first_name 
    chat = update.effective_chat
    if query.data == "saif_":
        await query.message.edit_text(
            ABOUT_TEXT.format(
                BOT_NAME, BOT_NAME, BOT_VERSION, uptime, PYTHON_VERSION, PYRO_VERSION, TELETHON_VERSION, PTB_VERSION, BOT_API_VERSION, MONGO_VERSION, SQL_VERSION, BOT_NAME,
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(ABOUT_BUTTON),
        )
    elif query.data == "saif_support":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            SAIF_SUPPORT.format(
                BOT_NAME,
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(ABOUT_BUTTON),
        )
    elif query.data == "saif_sponsor":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            SAIF_SPONSORS.format(
                BOT_NAME, BOT_NAME,
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(ABOUT_BUTTON),
        )
    elif query.data == "saif_developer":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            SAIF_DEVELOPERS.format(
                BOT_NAME,
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(ABOUT_BUTTON),
        )
    elif query.data == "saif_source":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            SAIF_SOURCE.format(
                BOT_NAME, BOT_NAME, BOT_NAME, BOT_NAME, BOT_NAME,
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(ABOUT_BUTTON),
        )
    elif query.data == "saif_close":
        await query.message.delete()
            
    elif query.data == "saif_back":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name), escape_markdown(context.bot.first_name)),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )

async def music_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    first_name = update.effective_user.first_name 
    if query.data == "Music_":
        await query.message.edit_text(
            text=MUSIC_TEXT.format(escape_markdown(first_name), 
                                   escape_markdown(context.bot.first_name)),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(music_buttons),
        )

    elif query.data == "Music_admin":
        await query.message.edit_text(
            text=MUSIC_ADMIN,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(music_buttons),
        )
    elif query.data == "Music_play":
        await query.message.edit_text(
            text=MUSIC_PLAY,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(music_buttons),
        )
    elif query.data == "Music_bot":
        await query.message.edit_text(
            text=MUSIC_BOT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(music_buttons),
        )
    elif query.data == "Music_extra":
        await query.message.edit_text(
            text=MUSIC_EXTRA,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(music_buttons),
        )
    elif query.data == "Music_close":
        await query.message.delete()
        
    elif query.data == "Music_back":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name),
                                 escape_markdown(context.bot.first_name)),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )



async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    await context.bot.send_message(
        chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML
    )

async def error_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raise context.error
    except (Forbidden, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError) as e:
        LOGGER.warning(f"Error: {e}")

async def help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    try:
        if mod := re.match(r"help_module(.+?)", data):
            module = mod.group(1)
            text = f"➲ *HELP SECTION OF* *{HELPABLE[module].__mod_name__}*:\n{HELPABLE[module].__help__}"
            await query.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◁", callback_data="help_back")]]))
        elif match := re.match(r"help_(prev|next)(\d+)", data):
            page = int(match.group(2)) + (-1 if match.group(1) == "prev" else 1)
            await query.message.edit_text(HELP_STRINGS, parse_mode=ParseMode.MARKDOWN,
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(page, HELPABLE, "help")))
        elif "help_back" in data:
            await query.message.edit_text(HELP_STRINGS, parse_mode=ParseMode.MARKDOWN,
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))
        await context.bot.answer_callback_query(query.id)
    except BadRequest:
        pass

async def stats_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == "insider_":
        uptime = time.time() - StartTime
        text = f"""⚡ Powered By: @BotXNews
➖➖➖➖➖
UPTIME: {int(uptime // 3600)}h {(uptime % 3600)//60:.0f}m
CPU: {psutil.cpu_percent()}%
RAM: {psutil.virtual_memory().percent}%
DISK: {psutil.disk_usage('/').percent}%
PYTHON: {PYTHON_VERSION} | PTB: {PTB_VERSION}
Telethon: {TELETHON_VERSION} | Pyrogram: {PYROGRAM_VERSION}
"""
        await update.callback_query.answer(text=text, show_alert=True)

async def send_alive(context: ContextTypes.DEFAULT_TYPE):
    if SUPPORT_CHAT:
        try:
            await context.bot.send_photo(
                chat_id=f"@{SUPPORT_CHAT}",
                photo="https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg",
                caption=f"""
Hey Developer's {context.bot.first_name} is online now.

**Python :** `v{PYTHON_VERSION}`
**Telethon :** `v{TELETHON_VERSION}`
**Pyrogram :** `v{PYROGRAM_VERSION}`
**PTB :** `v{PTB_VERSION}`
**API :** `v{BOT_API_VERSION}`
**{BOT_NAME} :** `v{BOT_VERSION}`

⚡ Powered By: @BotXNews
""", parse_mode=ParseMode.MARKDOWN)
        except (Forbidden, BadRequest) as e:
            LOGGER.warning(f"Alive Msg Error: {e}")

async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    args = update.effective_message.text.split(None, 1)
    if chat.type != chat.PRIVATE:
        module = args[1].lower() if len(args) >= 2 else None
        if module and module in HELPABLE:
            await update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("HELP", url=f"https://t.me/{context.bot.username}?start=ghelp_{module}")]]))
        else:
            await update.effective_message.reply_text(
                "» *Choose an option for getting help*",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("OPEN IN PM", url=f"https://t.me/{context.bot.username}?start=help")],
                    [InlineKeyboardButton("OPEN HERE", callback_data="extra_command_handler")]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        module = args[1].lower() if len(args) >= 2 else None
        if module and module in HELPABLE:
            await send_help(chat.id, f"*Help for {HELPABLE[module].__mod_name__}*:\n{HELPABLE[module].__help__}",
                            InlineKeyboardMarkup([[InlineKeyboardButton("◁", callback_data="help_back")]]))
        else:
            await send_help(chat.id, HELP_STRINGS)

async def get_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, user = update.effective_chat, update.effective_user
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            await update.effective_message.reply_text(
                "Click below to get chat settings.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("SETTINGS", url=f"https://t.me/{context.bot.username}?start=stngs_{chat.id}")]
                ]))
    else:
        await send_settings(chat.id, user.id, user=True)

async def migrate_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    old_chat, new_chat = (update.effective_chat.id, msg.migrate_to_chat_id) if msg.migrate_to_chat_id else (msg.migrate_from_chat_id, update.effective_chat.id)
    LOGGER.info(f"Migrating: {old_chat} -> {new_chat}")
    for mod in MIGRATEABLE:
        with contextlib.suppress(Exception):
            mod.__migrate__(old_chat, new_chat)
    raise ApplicationHandlerStop


# ======================== Main Setup ========================

def main():
    application.job_queue.run_repeating(send_alive, interval=1800, first=10)
    application.add_handler(CommandHandler("start", start, block=False))
    application.add_handler(CommandHandler("help", get_help, block=False))
    application.add_handler(CallbackQueryHandler(help_button, pattern=r"help_.*", block=False))
    application.add_handler(CallbackQueryHandler(saif_about_callback, pattern=r"saif_", block=False))
    application.add_handler(CallbackQueryHandler(music_about_callback, pattern=r"Music_", block=False))
    application.add_handler(CommandHandler("settings", get_settings, block=False))
    application.add_handler(CommandHandler("donate", donate, block=False))
    application.add_handler(MessageHandler(filters.StatusUpdate.MIGRATE, migrate_chats, block=False))
    application.add_error_handler(error_callback)

    LOGGER.info("MissCutie is running >> Long polling started")
    application.run_polling(timeout=15, drop_pending_updates=True)


if __name__ == "__main__":
    try:
        LOGGER.info("Loaded modules: " + str(ALL_MODULES))
        tbot.start(bot_token=TOKEN)
        app.start()
        main()
    except KeyboardInterrupt:
        pass
    except Exception:
        LOGGER.error(traceback.format_exc())
    finally:
        try:
            if loop.is_running():
                loop.stop()
        finally:
            loop.close()
        LOGGER.info("» Stopped Services")