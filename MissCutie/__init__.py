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


load_dotenv()

try:
    LOGGER_LEVEL = os.environ.get("LOGGER_LEVEL", 30)
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
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

#python version check
if sys.version_info[0] < 3 or sys.version_info[1] < 9:
    print(
        "You MUST have a python version of at least 3.9, exiting..."
    )
    quit(1)

ENV = bool(os.environ.get("ENV", False))

if ENV:
    # Extract environment variables...
    ALLOW_CHATS = os.environ.get("ALLOW_CHATS", True)
    ALLOW_EXCL = os.environ.get("ALLOW_EXCL", False)
    API_HASH = os.environ.get("API_HASH", None)
    API_ID = os.environ.get("API_ID", None)
    ARQ_API_KEY = os.environ.get("ARQ_API_KEY", "TLKINQ-XEVTPG-FQPEVU-ODUYVW-ARQ")
    ARQ_API_URL = os.environ.get("ARQ_API_URL", "https://arq.hamker.in")
    BAN_STICKER = os.environ.get("BAN_STICKER", "CAACAgUAAxkBAAEDRNJhjolhBDkOeJLs2cPuhskKthnoQwACFwIAAs4DwFWTjimU8iDvqiIE")
    CERT_PATH = os.environ.get("CERT_PATH")
    DB_URI = os.environ.get("DATABASE_URL")
    DEL_CMDS = bool(os.environ.get("DEL_CMDS", False))
    DONATION_LINK = os.environ.get("DONATION_LINK")
    EVENT_LOGS = os.environ.get("EVENT_LOGS", None)
    INFOPIC = bool(os.environ.get("INFOPIC", False))
    JOIN_LOGGER = os.environ.get("JOIN_LOGGER", None)
    LOAD = os.environ.get("LOAD", "").split()
    LOGGER_LEVEL = int(os.environ.get("LOGGER_LEVEL", 30))
    MONGO_DB_URI = os.environ.get("MONGO_DB_URI", None)
    NO_LOAD = os.environ.get("NO_LOAD", "cleaner disasters").split()
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", None)
    PORT = int(os.environ.get("PORT", 8443))
    STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", False))
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", None)
    TEMP_DOWNLOAD_LOC = os.environ.get("TEMP_DOWNLOAD_LOC", "./Downloads")
    TIME_API_KEY = os.environ.get("TIME_API_KEY", None)
    TOKEN = os.environ.get("TOKEN", None)
    URL = os.environ.get("URL", "")  # Does not contain token
    WALL_API = os.environ.get("WALL_API", None)
    WEBHOOK = bool(os.environ.get("WEBHOOK", False))
    WORKERS = int(os.environ.get("WORKERS", 8))
    
    if DB_URI.startswith("postgres://"):
        DB_URI = DB_URI.replace("postgres://", "postgresql://")
        
    try:
        OWNER_ID = int(os.environ.get("OWNER_ID", None))
    except ValueError:
        raise Exception("Your OWNER_ID env variable is not a valid integer.")

    try:
        DRAGONS = set(int(x) for x in os.environ.get("DRAGONS", "").split())
        DEV_USERS = set(int(x) for x in os.environ.get("DEV_USERS", "").split())
    except ValueError:
        raise Exception("Your sudo or dev users list does not contain valid integers.")

    try:
        BL_CHATS = set(int(x) for x in os.environ.get("BL_CHATS", "").split())
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")


else:
    try:
        from MissCutie.config import Development as Config
    except:
        print("Can't import config!")
        
    # Use config from Development...
    ALLOW_CHATS = Config.ALLOW_CHATS
    ALLOW_EXCL = Config.ALLOW_EXCL
    API_HASH = Config.API_HASH
    API_ID = Config.API_ID
    ARQ_API_KEY = Config.ARQ_API_KEY
    ARQ_API_URL = Config.ARQ_API_URL
    BAN_STICKER = Config.BAN_STICKER
    CERT_PATH = Config.CERT_PATH
    DB_URI = Config.SQLALCHEMY_DATABASE_URI
    DEL_CMDS = Config.DEL_CMDS
    DONATION_LINK = Config.DONATION_LINK
    EVENT_LOGS = Config.EVENT_LOGS
    INFOPIC = Config.INFOPIC
    JOIN_LOGGER = Config.JOIN_LOGGER
    LOAD = Config.LOAD
    LOGGER_LEVEL = int(Config.LOGGER_LEVEL)
    MONGO_DB_URI = Config.MONGO_DB_URI
    NO_LOAD = Config.NO_LOAD
    OWNER_USERNAME = Config.OWNER_USERNAME
    PORT = Config.PORT
    STRICT_GBAN = Config.STRICT_GBAN
    SUPPORT_CHAT = Config.SUPPORT_CHAT
    TEMP_DOWNLOAD_LOC = Config.TEMP_DOWNLOAD_LOC
    TIME_API_KEY = Config.TIME_API_KEY
    TOKEN = Config.TOKEN
    URL = Config.URL
    WALL_API = Config.WALL_API
    WEBHOOK = Config.WEBHOOK
    WORKERS = Config.WORKERS
    
    if DB_URI.startswith("postgres://"):
        DB_URI = DB_URI.replace("postgres://", "postgresql://")
    
    try:
        OWNER_ID = int(Config.OWNER_ID)
    except ValueError:
        raise Exception("Your OWNER_ID variable is not a valid integer.")

    try:
        BL_CHATS = set(int(x) for x in Config.BL_CHATS or [])
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")

    try:
        DRAGONS = set(int(x) for x in Config.DRAGONS or [])
        DEV_USERS = set(int(x) for x in Config.DEV_USERS or [])
    except ValueError:
        raise Exception("Your sudo or dev users list does not contain valid integers.")


# Telethon Client
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)

# Pyrogram Client
app = Client("Cutie", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)
aiohttpsession = ClientSession()

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

# Load at end to ensure all prev variables have been set
from MissCutie.modules.helper_funcs.handlers import (
    CustomCommandHandler,
    CustomMessageHandler,
)

# make sure the regex handler can take extra kwargs
tg.CommandHandler = CustomCommandHandler
tg.MessageHandler = CustomMessageHandler
