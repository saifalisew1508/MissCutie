import json
import logging
import os


def get_user_list(config, key):
    with open("{}/MissCutie/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


# Create a new config.py or rename this to config.py file in the same dir and import, then extend this class.
class Config(object):
    ALLOW_CHATS = True
    ALLOW_EXCL = True
    API_HASH = "d54a6609d5cc5ba0094ee206791e1490"
    API_ID = 23738177  # integer value, don't use ""
    ARQ_API_KEY = "TLKINQ-XEVTPG-FQPEVU-ODUYVW-ARQ"
    BAN_STICKER = ""  # banhammer marie sticker id, the bot will send this sticker before banning or kicking a user in chat.
    CERT_PATH = None
    DEL_CMDS = True  # Delete commands that users don't have access to, like delete /ban if a non-admin uses it.
    DEV_USERS = get_user_list("elevated_users.json", "devs")
    DONATION_LINK = None  # EG, PayPal
    DRAGONS = get_user_list("elevated_users.json", "sudos")
    EVENT_LOGS = -1001660668029
    INFOPIC = True
    JOIN_LOGGER = -1001660668029
    LOAD = []
    LOGGER = True
    LOGGER_LEVEL = logging.INFO
    MONGO_DB_URI = "MONGO_DB_URI"
    MONGO_DB_NAME = "Cutie"
    NO_LOAD = None
    OPENAI_API_KEY = "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"
    OWNER_ID = 5982904247  # If you don't know, run the bot and do /id in your private chat with it, also an integer
    OWNER_USERNAME = "LostedPerson"
    PORT = 5000
    SQLALCHEMY_DATABASE_URI = "something://somewhat:user@hosturl:port/databasename"  # needed for any database modules
    STRICT_GBAN = True
    SUPPORT_CHAT = "PublicSource_Chat"  # Your own group for support, do not add the @
    TELETHON_VERSION = "1.0.0"
    TEMP_DOWNLOAD_LOC = "./Downloads"
    TIME_API_KEY = "awoo"  # Get your API key from https://timezonedb.com/api
    TOKEN = "BOT_TOKEN"  # This var used to be API_KEY but it is now TOKEN, adjust accordingly.
    URL = None
    WEBHOOK = False
    WALL_API = "awoo"  # For wallpapers, get one from https://wall.alphacoders.com/api.php
    WORKERS = 8  # Number of subthreads to use. Set as the number of threads your processor uses

    BL_CHATS = []  # List of groups that you want blacklisted.
    SPAMMERS = None


class Development(Config):
    LOGGER = True


class Production(Config):
    LOGGER = True
