from enum import Enum
from functools import wraps
from threading import RLock
from time import perf_counter

from cachetools import TTLCache
from telegram import Chat, ChatMember, ChatMemberAdministrator, ChatMemberOwner, Update
from telegram.constants import ChatMemberStatus, ChatType
from telegram.ext import ContextTypes
from telegram.error import Forbidden

from MissCutie import application, DEV_USERS, DRAGONS, SUPPORT_CHAT, DEL_CMDS

# Constants
TELEGRAM_SYSTEM_USERS = [777000, 1087968824]

# Cache for admin list (10 minutes TTL)
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10, timer=perf_counter)
THREAD_LOCK = RLock()


def check_admin(
    permission: str = None,
    is_bot: bool = False,
    is_user: bool = False,
    is_both: bool = False,
    only_owner: bool = False,
    only_sudo: bool = False,
    only_dev: bool = False,
    no_reply: bool = False,
):
    """
    Decorator to check admin permission levels in groups.
    """
    def wrapper(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            chat = update.effective_chat
            user = update.effective_user
            message = update.effective_message

            if chat.type == ChatType.PRIVATE and not (only_dev or only_sudo or only_owner):
                return await func(update, context, *args, **kwargs)

            bot_member = await chat.get_member(context.bot.id) if is_bot or is_both else None
            user_member = await chat.get_member(user.id) if is_user or is_both else None

            if only_owner:
                if isinstance(user_member, ChatMemberOwner) or user.id in DEV_USERS:
                    return await func(update, context, *args, **kwargs)
                return await message.reply_text("Only chat owner can perform this action.")

            if only_dev and user.id not in DEV_USERS:
                return await message.reply_text(
                    "Hey little kid\nWho the hell are you to say me what to execute on my server?"
                )

            if only_sudo and user.id not in DRAGONS:
                return await message.reply_text("Who the hell are you to say me what to do?")

            if user.id in TELEGRAM_SYSTEM_USERS:
                return await func(update, context, *args, **kwargs)

            if permission:
                no_perm_msg = f"You don't have permission to {permission.replace('_', ' ').replace('can', '').strip()}."

                if is_bot and isinstance(bot_member, ChatMemberAdministrator):
                    if getattr(bot_member, permission, False):
                        return await func(update, context, *args, **kwargs)
                    if not no_reply:
                        return await message.reply_text(f"I don't have permission to {no_perm_msg}")

                elif is_user:
                    if isinstance(user_member, ChatMemberOwner) or user.id in DRAGONS:
                        return await func(update, context, *args, **kwargs)
                    if isinstance(user_member, ChatMemberAdministrator) and getattr(user_member, permission, False):
                        return await func(update, context, *args, **kwargs)
                    if not no_reply:
                        return await message.reply_text(no_perm_msg)

                elif is_both:
                    if not (isinstance(bot_member, ChatMemberAdministrator) and getattr(bot_member, permission, False)):
                        if not no_reply:
                            return await message.reply_text(f"I don't have permission to {no_perm_msg}")
                        return

                    if not (isinstance(user_member, ChatMemberOwner) or user.id in DEV_USERS or
                            (isinstance(user_member, ChatMemberAdministrator) and getattr(user_member, permission, False))):
                        if not no_reply:
                            return await message.reply_text(no_perm_msg)
                        return

                    return await func(update, context, *args, **kwargs)

            else:
                if is_bot and bot_member.status != ChatMemberStatus.ADMINISTRATOR:
                    return await message.reply_text("I'm not admin here.")

                if is_user and not (user_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] or user.id in DRAGONS):
                    return await message.reply_text("You are not admin here.")

                if is_both:
                    if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
                        return await message.reply_text("I'm not admin here.")
                    if not (user_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] or user.id in DRAGONS):
                        return await message.reply_text("You are not admin here.")

                return await func(update, context, *args, **kwargs)

        return wrapped
    return wrapper


def is_whitelist_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in DRAGONS or user_id in DEV_USERS


def is_support_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in DRAGONS or user_id in DEV_USERS


async def is_user_admin(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if chat.type == "private" or user_id in DRAGONS or user_id in DEV_USERS or user_id in TELEGRAM_SYSTEM_USERS:
        return True

    if not member:
        try:
            with THREAD_LOCK:
                return user_id in ADMIN_CACHE[chat.id]
        except KeyError:
            try:
                chat_admins = await application.bot.getChatAdministrators(chat.id)
                admin_list = [x.user.id for x in chat_admins]
                ADMIN_CACHE[chat.id] = admin_list
                return user_id in admin_list
            except Forbidden:
                return False
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def is_bot_admin(chat: Chat, bot_id: int, bot_member: ChatMember = None) -> bool:
    if chat.type == "private":
        return True
    bot_member = bot_member or await chat.get_member(bot_id)
    return bot_member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def can_delete(chat: Chat, bot_id: int) -> bool:
    chat_member = await chat.get_member(bot_id)
    return isinstance(chat_member, ChatMemberAdministrator) and chat_member.can_delete_messages


async def is_user_ban_protected(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if chat.type == "private" or user_id in DRAGONS or user_id in DEV_USERS or user_id in TELEGRAM_SYSTEM_USERS:
        return True
    if not member:
        member = await chat.get_member(user_id)
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def is_user_in_chat(chat: Chat, user_id: int) -> bool:
    member = await chat.get_member(user_id)
    return member.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)


def support_plus(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if is_support_plus(update.effective_chat, update.effective_user.id):
            return await func(update, context, *args, **kwargs)
        if DEL_CMDS and " " not in update.effective_message.text:
            try:
                await update.effective_message.delete()
            except:
                pass
    return wrapper


def whitelist_plus(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if is_whitelist_plus(update.effective_chat, update.effective_user.id):
            return await func(update, context, *args, **kwargs)
        return await update.effective_message.reply_text(
            f"You don't have access to use this.\nVisit @{SUPPORT_CHAT}"
        )
    return wrapper


def user_not_admin(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not await is_user_admin(update.effective_chat, update.effective_user.id):
            return await func(update, context, *args, **kwargs)
    return wrapper


def connection_status(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        conn = await connected(context.bot, update, update.effective_chat, update.effective_user.id, need_admin=False)
        if conn:
            update.__setattr__("_effective_chat", await application.bot.getChat(conn))
        elif update.effective_chat.type == ChatType.PRIVATE:
            return await update.effective_message.reply_text(
                "Send /connect in a group that you and I have in common first."
            )
        return await func(update, context, *args, **kwargs)
    return wrapper


# Workaround for circular import
from MissCutie.modules import connection
connected = connection.connected