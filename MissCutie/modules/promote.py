import html
from telegram import ChatMemberAdministrator, Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberOwner
from telegram.constants import ParseMode, ChatMemberStatus, ChatID, ChatType
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CommandHandler, filters, CallbackQueryHandler
from telegram.helpers import mention_html

from MissCutie import DRAGONS, application
from MissCutie.modules.disable import DisableAbleCommandHandler
from MissCutie.modules.helper_funcs.chat_status import (
    check_admin,
    connection_status,
    ADMIN_CACHE,
)

from MissCutie.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from MissCutie.modules.log_channel import loggable
from MissCutie.modules.helper_funcs.alternate import send_message


PERMISSION_NAMES = {
    "can_change_info": "Change Info",
    "can_post_messages": "Post Messages",
    "can_edit_messages": "Edit Messages",
    "can_delete_messages": "Delete Messages",
    "can_invite_users": "Invite Users",
    "can_restrict_members": "Restrict Members",
    "can_pin_messages": "Pin Messages",
    "can_promote_members": "Promote Members",
    "can_manage_chat": "Manage Chat",
    "can_manage_video_chats": "Manage Video Chats",
    "can_manage_topics": "Manage Topics",
}


def create_permission_buttons(user_id, current_permissions):
    buttons = []
    for perm, name in PERMISSION_NAMES.items():
        if current_permissions.get(perm, False):
            buttons.append(
                InlineKeyboardButton(f"{name} ✅", callback_data=f"admin_=toggleperm={user_id}={perm}=False")
            )
        else:
            buttons.append(
                InlineKeyboardButton(f"{name} ❌", callback_data=f"admin_=toggleperm={user_id}={perm}=True")
            )
    return buttons


