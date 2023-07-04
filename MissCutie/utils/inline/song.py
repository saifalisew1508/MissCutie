from pyrogram.types import InlineKeyboardButton


def song_markup(_, vidid):
    return [
        [
            InlineKeyboardButton(
                text=_["🔊 Audio"],
                callback_data=f"song_helper audio|{vidid}",
            ),
            InlineKeyboardButton(
                text=_["🎥 Video"],
                callback_data=f"song_helper video|{vidid}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["🗑 Close"], callback_data="close"
            ),
        ],
    ]
