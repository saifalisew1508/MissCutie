from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import functions, types
from telethon.tl.types import ChatBannedRights

from MissCutie import telethn as tbot
from MissCutie.events import register
from MissCutie.modules.sql.night_mode_sql import (
    add_nightmode,
    get_all_chat_id,
    is_nightmode_indb,
    rmnightmode,
)

hehes = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)

openhehe = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=False,
    pin_messages=False,
    change_info=False,
)


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        participant = await tbot(functions.channels.GetParticipantRequest(chat, user))
        return isinstance(
            participant.participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    elif isinstance(chat, types.InputPeerChat):
        ui = await tbot.get_peer_id(user)
        full_chat = await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ps = full_chat.full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    else:
        return None


@register(pattern="^/nightmode")
async def close_ws(event):
    if event.is_group:
        if not await is_register_admin(event.input_chat, event.message.sender_id):
            await event.reply("🤦🏻‍♂️ You are not an admin, so you can't use this command...")
            return
    else:
        await event.reply("You can only enable Night Mode in groups.")
        return

    if is_nightmode_indb(str(event.chat_id)):
        await event.reply("This chat has already enabled Night Mode.")
        return

    add_nightmode(str(event.chat_id))
    await event.reply(
        f"Added chat {event.chat.title} with ID {event.chat_id} to the database. **This group will be closed from 12 AM (IST) and will be opened at 6 AM (IST)**"
    )


@register(pattern="^/rmnight")
async def disable_ws(event):
    if event.is_group:
        if not await is_register_admin(event.input_chat, event.message.sender_id):
            await event.reply("🤦🏻‍♂️ You are not an admin, so you can't use this command...")
            return
    else:
        await event.reply("You can only disable Night Mode in groups.")
        return

    if not is_nightmode_indb(str(event.chat_id)):
        await event.reply("This chat has not enabled Night Mode.")
        return

    rmnightmode(str(event.chat_id))
    await event.reply(
        f"Removed chat {event.chat.title} with ID {event.chat_id} from the database."
    )


async def job_close():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                "12:00 AM, the group is closing till 6 AM. Night Mode started! \n**Powered By {BOT_NAME}**",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=hehes
                )
            )
        except Exception as e:
            logger.info(f"Unable to close group {warner} - {e}")


# Run every day at 12 AM
scheduler_close = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler_close.add_job(job_close, trigger="cron", hour=23, minute=59)
scheduler_close.start()


async def job_open():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                "6:00 AM, the group is opening.\n**Powered By {BOT_NAME}**",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=openhehe
                )
            )
        except Exception as e:
            logger.info(f"Unable to open group {warner.chat_id} - {e}")


# Run every day at 6 AM
scheduler_open = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler_open.add_job(job_open, trigger="cron", hour=6, minute=1)
scheduler_open.start()

from MissCutie.modules.language import gs


def get_help(chat):
    return gs(chat, "nightmode_help")
__mod_name__ = "Night-Mode"
