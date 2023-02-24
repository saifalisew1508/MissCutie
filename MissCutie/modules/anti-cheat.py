from telethon import Telegramtelethn, events, functions, types


# Dictionary to keep track of banned members for each chat
banned_count = {}

@telethn.on(events.NewMessage)
async def check_banned_members(event):
    """Handler for new messages"""
    if not event.is_group:
        return

    # Get the chat ID and admin user ID
    chat_id = event.chat_id
    user_id = event.sender_id

    # Check if the user is an admin in the chat
    chat_member = await telethn(functions.channels.GetParticipantRequest(
        channel=chat_id,
        user_id=user_id
    ))
    if not isinstance(chat_member.participant, types.ChannelParticipantAdmin):
        return

    # Check if the user has banned three members in this chat
    if chat_id in banned_count and banned_count[chat_id] >= 3:
        # Demote the admin to a member
        await telethn(functions.channels.EditAdminRequest(
            channel=chat_id,
            user_id=user_id,
            is_admin=False
        ))

        # Send a message to the chat to announce the demotion
        await telethn.send_message(chat_id, f'{user_id} has been demoted due to banning too many members.')

    # Check if the message is a member ban event
    if isinstance(event.message, types.MessageService) and event.message.action:
        if isinstance(event.message.action, types.MessageActionChatDeleteUser):
            # Increment the banned count for this chat
            if chat_id in banned_count:
                banned_count[chat_id] += 1
            else:
                banned_count[chat_id] = 1

