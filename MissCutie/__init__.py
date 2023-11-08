import logging
import os
import platform
import sys
import time
import asyncio
import telegram.ext as tg
import random

from telethon import __version__ as tlhver

# Pyrogram Imports
from pyrogram import __version__ as pyrover
from pyrogram import Client, errors
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, ChannelInvalid

from Python_ARQ import ARQ

from aiohttp import ClientSession

from telegram.ext import Application
from telegram.error import BadRequest, Forbidden
from telethon.sessions import MemorySession
from telethon import TelegramClient
from telegram import __bot_api_version__, __version__ as ptb_version
from dotenv import load_dotenv

#database version import 
from sqlalchemy import __version__ as sql_version
from pymongo import __version__ as mongo_version



try:
    from MissCutie.config import Development as Config
except:
    print("Can't import config!")


load_dotenv()

try:
    LOGGER_LEVEL = os.environ.get("LOGGER_LEVEL", 40)
    "logger level, `debug(10)`, `info(20)`, `warn(30)` and `error(40)`. default is `info`"
except:
    LOGGER_LEVEL = int(Config.LOGGER_LEVEL)

StartTime = time.time()

#setup logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=LOGGER_LEVEL
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

#python version check
if sys.version_info[0] < 3 or sys.version_info[1] < 9:
    print(
        "You MUST have a python version of at least 3.9, exiting..."
    )
    quit(1)

ENV = bool(os.environ.get("ENV", False))
BOT_VERSION = "5.0-Testing"
PTB_VERSION = ptb_version
PYRO_VERSION = pyrover
TELETHON_VERSION = tlhver
BOT_API_VERSION = __bot_api_version__
PYTHON_VERSION = platform.python_version()
SQL_VERSION = sql_version
MONGO_VERSION = mongo_version


TOKEN = "5810582849:AAHgoiQj1mr7ZYj7z8XcyOYfyGbBksvsLl4"
OWNER_ID = 6193432445
MONGO_DB_URI = "mongodb+srv://MissCutieRobot:MissCutieRobot@atlascluster.jzg32tp.mongodb.net/?retryWrites=true&w=majority"


if ENV:
#    TOKEN = os.environ.get("TOKEN", None)

#    try:
#        OWNER_ID = int(os.environ.get("OWNER_ID", None))
#    except ValueError:
#        raise Exception("Your OWNER_ID env variable is not a valid integer.")

    JOIN_LOGGER = os.environ.get("JOIN_LOGGER", None)
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", None)

    try:
        DRAGONS = set(int(x) for x in os.environ.get("DRAGONS", "").split())
        DEV_USERS = set(int(x) for x in os.environ.get("DEV_USERS", "").split())
    except ValueError:
        raise Exception("Your sudo or dev users list does not contain valid integers.")

    INFOPIC = bool(os.environ.get("INFOPIC", False))
    EVENT_LOGS = os.environ.get("EVENT_LOGS", None)
    WEBHOOK = bool(os.environ.get("WEBHOOK", False))
    URL = os.environ.get("URL", "")  # Does not contain token
    PORT = int(os.environ.get("PORT", 8443))
    CERT_PATH = os.environ.get("CERT_PATH")
    API_ID = os.environ.get("API_ID", None)
    API_HASH = os.environ.get("API_HASH", None)
    DONATION_LINK = os.environ.get("DONATION_LINK")
    LOAD = os.environ.get("LOAD", "").split()
    NO_LOAD = os.environ.get("NO_LOAD", "cleaner disasters").split()
    DEL_CMDS = bool(os.environ.get("DEL_CMDS", False))
    STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", False))
    WORKERS = int(os.environ.get("WORKERS", 8))
    BAN_STICKER = os.environ.get("BAN_STICKER", "CAACAgUAAxkBAAEDRNJhjolhBDkOeJLs2cPuhskKthnoQwACFwIAAs4DwFWTjimU8iDvqiIE")
    ALLOW_EXCL = os.environ.get("ALLOW_EXCL", False)
    TIME_API_KEY = os.environ.get("TIME_API_KEY", None)
    AI_API_KEY = os.environ.get("AI_API_KEY", None)
    WALL_API = os.environ.get("WALL_API", None)
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", None)
    ARQ_API_URL = os.environ.get("ARQ_API_URL", "https://arq.hamker.in")
    ARQ_API_KEY = os.environ.get("ARQ_API_KEY", "TLKINQ-XEVTPG-FQPEVU-ODUYVW-ARQ")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")
