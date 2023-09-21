from MissCutie import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Emojis
HELP_ICON = "❓"
MUSIC_ICON = "🎵"
ABOUT_ICON = "ℹ️"
MANAGER_ICON = "👤"
ADD_GROUP_ICON = "➕"
BACK_ICON = "🔙"
CLOSE_ICON = "🗑"
ABOUT_BOT_ICON = "🤖"
COMMANDS_ICON = "⚙️"
SUPPORT_ICON = "🌍"
SPONSOR_ICON = "❤️"
DEVELOPERS_ICON = "🙋‍♂️"
SOURCE_ICON = "🔍"

PM_START_BUTTON = [
    [
        InlineKeyboardButton(text=f"{HELP_ICON} Help Menu", callback_data="help_back"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} Music Menu", callback_data="Music_"),
    ],
    [
        InlineKeyboardButton(text=f"{ABOUT_ICON} About", callback_data="saif_"),
        InlineKeyboardButton(text=f"{MANAGER_ICON} Manager", url=f"tg://user?id={OWNER_ID}"),
    ],
    [
        InlineKeyboardButton(text=f"{ADD_GROUP_ICON} Add Your Group", url=f"https://t.me/{application.bot.username}?startgroup=true"),
    ],
]

ABOUT_BUTTON = [
    [
        InlineKeyboardButton(text=f"{ABOUT_BOT_ICON} About", callback_data="saif_"),
        InlineKeyboardButton(text=f"{COMMANDS_ICON} Commands", callback_data="help_back"),
    ],
    [
        InlineKeyboardButton(text=f"{SUPPORT_ICON} Support", callback_data="saif_support"),
        InlineKeyboardButton(text=f"{SPONSOR_ICON} Sponsor Me", callback_data="saif_sponsor"),
    ],
    [
        InlineKeyboardButton(text=f"{DEVELOPERS_ICON} Developers", callback_data="saif_developer"),
        InlineKeyboardButton(text=f"{SOURCE_ICON} Source", callback_data="saif_source"),
    ],
    [
        InlineKeyboardButton(text=f"{BACK_ICON}", callback_data="saif_back"),
        InlineKeyboardButton(text=f"{CLOSE_ICON}", callback_data="saif_close"),
    ],
]

MUSIC_BUTTON = [
    [
        InlineKeyboardButton(text=f"{MUSIC_ICON} Admin", callback_data="Music_admin"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} Auth", callback_data="Music_auth"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} Broadcast", callback_data="Music_broadcast"),
    ],
    [
        InlineKeyboardButton(text=f"{MUSIC_ICON} BL-Chat", callback_data="Music_blackchat"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} BL-User", callback_data="Music_blackuser"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} C-Play", callback_data="Music_cplay"),
    ],
    [
        InlineKeyboardButton(text=f"{MUSIC_ICON} Gban", callback_data="Music_gban"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} Loop", callback_data="Music_loop"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} Maintenance", callback_data="Music_maintenance"),
    ],
    [
        InlineKeyboardButton(text=f"{MUSIC_ICON} Ping", callback_data="Music_ping"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} Play", callback_data="Music_play"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} Shuffle", callback_data="Music_shuffle"),
    ],
    [
        InlineKeyboardButton(text=f"{MUSIC_ICON} Seek", callback_data="Music_seek"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} Song", callback_data="Music_song"),
        InlineKeyboardButton(text=f"{MUSIC_ICON} Speed", callback_data="Music_speed"),
    ],
    [
        InlineKeyboardButton(text=f"{BACK_ICON}", callback_data="saif_back"),
        InlineKeyboardButton(text=f"{CLOSE_ICON}", callback_data="Music_close"),
    ],
]
