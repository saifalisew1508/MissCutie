from telethon import *
from telethon.tl.types import InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telethon.tl.functions.messages import SetInlineBotResultsRequest
from telethon.tl.functions.users import GetUsersRequest
from telethon.tl.types import InputUserSelf, InputUser
from telethon.tl.functions.users import GetFullUserRequest
from MissCutie import telethn as client

    lengths = 200
    IMG = "https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg"

    @client.on(events.InlineQuery)
    async def wishper_ai(event):
        query = event.query
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
                data="show_whisper"
            )
        else:
            u_target = 'anyone' if (x := split_query[0]) == '@' else x
            title = f"🔒 A whisper message to {u_target}, Only he/she can open it."
            content = f"🔒 A whisper message to {u_target}, Only he/she can open it."
            description = f"{emoji.SHUSHING_FACE} {split_query[1]}"
            button = Button.inline('Show Message', b'show_whisper')


        switch_pm_text = f"{emoji.INFORMATION} Learn how to send whispers"
        switch_pm_parameter = "learn"

        result = [
            await client(
                GetFullUserRequest(
                    await client(
                        GetUsersRequest(
                            [InputUserSelf()]
                        )
                    )
                )
            )
        ]
        await client(
            SetInlineBotResultsRequest(
                query_id=event.query.id,
                results=[
                    InputBotInlineResult(
                        id='0',
                        type='article',
                        title=title,
                        input_message_content=InputTextMessageContent(content),
                        description=description,
                        url=IMG,
                        thumb='https://te.legra.ph/file/5196d5fa658145cb6b9ef.jpg',
                        reply_markup=button
                    )
                ],
                switch_pm_text=switch_pm_text,
                switch_pm_parameter=switch_pm_parameter
            )
        )
