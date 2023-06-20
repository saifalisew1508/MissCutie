import importlib
import contextlib
import time
import re
import random

from MissCutie import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,
    PYTHON_VERSION,
    BOT_VERSION,
    PTB_VERSION,
    BOT_API_VERSION,
    PYRO_VERSION,
    TELETHON_VERSION,
    application,
    StartTime,
    telethn,
    pbot)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
import MissCutie.modules.sql.users_sql as sql
from MissCutie.modules import ALL_MODULES
from MissCutie.modules.helper_funcs.chat_status import is_user_admin
from MissCutie.modules.helper_funcs.misc import paginate_modules
from MissCutie.modules.connection import connected
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


PM_START_TEXT = """
*Hey* {} there! My name is *{}* - I'm here to help you manage your groups! Hit /help to find out more about how to use me to my full potential.

Join my [updates channel](http://t.me/BotXNews) to get information on all the latest updates.

Use the /donate command to donate our devlopers
"""

buttons = [
    [
        InlineKeyboardButton(text="Commands", callback_data="help_back"),
        InlineKeyboardButton(text="Music", callback_data="Music_"),
    ],
    [
        InlineKeyboardButton(text="About", callback_data="saif_"),
        InlineKeyboardButton(text="Updates", url="t.me/BotXNews"),
    ],
    [
        InlineKeyboardButton(
            text="Add Your Group",
            url=f"https://t.me/{application.bot.username}?startgroup=true",
        ),
    ],
]

HELP_STRINGS = """
Hey there! My name is *{}*.
I'm a modular group management bot with a few fun extras! Have a look at the following for an idea of some of \
the things I can help you with.
*Main* commands available:
 - /start: start the bot
 - /help: PM's you this message.
 - /help <module name>: PM's you info about that module.
 - /donate: information about how to donate!
 - /settings:
   - in PM: will send you your settings for all supported modules.
   - in a group: will redirect you to pm, with all that chat's settings.
{}
And the following:
""".format(application.bot.first_name, "" if not ALLOW_EXCL else "\nAll commands can either be used with / or !.\n")


DONATE_STRING = """Hey {},
So you want to donate {} ? Amazing!
You can donate on [PayPal](https://paypal.me/saifalisew1508), or you can set up a recurring donation on [GitHub Sponsors](https://github.com/sponsors/saifalisew1508). **UPI :** `saif.9@paytm` if you have any other way to donate contact at @PrinceXofficial ,
This project is entirely run by volunteers, and server fees aren't cheap, so we thank you for your support!."""

MUSIC_TEXT = """Heyaaaa {},

Click on the buttons below for more information. If you're facing any problem in command you can contact my bot owner or ask in support chat.

*Note ➨* Due to Music Bot and Modular Group Help Bot running on the same server it may be possible that sometimes Music Bot may slow down. Don't worry this is a temporary problem it will be fixed soon by our developers and server managers.

Enjoy With {}

All commands can be used with: /
"""

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
                        [[InlineKeyboardButton(text="◁", callback_data="help_back")]],
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

            await update.effective_message.reply_text(
                PM_START_TEXT.format(escape_markdown(first_name),
                                     escape_markdown(context.bot.first_name)),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        await update.effective_message.reply_photo(
            START_IMG,
            caption="i am alive   !\n<b>i didn't slept since​:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
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
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)


    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "*Available Commands for* *{}* :\n".format(
                    HELPABLE[module].__mod_name__,
                )
                + HELPABLE[module].__help__
            )
            await query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="◁", callback_data="help_back")]],
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help"),
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help"),
                ),
            )

        elif back_match:
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help"),
                ),
            )

        # ensure no spinny white circle
        await context.bot.answer_callback_query(query.id)
        # await query.message.delete()

    except BadRequest:
        pass