#    MONGO_DB_URI = os.environ.get("MONGO_DB_URI", None)
    ALLOW_CHATS = os.environ.get("ALLOW_CHATS", True)
    DB_URI = os.environ.get("DATABASE_URL")

    if DB_URI.startswith("postgres://"):
        DB_URI = DB_URI.replace("postgres://", "postgresql://")

    TEMP_DOWNLOAD_LOC = os.environ.get("TEMP_DOWNLOAD_LOC", "./Downloads")


    try:
        BL_CHATS = set(int(x) for x in os.environ.get("BL_CHATS", "").split())
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")

else:

#    TOKEN = Config.TOKEN

#    try:
#        OWNER_ID = int(Config.OWNER_ID)
#    except ValueError:
#        raise Exception("Your OWNER_ID variable is not a valid integer.")

    JOIN_LOGGER = Config.JOIN_LOGGER
    OWNER_USERNAME = Config.OWNER_USERNAME
    ALLOW_CHATS = Config.ALLOW_CHATS
    try:
        DRAGONS = set(int(x) for x in Config.DRAGONS or [])
        DEV_USERS = set(int(x) for x in Config.DEV_USERS or [])
    except ValueError:
        raise Exception("Your sudo or dev users list does not contain valid integers.")

    EVENT_LOGS = Config.EVENT_LOGS
    WEBHOOK = Config.WEBHOOK
    URL = Config.URL
    PORT = Config.PORT
    CERT_PATH = Config.CERT_PATH
    API_ID = Config.API_ID
    API_HASH = Config.API_HASH
    DONATION_LINK = Config.DONATION_LINK
    LOAD = Config.LOAD
    NO_LOAD = Config.NO_LOAD
    DEL_CMDS = Config.DEL_CMDS
    STRICT_GBAN = Config.STRICT_GBAN
    WORKERS = Config.WORKERS
    BAN_STICKER = Config.BAN_STICKER
    ALLOW_EXCL = Config.ALLOW_EXCL
    TIME_API_KEY = Config.TIME_API_KEY
    AI_API_KEY = Config.AI_API_KEY
    WALL_API = Config.WALL_API
    SUPPORT_CHAT = Config.SUPPORT_CHAT
    INFOPIC = Config.INFOPIC
    TEMP_DOWNLOAD_LOC = Config.TEMP_DOWNLOAD_LOC
    DB_URI = Config.SQLALCHEMY_DATABASE_URI 
#    MONGO_DB_URI = Config.MONGO_DB_URI
    ARQ_API_KEY = Config.ARQ_API_KEY
    OPENAI_API_KEY = Config.OPENAI_API_KEY

    if DB_URI.startswith("postgres://"):
        DB_URI = DB_URI.replace("postgres://", "postgresql://")

    try:
        BL_CHATS = set(int(x) for x in Config.BL_CHATS or [])
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")

DEV_USERS.add(OWNER_ID)

# Telethon Client
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)

# Pyrogram Client
pyroclient = Client(
    "MissCutie",
    API_ID,
    API_HASH,
    bot_token=TOKEN,
    no_updates= True
)
aiohttpsession = ClientSession()
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)


application = Application.builder().token(TOKEN).concurrent_updates(True).build()
asyncio.get_event_loop().run_until_complete(application.bot.initialize())

DRAGONS = list(DRAGONS) + list(DEV_USERS)
DEV_USERS = list(DEV_USERS)

# Bot Info
LOGGER.info("Getting Bot Info")
BOT_ID = application.bot.id
BOT_NAME = application.bot.first_name
BOT_USERNAME = application.bot.username
BOT_PIC = application.bot.get_user_profile_photos



# Don't edit below this line

YTDOWNLOADER = 1




# Load at end to ensure all prev variables have been set
from MissCutie.modules.helper_funcs.handlers import (
    CustomCommandHandler,
    CustomMessageHandler,
)

# make sure the regex handler can take extra kwargs

tg.CommandHandler = CustomCommandHandler
tg.MessageHandler = CustomMessageHandler