@connection_status
@loggable
@check_admin(permission="can_promote_members", is_both=True)
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    user_id = await extract_user(message, context, args)
    promoter = await chat.get_member(user.id)

    if message.from_user.id == ChatID.ANONYMOUS_ADMIN:
        await message.reply_text(
            text="You are an anonymous admin.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Click to prove Admin.",
                            callback_data=f"admin_=promote={user_id}",
                        ),
                    ],
                ],
            ),
        )
        return

    if not user_id:
        await message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.",
        )
        return

    try:
        user_member = await chat.get_member(user_id)
    except:
        return

    if user_member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
        await message.reply_text("How am I meant to promote someone that's already an admin?")
        return

    if user_id == bot.id:
        await message.reply_text("I can't promote myself! Get an admin to do it for me.")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = await chat.get_member(bot.id)

    if isinstance(bot_member, ChatMemberAdministrator):
        try:
            await bot.promoteChatMember(
                chat.id,
                user_id,
                can_change_info=bot_member.can_change_info,
                can_post_messages=bot_member.can_post_messages,
                can_edit_messages=bot_member.can_edit_messages,
                can_delete_messages=bot_member.can_delete_messages,
                can_invite_users=bot_member.can_invite_users,
                can_restrict_members=bot_member.can_restrict_members,
                can_pin_messages=bot_member.can_pin_messages,
                can_manage_chat=bot_member.can_manage_chat,
                can_manage_video_chats=bot_member.can_manage_video_chats,
                can_manage_topics=bot_member.can_manage_topics
            )
        except BadRequest as err:
            if err.message == "User_not_mutual_contact":
                await message.reply_text("<b>Failed To Promote:<b> I can't promote someone who isn't in the group.")
            else:
                await message.reply_text("<b>Failed To Promote:<b> An error occurred while promoting.")
            return

    await bot.sendMessage(
        chat.id,
        f"Successfully promoted <b>{user_member.user.first_name or user_id}</b>!",
        parse_mode=ParseMode.HTML,
        message_thread_id=message.message_thread_id if chat.is_forum else None,
        reply_markup=InlineKeyboardMarkup(
            [
                create_permission_buttons(user_id, bot_member),
                [
                    InlineKeyboardButton(
                        text="Demote 🙍🏻",
                        callback_data=f"admin_=demote={user_id}",
                    ),
                    InlineKeyboardButton(
                        text="Delete ❌️",
                        callback_data=f"admin_=delete",
                    ),
                ],
            ],
        )
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@loggable
@check_admin(permission="can_promote_members", is_both=True)
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = await extract_user(message, context, args)
    demoter = await chat.get_member(user.id)

    if message.from_user.id == ChatID.ANONYMOUS_ADMIN:
        await message.reply_text(
            text="You are an anonymous admin.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Click to prove Admin.",
                            callback_data=f"admin_=demote={user_id}",
                        ),
                    ],
                ],
            ),
        )
        return

    if not user_id:
        await message.reply_text(
            "<b>Failed To Demote:<b> You don't seem to be referring to a user or the ID specified is incorrect.",
        )
        return

    try:
        user_member = await chat.get_member(user_id)
    except:
        return

    if user_member.status == ChatMemberStatus.OWNER:
        await message.reply_text("<b>Failed To Demote:<b> This person CREATED the chat, how would I demote them?")
        return

    if not user_member.status == ChatMemberStatus.ADMINISTRATOR:
        await message.reply_text("<b>Failed To Demote:<b> Can't demote what wasn't promoted!")
        return

    if user_id == bot.id:
        await message.reply_text("<b>Failed To Demote:<b> I can't demote myself! Get an admin to do it for me.")
        return

    try:
        await bot.promote_chat_member(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False,
            can_manage_topics=False
        )

        await bot.sendMessage(
            chat.id,
            f"Successfully demoted <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML,
            message_thread_id=message.message_thread_id if chat.is_forum else None
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        await message.reply_text(
            "Could not demote. I might not be admin, or the admin status was appointed by another"
            " user, so I can't act upon them!",
        )
        raise


@loggable
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    bot = context.bot
    message = update.effective_message
    chat = update.effective_chat
    admin_user = query.from_user

    splitter = query.data.replace("admin_", "").split("=")

    if splitter[1] == "promote":
        promoter = await chat.get_member(admin_user.id)

        if (
            not (
                promoter.can_promote_members if isinstance(promoter, ChatMemberAdministrator) else None 
                or promoter.status == ChatMemberStatus.OWNER
            )
            and admin_user.id not in DRAGONS
        ):
            await query.answer("You don't have enough rights to promote!", show_alert=True)
            return

        user_id = splitter[2]

        try:
            user_member = await chat.get_member(user_id)
        except:
            return

        if user_member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            await message.edit_text("How am I meant to promote someone that's already an admin?")
            return

        if user_id == bot.id:
            await message.edit_text("I can't promote myself! Get an admin to do it for me.")
            return

        # set same perms as bot - bot can't assign higher perms than itself!
        bot_member = await chat.get_member(bot.id)

        if isinstance(bot_member, ChatMemberAdministrator):
            try:
                await bot.promoteChatMember(
                    chat.id,
                    user_id,
                    can_change_info=bot_member.can_change_info,
                    can_post_messages=bot_member.can_post_messages,
                    can_edit_messages=bot_member.can_edit_messages,
                    can_delete_messages=bot_member.can_delete_messages,
                    can_invite_users=bot_member.can_invite_users,
                    can_restrict_members=bot_member.can_restrict_members,
                    can_pin_messages=bot_member.can_pin_messages,
                    can_manage_chat=bot_member.can_manage_chat,
                    can_manage_video_chats=bot_member.can_manage_video_chats,
                    can_manage_topics=bot_member.can_manage_topics
                )
            except BadRequest as err:
                if err.message == "User_not_mutual_contact":
                    await message.reply_text("<b>Failed To Promote:<b> I can't promote someone who isn't in the group.")
                else:
                    await message.reply_text("<b>Failed To Promote:<b> An error occurred while promoting.")
                return

        await bot.sendMessage(
            chat.id,
            f"Successfully promoted <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML,
            message_thread_id=message.message_thread_id if chat.is_forum else None,
            reply_markup=InlineKeyboardMarkup(
                [
                    create_permission_buttons(user_id, bot_member),
                    [
                        InlineKeyboardButton(
                            text="Demote 🙍🏻",
                            callback_data=f"admin_=demote={user_id}",
                        ),
                        InlineKeyboardButton(
                            text="Delete ❌️",
                            callback_data=f"admin_=delete",
                        ),
                    ],
                ],
            )
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#PROMOTED\n"
            f"<b>Admin:</b> {mention_html(admin_user.id, admin_user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )
        await query.answer()
        return log_message

    if splitter[1] == "demote":
        demoter = await chat.get_member(admin_user.id)

        if (
            not (
                demoter.can_promote_members if isinstance(demoter, ChatMemberAdministrator) else None 
                or demoter.status == ChatMemberStatus.OWNER
            )
            and admin_user.id not in DRAGONS
        ):
            await query.answer("You don't have enough rights to demote!", show_alert=True)
            return

        user_id = splitter[2]

        try:
            user_member = await chat.get_member(user_id)
        except:
            return

        if user_member.status == ChatMemberStatus.OWNER:
            await message.edit_text("<b>Failed To Demote:<b> This person CREATED the chat, how would I demote them?")
            return

        if not user_member.status == ChatMemberStatus.ADMINISTRATOR:
            await message.edit_text("<b>Failed To Demote:<b> Can't demote what wasn't promoted!")
            return

        if user_id == bot.id:
            await message.edit_text("<b>Failed To Demote:<b> I can't demote myself! Get an admin to do it for me.")
            return

        try:
            await bot.promote_chat_member(
                chat.id,
                user_id,
                can_change_info=False,
                can_post_messages=False,
                can_edit_messages=False,
                can_delete_messages=False,
                can_invite_users=False,
                can_restrict_members=False,
                can_pin_messages=False,
                can_promote_members=False,
                can_manage_chat=False,
                can_manage_video_chats=False,
                can_manage_topics=False
            )

            await bot.sendMessage(
                chat.id,
                f"Successfully demoted <b>{user_member.user.first_name or user_id}</b>!",
                parse_mode=ParseMode.HTML,
                message_thread_id=message.message_thread_id if chat.is_forum else None
            )

            log_message = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#DEMOTED\n"
                f"<b>Admin:</b> {mention_html(admin_user.id, admin_user.first_name)}\n"
                f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
            )

            return log_message
        except BadRequest:
            await message.edit_text(
                "Could not demote. I might not be admin, or the admin status was appointed by another"
                " user, so I can't act upon them!",
            )
            raise

    if splitter[1] == "toggleperm":
        user_id = splitter[2]
        permission = splitter[3]
        enable = splitter[4] == "True"

        # Retrieve the current permissions of the user
        user_member = await chat.get_member(user_id)
        new_permissions = {
            "can_change_info": user_member.can_change_info,
            "can_post_messages": user_member.can_post_messages,
            "can_edit_messages": user_member.can_edit_messages,
            "can_delete_messages": user_member.can_delete_messages,
            "can_invite_users": user_member.can_invite_users,
            "can_restrict_members": user_member.can_restrict_members,
            "can_pin_messages": user_member.can_pin_messages,
            "can_promote_members": user_member.can_promote_members,
            "can_manage_chat": user_member.can_manage_chat,
            "can_manage_video_chats": user_member.can_manage_video_chats,
            "can_manage_topics": user_member.can_manage_topics
        }

        new_permissions[permission] = enable

        try:
            await bot.promoteChatMember(
                chat.id,
                user_id,
                **new_permissions
            )
            await query.answer(f"Permission {PERMISSION_NAMES[permission]} {'enabled' if enable else 'disabled'}!")
        except BadRequest:
            await query.answer("Failed to update permissions. I might not have enough rights to do that.", show_alert=True)
            return

        await message.edit_reply_markup(
            InlineKeyboardMarkup(
                [
                    create_permission_buttons(user_id, new_permissions),
                    [
                        InlineKeyboardButton(
                            text="Demote 🙍🏻",
                            callback_data=f"admin_=demote={user_id}",
                        ),
                        InlineKeyboardButton(
                            text="Delete ❌️",
                            callback_data=f"admin_=delete",
                        ),
                    ],
                ],
            )
        )
        return


promote_handler = DisableAbleCommandHandler("promote", promote, filters=filters.ChatType.GROUPS, block=False)
demote_handler = DisableAbleCommandHandler("demote", demote, filters=filters.ChatType.GROUPS, block=False)
admin_callback_handler = CallbackQueryHandler(admin_callback, pattern=r"admin_=")

application.add_handler(promote_handler)
application.add_handler(demote_handler)
application.add_handler(admin_callback_handler)

__handlers__ = [
    promote_handler,
    demote_handler,
    admin_callback_handler
]