async def saif_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "saif_":
        uptime = get_readable_time((time.time() - StartTime))
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            text=f"*Hey Buddy, My name is {context.bot.first_name}*"
            "\n*This is a Bot developed in Python using Telethon, Pyrogram and PTB Library. it's online since 09 January 2022 and it's constantly updated!*"
            "\n*Written in Python with SQLalchemy and MongoDB as database.*"
            "\n\nAbout bot Library, Databse Users and Chats"
            f"\n*➥ Python          :* {PYTHON_VERSION}"
            f"\n*➥ Pyrogram     :* {PYRO_VERSION}"
            f"\n*➥ Telethon       :* {TELETHON_VERSION}"
            f"\n*➥ PTB Library  :* {PTB_VERSION}"
            f"\n*➥ Uptime          :* {uptime}"
            f"\n*➥ Total Users  :* {sql.num_users()}"
            f"\n*➥ Total Chats  :* {sql.num_chats()}"
            "\n\n*Bot Admins.*"
            "\n• @PrinceXofficial, bot creator and main developer."
            "\n\n__⚠️ The bot staff cannot assist you in situations involving groups using this bot.__"
            "\n\n*Supporters*"
            "\n• [Click here](http://t.me/MissCutieUpdates) to consult the updated list of Official Supporters of the bot."
            "\n\n• Thanks to all our donors for supporting server and development expenses and all those who have reported bugs or suggested new features."
            "\n• We also thank all the groups who rely on our Bot for this service, we hope you will always like it: we are constantly working to improve it!"
            f"\n\nClick on the *Commands* buttons given below for getting basic help and info about {context.bot.first_name}.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Support", callback_data="saif_support"
                        ),
                        InlineKeyboardButton(
                            text="Commands", callback_data="help_back"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Developer", url="https://t.me/PrinceXofficial"
                        ),
                        InlineKeyboardButton(
                            text="Source",
                            url="https://github.com/saifalisew1508/MissCutieRobot",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="◁", callback_data="saif_back"),
                    ],
                ]
            ),
        )
    elif query.data == "saif_support":
        await query.message.edit_text(
            text="*Click on the buttons given below to get help and more information about me.*"
            f"\n\nIf you found any bug in {context.bot.first_name} or if you wanna give feedback about the {context.bot.first_name}, please report it at support chat.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Support", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                        InlineKeyboardButton(
                            text="Updates", url=f"https://t.me/BotXNews"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Developer", url="https://t.me/PrinceXofficial"
                        ),
                        InlineKeyboardButton(
                            text="Github", url="https://github.com/saifalisew1508"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="◁", callback_data="saif_"),
                    ],
                ]
            ),
        )
    elif query.data == "saif_back":
        first_name = update.effective_user.first_name 
        await query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name), 
                                 escape_markdown(context.bot.first_name)),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )



