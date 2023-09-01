
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


PM_START_BUTTON = [
    [
        InlineKeyboardButton(text="Help Menu", callback_data="help_back"),
        InlineKeyboardButton(text="Music Menu", callback_data="Music_"),
    ],
    [
        InlineKeyboardButton(text="About", callback_data="saif_"),
        InlineKeyboardButton(text="Manager", url=f"tg://user?id={OWNER_ID}"),
    ],
    [
        InlineKeyboardButton(text="Add Your Group ➕️", url=f"https://t.me/{application.bot.username}?startgroup=true"),
    ],
]



ABOUT_BUTTON = [
    [
        InlineKeyboardButton(text="About 🤖", callback_data="saif_"),
        InlineKeyboardButton(text="Commands ⚙️", callback_data="help_back"),
    ],
    [
        InlineKeyboardButton(text="Support 🌍", callback_data="saif_support"),
        InlineKeyboardButton(text="Sponsor Me ❤", callback_data="saif_sponsor"),
    ],
    [
        InlineKeyboardButton(text="Developers 🙋🏻", callback_data="saif_developer"),
        InlineKeyboardButton(text="Source 🤖", callback_data="saif_source"),
    ],
    [
        InlineKeyboardButton(text="🔙", callback_data="saif_back"),
        InlineKeyboardButton(text="🗑", callback_data="saif_close"),
    ],
]



MUSIC_BUTTON = [
    [
        InlineKeyboardButton(text="Admin", callback_data="Music_admin"),
        InlineKeyboardButton(text="Auth", callback_data="Music_auth"),
        InlineKeyboardButton(text="Broadcast", callback_data="Music_broadcast"),
    ],
    [
        InlineKeyboardButton(text="BL-Chat", callback_data="Music_blackchat"),
        InlineKeyboardButton(text="BL-User", callback_data="Music_blackuser"),
        InlineKeyboardButton(text="C-Play", callback_data="Music_cplay"),
    ],
    [
        InlineKeyboardButton(text="Gban", callback_data="Music_gban"),
        InlineKeyboardButton(text="Loop", callback_data="Music_loop"),
        InlineKeyboardButton(text="Maintainance", callback_data="Music_maintainance"),
    ],
    [
        InlineKeyboardButton(text="Ping", callback_data="Music_ping"),
        InlineKeyboardButton(text="Play", callback_data="Music_play"),
        InlineKeyboardButton(text="Shuffle", callback_data="Music_shuffle"),
    ],
    [
        InlineKeyboardButton(text="Seek", callback_data="Music_seek"),
        InlineKeyboardButton(text="Song", callback_data="Music_song"),
        InlineKeyboardButton(text="Speed", callback_data="Music_speed"),
    ],
    [
        InlineKeyboardButton(text="🔙", callback_data="saif_back"),
        InlineKeyboardButton(text="🗑", callback_data="Music_close"),
    ],
]