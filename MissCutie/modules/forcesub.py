from telethon import Button, events, types
from telethon.errors import ChatAdminRequiredError
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

# Importing other required modules and variables
from MissCutie import BOT_ID
from MissCutie import DEV_USERS
from MissCutie import OWNER_ID
from MissCutie import telethn
from MissCutie.events import callbackquery
from MissCutie.events import register
from MissCutie.modules.no_sql import fsub_db as db

async def is_admin(chat_id, user_id):
    try:
        p = await telethn(GetParticipantRequest(chat_id, user_id))
    except UserNotParticipantError:
        return False
    return isinstance(p.participant, types.ChannelParticipantAdmin) or isinstance(p.participant, types.ChannelParticipantCreator)

async def participant_check(channel, user_id):
    try:
        await telethn(GetParticipantRequest(channel, int(user_id)))
        return True
    except UserNotParticipantError:
        return False
    except:
        return False

@register(pattern="^/(fsub|Fsub|forcesubscribe|Forcesub|forcesub|Forcesubscribe) ?(.*)")
async def fsub(event):
    # Check if the event is in a private chat or a group
    if event.is_private:
        return
    if event.is_group:
        perm = await event.client.get_permissions(event.chat_id, event.sender_id)
        if not perm.is_admin:
            return await event.reply("You need to be an admin to do this.")
        if not perm.is_creator:
            return await event.reply("Group creator required. You have to be the group creator to do that.")

    # Extract the channel parameter from the command
    try:
        channel = event.text.split(None, 1)[1]
    except IndexError:
        channel = None

    if not channel:
        # Handle case when channel parameter is not provided
        chat_db = db.fs_settings(event.chat_id)
        if not chat_db:
            await event.reply("Force subscribe is disabled in this chat.")
        else:
            await event.reply(f"Force subscribe is currently enabled. Users are forced to join @{chat_db.channel} to speak here.")
    elif channel in ["on", "yes", "y"]:
        await event.reply("Please specify the channel username.")
    elif channel in ["off", "no", "n"]:
        await event.reply("Force subscribe is disabled successfully.")
        db.disapprove(event.chat_id)
    else:
        # Check if the channel exists and if the bot is an admin in the channel
        try:
            channel_entity = await event.client.get_entity(channel)
        except:
            return await event.reply("Invalid channel username provided.")

        channel = channel_entity.username
        try:
            if not channel_entity.broadcast:
                return await event.reply("That's not a valid channel.")
        except:
            return await event.reply("That's not a valid channel.")

        if not await participant_check(channel, BOT_ID):
            return await event.reply(f"I am not an admin in the channel {channel}. Add me as an admin to enable forcesubscribe.")

        db.add_channel(event.chat_id, str(channel))
        await event.reply(f"Force subscribe is enabled to @{channel}.")

@telethn.on(events.NewMessage())
async def fsub_n(e):
    # Check if force subscribe is enabled in the chat
    if not db.fs_settings(e.chat_id):
        return
    if e.is_private:
        return
    if e.chat.admin_rights and not e.chat.admin_rights.ban_users:
        return
    if not e.from_id:
        return
    if await is_admin(e.chat_id, e.sender_id) or e.sender_id in DEV_USERS or e.sender_id == OWNER_ID:
        return

    channel = db.fs_settings(e.chat_id).get("channel")
    try:
        check = await participant_check(channel, e.sender_id)
    except ChatAdminRequiredError:
        return

    if not check:
        buttons = [
            Button.url("Join Channel", f"t.me/{channel}"),
            Button.inline("Unmute me", data="fs_{}".format(str(e.sender_id)))
        ]
        txt = f'<b><a href="tg://user?id={e.sender_id}">{e.sender.first_name}</a></b>, You are not subscribed to our <b><a href="t.me/{channel}">Channel</a></b> yet. Please <b><a href="t.me/{channel}">join</a></b> and press the button below to unmute yourself.'
        await e.reply(txt, buttons=buttons, parse_mode="html", link_preview=False)
        await e.client.edit_permissions(e.chat_id, e.sender_id, send_messages=False)

@callbackquery(pattern=r"fs(\_(.*))")
async def unmute_fsub(event):
    user_id = int(((event.pattern_match.group(1)).decode()).split("_", 1)[1])
    if not event.sender_id == user_id:
        return await event.answer("This isn't for you.", alert=True)

    channel = db.fs_settings(event.chat_id).get("channel")
    try:
        check = await participant_check(channel, user_id)
    except ChatAdminRequiredError:
        check = False
        return

    if not check:
        return await event.answer("Join Channel for Unmute yourself!", alert=True)

    try:
        await event.client.edit_permissions(event.chat_id, user_id, send_messages=True)
    except ChatAdminRequiredError:
        pass

    await event.delete()