async def Music_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    first_name = update.effective_user.first_name 
    if query.data == "Music_":
        await query.message.edit_text(
            text=MUSIC_TEXT.format(escape_markdown(first_name), 
                                   escape_markdown(context.bot.first_name)),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=" Admin ", callback_data="Music_admin"
                        ),
                        InlineKeyboardButton(
                            text=" Play ", callback_data="Music_play"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text=" Bot ", callback_data="Music_bot"),
                        InlineKeyboardButton(
                            text=" Extra ",
                            callback_data="Music_extra",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="◁", callback_data="saif_back"),
                    ],
                ]
            ),
        )
    elif query.data == "Music_admin":
        await query.message.edit_text(
            text=f"*Admin Commands*"
            f"""
**c** stands for channel play.

/pause or /cpause - Pause the playing music.
/resume or /cresume- Resume the paused music.
/mute or /cmute- Mute the playing music.
/unmute or /cunmute- Unmute the muted music.
/skip or /cskip- Skip the current playing music.
/stop or /cstop- Stop the playing music.
/shuffle or /cshuffle- Randomly shuffles the queued playlist.
/seek or /cseek - Forward Seek the music to your duration
/seekback or /cseekback - Backward Seek the music to your duration
/restart - Restart bot for your chat .


✅<u>**Specific Skip:**</u>
/skip or /cskip [Number(example: 3)] 
    - Skips music to a the specified queued number. Example: /skip 3 will skip music to third queued music and will ignore 1 and 2 music in queue.

✅<u>**Loop Play:**</u>
/loop or /cloop [enable/disable] or [Numbers between 1-10] 
    - When activated, bot loops the current playing music to 1-10 times on voice chat. Default to 10 times.

✅<u>**Auth Users:**</u>
Auth Users can use admin commands without admin rights in your chat.

/auth [Username] - Add a user to AUTH LIST of the group.
/unauth [Username] - Remove a user from AUTH LIST of the group.
/authusers - Check AUTH LIST of the group.
""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="Back", callback_data="Music_"),
                    ]
                ]
            ),
        )
    elif query.data == "Music_play":
        await query.message.edit_text(
            text=f"*Play Commands*"
            f"""
Available Commands = play , vplay , cplay

ForcePlay Commands = playforce , vplayforce , cplayforce

**c** stands for channel play.
**v** stands for video play.
**force** stands for force play.

/play or /vplay or /cplay  - Bot will start playing your given query on voice chat or Stream live links on voice chats.

/playforce or /vplayforce or /cplayforce -  **Force Play** stops the current playing track on voice chat and starts playing the searched track instantly without disturbing/clearing queue.

/channelplay [Chat username or id] or [Disable] - Connect channel to a group and stream music on channel's voice chat from your group.


✅**<u>Bot's Server Playlists:</u>**
/playlist  - Check Your Saved Playlist On Servers.
/deleteplaylist - Delete any saved music in your playlist
/play  - Start playing Your Saved Playlist from Servers.
""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="Back", callback_data="Music_"),
                    ]
                ]
            ),
        )
    elif query.data == "Music_bot":
        await query.message.edit_text(
            text=f"*Bot Commands*"
            f"""
/stats - Get Top 10 Tracks Global Stats, Top 10 Users of bot, Top 10 Chats on bot, Top 10 Played in a chat etc etc.

/sudolist - Check Sudo Users of Yukki Music Bot

/lyrics [Music Name] - Searches Lyrics for the particular Music on web.

/song [Track Name] or [YT Link] - Download any track from youtube in mp3 or mp4 formats.

/player -  Get a interactive Playing Panel.

**c** stands for channel play.

/queue or /cqueue- Check Queue List of Music.
""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="Back", callback_data="Music_"),
                    ]
                ]
            ),
        )
    elif query.data == "Music_extra":
        await query.message.edit_text(
            text=f"*Extra Commands *"
            f"""
/start - Start the Music Bot.
/help  - Get Commands Helper Menu with detailed explanations of commands.
/ping- Ping the Bot and check Ram, Cpu etc stats of Bot.

✅<u>**Group Settings:**</u>
/settings - Get a complete group's settings with inline buttons

🔗 **Options in Settings:**

1️⃣ You can set **Audio Quality** you want to stream on voice chat.

2️⃣ You can set **Video Quality** you want to stream on voice chat.

3️⃣ **Auth Users**:- You can change admin commands mode from here to everyone or admins only. If everyone, anyone present in you group will be able to use admin commands(like /skip, /stop etc)

4️⃣ **Clean Mode:** When enabled deletes the bot's messages after 5 mins from your group to make sure your chat remains clean and good.

5️⃣ **Command Clean** : When activated, Bot will delete its executed commands (/play, /pause, /shuffle, /stop etc) immediately.

6️⃣ **Play Settings:**

/playmode - Get a complete play settings panel with buttons where you can set your group's play settings. 

<u>Options in playmode:</u>

1️⃣ **Search Mode** [Direct or Inline] - Changes your search mode while you give /play mode. 

2️⃣ **Admin Commands** [Everyone or Admins] - If everyone, anyone present in you group will be able to use admin commands(like /skip, /stop etc)

3️⃣ **Play Type** [Everyone or Admins] - If admins, only admins present in group can play music on voice chat.
""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="Back", callback_data="Music_"),
                    ]
                ]
            ),
        )
    elif query.data == "Music_back":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name),
                                 escape_markdown(context.bot.first_name)),
            reply_markup=InlineKeyboardMarkup(buttons),
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
                            text="Open in private",
                            url="t.me/{}?start=help".format(context.bot.username),
                            ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Open here",
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
                [[InlineKeyboardButton(text="◁", callback_data="help_back")]],
            ),
        )

    else:
        await send_help(chat.id, HELP_STRINGS)


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
                                text="◁",
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
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))



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
                                text="settings",
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
            DONATE_STRING.format(escape_markdown(first_name), 
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
                DONATE_STRING.format(escape_markdown(first_name), 
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
Hey developer's {context.bot.first_name} online now.

**Python      : {PYTHON_VERSION}**
**Telethon    : {TELETHON_VERSION}**
**Pyrogram    : {PYRO_VERSION}**
**Python-Telegram-Bot :** {PTB_VERSION}**

Presented By @BotXNews
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
    
    application.job_queue.run_repeating(send_alive, interval=3600, first=10)

    start_handler = CommandHandler("start", start, block=False)

    help_handler = CommandHandler("help", get_help, block=False)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*", block=False)

    settings_handler = CommandHandler("settings", get_settings, block=False)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_", block=False)

    about_callback_handler = CallbackQueryHandler(saif_about_callback, pattern=r"saif_", block=False)
    Music_callback_handler = CallbackQueryHandler(Music_about_callback, pattern=r"Music_", block=False)

    donate_handler = CommandHandler("donate", donate, block=False)
    migrate_handler = MessageHandler(filters.StatusUpdate.MIGRATE, migrate_chats, block=False)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(about_callback_handler)
    application.add_handler(Music_callback_handler)
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
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
