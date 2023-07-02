import os
from time import sleep

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telethon import *
from telethon.errors import *
from telethon.errors import FloodWaitError, UserNotParticipantError
from telethon.tl import *
from telethon.tl import functions, types
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import *
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
    ChatBannedRights,
)

from MissCutie import *
from MissCutie import LOGGER
from MissCutie.events import register, callbackquery

sudo = 1930139488
BOT_ID = 5071423206
CMD_HELP = "/ !"


# ================================================


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await telethn(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


@register(pattern="^/unbanall$")
async def unban_all(event):
    chat = await event.get_chat()
    admin = chat.admin_rights.ban_users
    creator = chat.creator
    if event.is_private:
        return await event.respond(
            "__This command can be used in groups and channels!__"
        )

    is_admin = False
    try:
        cutiepii = await telethn(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            cutiepii.participant,
            (
                ChannelParticipantAdmin,
                ChannelParticipantCreator,
            ),
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("__Only admins can unban all members!__")

    if not admin and not creator:
        await event.reply("`I don't have enough permissions!`")
        return

    done = await event.reply("Searching for banned participants...")
    p = 0
    async for i in telethn.iter_participants(
        event.chat_id, filter=ChannelParticipantsKicked, aggressive=True
    ):
        rights = ChatBannedRights(until_date=0, view_messages=False)
        try:
            await telethn(
                functions.channels.EditBannedRequest(event.chat_id, i, rights)
            )
        except FloodWaitError as ex:
            LOGGER.warn(f"Sleeping for {ex.seconds} seconds")
            sleep(ex.seconds)
        except Exception as ex:
            await event.reply(str(ex))
        else:
            p += 1

    if p == 0:
        await done.edit("No one is banned in this chat.")
        return
    required_string = "Successfully unbanned **{}** users."
    await event.reply(required_string.format(p))


@register(pattern="^/unmuteall$")
async def unmute_all(event):
    if event.is_private:
        return await event.respond(
            "__This command can be used in groups and channels!__"
        )

    is_admin = False
    try:
        cutiepii = await telethn(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            cutiepii.participant,
            (
                ChannelParticipantAdmin,
                ChannelParticipantCreator,
            ),
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("__Only admins can unmute all members!__")

    chat = await event.get_chat()
    admin = chat.admin_rights.ban_users
    creator = chat.creator

    if not admin and not creator:
        await event.reply("`I don't have enough permissions!`")
        return

    done = await event.reply("Working...")
    p = 0
    async for i in telethn.iter_participants(
        event.chat_id, filter=ChannelParticipantsBanned, aggressive=True
    ):
        rights = ChatBannedRights(
            until_date=0,
            send_messages=False,
        )
        try:
            await telethn(
                functions.channels.EditBannedRequest(event.chat_id, i, rights)
            )
        except FloodWaitError as ex:
            LOGGER.warn(f"Sleeping for {ex.seconds} seconds")
            sleep(ex.seconds)
        except Exception as ex:
            await event.reply(str(ex))
        else:
            p += 1

    if p == 0:
        await done.edit("No one is muted in this chat.")
        return
    required_string = "Successfully unmuted **{}** users."
    await event.reply(required_string.format(p))


@register(pattern="^/deleteall$")
async def delete_all_messages(event):
    chat = await event.get_chat()
    admin = chat.admin_rights.delete_messages
    creator = chat.creator

    if event.is_private:
        return await event.respond(
            "__This command can be used in groups and channels only!__"
        )

    is_admin = False
    try:
        cutiepii = await telethn(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            cutiepii.participant,
            (
                ChannelParticipantAdmin,
                ChannelParticipantCreator,
            ),
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("__Only admins can delete all messages!__")

    if not admin and not creator:
        await event.reply("`I don't have enough permissions!`")
        return

    done = await event.reply("Deleting all messages...")
    async for message in telethn.iter_messages(event.chat_id):
        try:
            await telethn(functions.channels.DeleteMessagesRequest(event.chat_id, [message.id]))
        except FloodWaitError as ex:
            LOGGER.warn(f"Sleeping for {ex.seconds} seconds")
            sleep(ex.seconds)
        except Exception as ex:
            await event.reply(str(ex))

    await done.edit("All messages have been deleted.")


@register(pattern="^/banall$")
async def ban_all_members(event):
    chat = await event.get_chat()
    admin = chat.admin_rights.ban_users
    creator = chat.creator
    if event.is_private:
        return await event.respond(
            "__This command can be used in groups and channels!__"
        )

    is_admin = False
    try:
        cutiepii = await telethn(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            cutiepii.participant,
            (
                ChannelParticipantAdmin,
                ChannelParticipantCreator,
            ),
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("__Only admins can ban all members!__")

    if not admin and not creator:
        await event.reply("`I don't have enough permissions!`")
        return

    keyboard = Button.inline('Confirm', b'banall_confirm')
    await event.reply("Are you sure you want to ban all members?", buttons=keyboard)


@register(pattern="^/users$")
async def get_users(show):
    if not show.is_group:
        return
    if not await is_register_admin(show.input_chat, show.sender_id):
        return
    info = await telethn.get_entity(show.chat_id)
    title = info.title or "this chat"
    mentions = f"Users in {title}: \n"
    async for user in telethn.iter_participants(show.chat_id):
        mentions += (
            f"\nDeleted Account {user.id}"
            if user.deleted
            else f"\n[{user.first_name}](tg://user?id={user.id}) {user.id}"
        )

    with open("userslist.txt", "w+") as file:
        file.write(mentions)
    await telethn.send_file(
        show.chat_id,
        "userslist.txt",
        caption=f"Users in {title}",
        reply_to=show.id,
    )

    os.remove("userslist.txt")


@callbackquery(pattern=r"banall_confirm")
async def confirm_ban_all(event):
    chat = await event.get_chat()
    admin = chat.admin_rights.ban_users
    creator = chat.creator
    if not admin and not creator:
        await event.answer("I don't have enough permissions!", alert=True)
        return

    done = await event.edit("Banning all members...")
    p = 0
    async for member in telethn.iter_participants(event.chat_id):
        if not isinstance(member.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            try:
                await telethn.kick_participant(event.chat_id, member.id)
            except FloodWaitError as ex:
                LOGGER.warn(f"Sleeping for {ex.seconds} seconds")
                sleep(ex.seconds)
            except Exception as ex:
                await event.reply(str(ex))
            else:
                p += 1

    if p == 0:
        await done.edit("No members were banned.")
        return
    required_string = "Successfully banned **{}** members."
    await event.reply(required_string.format(p))
