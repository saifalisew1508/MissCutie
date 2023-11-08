import tracemalloc
import importlib
import contextlib
import time
import re
import random

from MissCutie import *
from strings.buttons import *

import MissCutie.modules.sql.users_sql as sql
from MissCutie.modules import ALL_MODULES
from MissCutie.modules.helper_funcs.chat_status import is_user_admin
from MissCutie.modules.helper_funcs.misc import paginate_modules
from MissCutie.modules.connection import connected
from MissCutie.modules.language import gs, set_lang
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Chat, User
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Forbidden,
)
from telegram.ext import (
    ContextTypes,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    filters,
    MessageHandler,
)
from telegram.constants import ParseMode
from telegram.ext import ApplicationHandlerStop
from telegram.helpers import escape_markdown
from sys import argv
from typing import Optional


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


START_IMG = "https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg"


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
    imported_module = importlib.import_module("MissCutie.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "get_help") and imported_module.get_help:
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
    uptime = get_readable_time((time.time() - StartTime))
    chat = update.effective_chat
    
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                await send_help(update.effective_chat.id, (gs(chat.id, "HELP_STRINGS")))
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                await send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="🔙", callback_data="help_back")]],
                    ),
                )
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = await application.bot.getChat(match.group(1))
                if await is_user_admin(chat, update.effective_user.id):
                    await send_settings(match.group(1), update.effective_user, update, context, False)
                else:
                    await send_settings(match.group(1), update.effective_user, update, context, True)
            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                await IMPORTED["rules"].send_rules(update, args[0], from_pm=True)
        else:
            first_name = update.effective_user.first_name
            chat = update.effective_chat
            await update.effective_message.reply_text(
                text=gs(chat.id, "PM_START_TEXT").format(escape_markdown(first_name),
                                     escape_markdown(context.bot.first_name)),
                reply_markup=InlineKeyboardMarkup(PM_START_BUTTON),
                parse_mode=ParseMode.MARKDOWN,
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




# for test purposes
async def error_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    try:
        raise error
    except Forbidden:
        LOGGER.error("\nForbidden Erro\n")
        LOGGER.error(error)
        raise error
        # remove update.message.chat_id from conversation list
    except BadRequest:
        LOGGER.error("\nBadRequest Error\n")
        LOGGER.error("BadRequest caught")
        LOGGER.error(error)
        raise error

        # handle malformed requests - read more below!
    except TimedOut:
        LOGGER.error("\nTimedOut Error\n")
        raise error
        # handle slow connection problems
    except NetworkError:
        LOGGER.error("\n NetWork Error\n")
        raise error
        # handle other connection problems
    except ChatMigrated as err:
        LOGGER.error("\n ChatMigrated error\n")
        raise error
        LOGGER.error(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        LOGGER.error(error)
        raise # then only it sends the message to the owner
        # handle all other telegram related errors




async def help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    chat = update.effective_chat
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    chat = update.effective_chat
    # print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            module = module.replace("_", " ")
            help_list = HELPABLE[module].get_help(update.effective_chat.id)
            if isinstance(help_list, list):
                help_text = help_list[0]
                help_PM_START_BUTTON = help_list[1:]
            elif isinstance(help_list, str):
                help_text = help_list
                help_PM_START_BUTTON = []
            text = (
                    "Here is the help for the *{}* module:\n".format(
                        HELPABLE[module].__mod_name__
                    )
                    + help_text
            )
            help_PM_START_BUTTON.append(
                [InlineKeyboardButton(text="🔙", callback_data="help_back")]
            )
            await query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="🔙", callback_data="help_back")]],
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_text(
                text=gs(chat.id, "HELP_STRINGS"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help"),
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_text(
                text=gs(chat.id, "HELP_STRINGS"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help"),
                ),
            )

        elif back_match:
            await query.message.edit_text(
                text=gs(chat.id, "HELP_STRINGS"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help"),
                ),
            )


        await context.bot.answer_callback_query(query.id)


    except BadRequest:
        pass



async def saif_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    first_name = update.effective_user.first_name 
    chat = update.effective_chat
    if query.data == "saif_":
        uptime = get_readable_time((time.time() - StartTime))
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            text=gs(chat.id, "ABOUT_TEXT").format(
                BOT_NAME, BOT_NAME, BOT_VERSION, uptime, PYTHON_VERSION, PYRO_VERSION, TELETHON_VERSION, PTB_VERSION, BOT_API_VERSION, MONGO_VERSION, SQL_VERSION, BOT_NAME,
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(ABOUT_BUTTON),
        )
    elif query.data == "saif_support":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            text=gs(chat.id, "SAIF_SUPPORT").format(
                BOT_NAME,
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(ABOUT_BUTTON),
        )
    elif query.data == "saif_sponsor":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            text=gs(chat.id, "SAIF_SPONSORS").format(
                BOT_NAME, BOT_NAME,
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(ABOUT_BUTTON),
        )
    elif query.data == "saif_developer":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            text=gs(chat.id, "SAIF_DEVELOPERS").format(
                BOT_NAME,
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(ABOUT_BUTTON),
        )
    elif query.data == "saif_source":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            text=gs(chat.id, "SAIF_SOURCE").format(
                BOT_NAME, BOT_NAME, BOT_NAME, BOT_NAME, BOT_NAME,
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(ABOUT_BUTTON),
        )
    elif query.data == "saif_close":
        await query.message.delete()
            
    elif query.data == "saif_back":
        chat = update.effective_chat
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            text=gs(chat.id, "PM_START_TEXT").format(escape_markdown(first_name), escape_markdown(context.bot.first_name)),
            reply_markup=InlineKeyboardMarkup(PM_START_BUTTON),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )


async def music_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    first_name = update.effective_user.first_name 
    if query.data == "Music_":
        await query.message.edit_text(
            text=gs(chat.id, "MUSIC_TEXT").format(escape_markdown(first_name), 
                                   escape_markdown(context.bot.first_name)),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )

    elif query.data == "Music_admin":
        await query.message.edit_text(
            text=gs(chat.id, "ADMIN_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_auth":
        await query.message.edit_text(
            text=gs(chat.id, "AUTH_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_broadcast":
        await query.message.edit_text(
            text=gs(chat.id, "BROADCAST_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_blackchat":
        await query.message.edit_text(
            text=gs(chat.id, "BLACKCHAT_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_blackuser":
        await query.message.edit_text(
            text=gs(chat.id, "BLACKUSER_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_cplay":
        await query.message.edit_text(
            text=gs(chat.id, "CPLAY_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_gban":
        await query.message.edit_text(
            text=gs(chat.id, "GBAN_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_loop":
        await query.message.edit_text(
            text=gs(chat.id, "LOOP_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_maintenance":
        await query.message.edit_text(
            text=gs(chat.id, "MAINTAINANCE_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_ping":
        await query.message.edit_text(
            text=gs(chat.id, "PING_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_play":
        await query.message.edit_text(
            text=gs(chat.id, "PLAY_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_shuffle":
        await query.message.edit_text(
            text=gs(chat.id, "SHUFFLE_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_seek":
        await query.message.edit_text(
            text=gs(chat.id, "SEEK_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_song":
        await query.message.edit_text(
            text=gs(chat.id, "SONG_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_speed":
        await query.message.edit_text(
            text=gs(chat.id, "SPEED_MUSIC"),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(MUSIC_BUTTON),
        )
    elif query.data == "Music_close":
        await query.message.delete()
        
    elif query.data == "Music_back":
        first_name = update.effective_user.first_name
        chat = update.effective_chat
        await query.message.edit_text(
            text=gs(chat.id, "PM_START_TEXT").format(escape_markdown(first_name),
                                 escape_markdown(context.bot.first_name)),
            reply_markup=InlineKeyboardMarkup(PM_START_BUTTON),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )



async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            await update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Help",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module,
                                ),
                            ),
                        ],
                    ],
                ),
            )
            return
        await update.effective_message.reply_text(
            "Choose an option for getting help.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="👤 Open in Private Chat",
                            url="t.me/{}?start=help".format(context.bot.username),
                            ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="👥️️ Open here",
                            callback_data="help_back",
                        ),
                    ],
                ],
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__,
            )
            + HELPABLE[module].__help__
        )
        await send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙", callback_data="help_back")]],
            ),
        )

    else:
        await send_help(chat.id, (gs(chat.id, "HELP_STRINGS")))


async def send_settings(chat: Chat | (int | str), user: User, update: Update, context:ContextTypes.DEFAULT_TYPE, is_user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user.id))
                for mod in USER_SETTINGS.values()
            )
            await application.bot.send_message(
                user.id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            await application.bot.send_message(
                user.id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            if not isinstance(chat, Chat):
                chat = await context.bot.get_chat(chat)

            conn = await connected(context.bot, update, chat, user.id, need_admin=True)

            chat_obj = await application.bot.getChat(conn)
            chat_name = chat_obj.title
            await application.bot.send_message(
                user.id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name,
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat.id),
                ),
            )
        else:
            await application.bot.send_message(
                user.id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )



async def settings_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = await bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__,
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            await query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="🔙",
                                callback_data="stngs_back({})".format(chat_id),
                            ),
                        ],
                    ],
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = await bot.get_chat(chat_id)
            await query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id,
                    ),
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = await bot.get_chat(chat_id)
            await query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id,
                    ),
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = await bot.get_chat(chat_id)
            await query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id),
                ),
            )

        # ensure no spinny white circle
        await bot.answer_callback_query(query.id)
        await query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings PM_START_BUTTON. %s", str(query.data))



async def get_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if await is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            await msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="👤 Get Settings in Private",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id,
                                ),
                            ),
                        ],
                    ],
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        await send_settings(chat, user, update, context, True)



async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_message.from_user
    first_name = update.effective_user.first_name 
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        await update.effective_message.reply_text(
            text=gs(chat.id, "DONATE_STRING").format(escape_markdown(first_name), 
                                 escape_markdown(context.bot.first_name)),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

        if OWNER_ID != 1930139488 and DONATION_LINK:
            await update.effective_message.reply_text(
                "You can also donate to the person currently running me"
                "[here]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

    else:
        try:
            await bot.send_message(
                user.id,
                text=gs(chat.id, "DONATE_STRING").format(escape_markdown(first_name), 
                                     escape_markdown(context.bot.first_name)),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            await update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!",
            )
        except Forbidden:
            await update.effective_message.reply_text(
                "Contact me in PM first to get donation information.",
            )



async def migrate_chats(update: Update, _: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        with contextlib.suppress(KeyError, AttributeError):
            mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise ApplicationHandlerStop


async def send_alive(context: ContextTypes.DEFAULT_TYPE):
    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            await context.bot.send_photo(
                f"@{SUPPORT_CHAT}",
                photo="https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg",
                caption=f"""
Hey Developer's {context.bot.first_name} is online now.

**Python :** `v{PYTHON_VERSION}`
**Telethon :** `v{TELETHON_VERSION}`
**Pyrogram :** `v{PYRO_VERSION}`
**Python Telegram Bot :** `v{PTB_VERSION}`
**Telegram Bot API :** `v{BOT_API_VERSION}`
**{BOT_NAME} :** `v{BOT_VERSION}`

⚡  𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚: @BotXNews
""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Forbidden:
            LOGGER.warning(
                f"Bot isn't able to send message to @{SUPPORT_CHAT}, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

def main():

    application.job_queue.run_repeating(send_alive, interval=86400, first=10)
    start_handler = CommandHandler("start", start, block=False)
    help_handler = CommandHandler("help", get_help, block=False)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*", block=False)
    settings_handler = CommandHandler("settings", get_settings, block=False)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_", block=False)
    about_callback_handler = CallbackQueryHandler(saif_about_callback, pattern=r"saif_", block=False)
    music_callback_handler = CallbackQueryHandler(music_about_callback, pattern=r"Music_", block=False)
    donate_handler = CommandHandler("donate", donate, block=False)
    migrate_handler = MessageHandler(filters.StatusUpdate.MIGRATE, migrate_chats, block=False)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(about_callback_handler)
    application.add_handler(music_callback_handler)
    application.add_handler(settings_handler)
    application.add_handler(help_callback_handler)
    application.add_handler(settings_callback_handler)
    application.add_handler(migrate_handler)
    application.add_handler(donate_handler)
    application.add_error_handler(error_callback)

    LOGGER.info("Using long polling.")
    application.run_polling(timeout=15, drop_pending_updates=False)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    LOGGER.info("Starting Telethon bot client")
    telethn.start(bot_token=TOKEN)
    LOGGER.info("Starting Pyrogram bot client")
    pyroclient.start()
    tracemalloc.start()
    main()
