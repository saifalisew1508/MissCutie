from MissCutie import pbot as app
from pyrogram import filters
from pyrogram import emoji
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

lengths = 200
IMG = "https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg"



@app.on_inline_query()
async def wishper_ai(_, query: InlineQuery):
    query_text = query.query
    split_query = query_text.split(' ', 1)

    if query_text == '' or len(query_text) > lengths or (query_text.startswith('@') and len(split_query) == 1):
        title = "🔐 Write a whisper message"
        content = (
            "**Send whisper messages through inline mode**\n\n"
            "Usage: `@MissCutieRobot [@username] text`"
        )
        description = "Usage: @MissCutieRobot [@username] text"
        button = InlineKeyboardButton(
            "More-Help",
            url="https://t.me/MissCutieRobot?start=learn"
        )
    elif not query_text.startswith('@'):
        title = f"{emoji.EYE} Whisper once to the first one who opens it"
        content = f"{emoji.EYE} The first one who opens the whisper can read it"
        description = f"{emoji.SHUSHING_FACE} {query_text}"
        button = InlineKeyboardButton(
            f"🎯 Show message",
            callback_data="show_whisper"
        )
    else:
        u_target = 'anyone' if (x := split_query[0]) == '@' else x
        title = f"🔒 A whisper message to {u_target}, Only he/she can open it."
        content = f"🔒 A whisper message to {u_target}, Only he/she can open it."
        description = f"{emoji.SHUSHING_FACE} {split_query[1]}"
        button = InlineKeyboardButton(
            f"{emoji.LOCKED_WITH_KEY} Show message",
            callback_data="show_whisper"
        )

    switch_pm_text = f"{emoji.INFORMATION} Learn how to send whispers"
    switch_pm_parameter = "learn"

    await query.answer(
        results=[
            InlineQueryResultArticle(
                title=title,
                input_message_content=InputTextMessageContent(content),
                description=description,
                thumb_url=IMG,
                reply_markup=InlineKeyboardMarkup([[button]])
            )
        ],
        switch_pm_text=switch_pm_text,
        switch_pm_parameter=switch_pm_parameter
    )

@app_on_callback_query(filters.regex("show_whisper"))
async def show_whisper(_,query):
        inline_message_id = query.inline_message_id
        whisper = whispers[inline_message_id]
        sender_uid = whisper['sender_uid']
        receiver_uname: Optional[str] = whisper['receiver_uname']
        whisper_text = whisper['text']
        from_user: User = query.from_user
        if receiver_uname and from_user.username \
            and from_user.username.lower() == receiver_uname.lower():
            return await query.answer(whisper_text, show_alert=True)
        if from_user.id == sender_uid or receiver_uname == '@':
            return await query.answer(whisper_text, show_alert=True) 
        if not receiver_uname:
            return await query.answer(whisper_text, show_alert=True)
        await query.answer("😶 This message is not for you", show_alert=True)
