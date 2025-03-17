# MissCutie/modules/admin_manage.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatAdministratorRights, ChatMemberAdministrator, ChatMemberOwner
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from MissCutie import application
from MissCutie.modules.helper_funcs.chat_status import bot_admin, check_admin, user_admin
from telegram.constants import ParseMode

PERMISSION_MAP = {
    "can_change_info": "Change Info",
    "can_delete_messages": "Delete Messages",
    "can_invite_users": "Invite Users",
    "can_restrict_members": "Restrict Members",
    "can_pin_messages": "Pin Messages",
    "can_promote_members": "Promote Members",
    "can_manage_video_chats": "Manage Video Chats",
    "can_post_messages": "Post Messages",
    "can_edit_messages": "Edit Messages",
    "can_manage_chat": "Manage Chat",
    "can_manage_topics": "Manage Topics",
}

TEMP_RIGHTS_STORE = {}

def is_full_admin(member) -> bool:
    if isinstance(member, ChatMemberOwner):
        return True
    if isinstance(member, ChatMemberAdministrator) and not member.is_anonymous:
        return all([
            member.can_change_info,
            member.can_delete_messages,
            member.can_invite_users,
            member.can_restrict_members,
            member.can_pin_messages,
            member.can_promote_members
        ])
    return False

def get_lacking_permissions(member):
    lacking = []
    for perm, name in PERMISSION_MAP.items():
        if not getattr(member, perm, False):
            lacking.append(f"❌ {name}")
    return lacking

@check_admin
@bot_admin
async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    from_user = update.effective_user
    member = await chat.get_member(from_user.id)

    if not is_full_admin(member):
        lack = get_lacking_permissions(member)
        lack_text = "\n".join(lack) or "You must be full admin (excluding anonymous) to promote."
        return await update.effective_message.reply_text(f"You lack permissions:\n{lack_text}")

    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        user_id = user.id
        title = "Admin" if not context.args else " ".join(context.args)
    elif context.args:
        try:
            user = await context.bot.get_chat_member(chat.id, context.args[0])
            user_id = user.user.id
            title = "Admin" if len(context.args) < 2 else " ".join(context.args[1:])
        except:
            return await update.effective_message.reply_text("User not found or invalid.")
    else:
        return await update.effective_message.reply_text("Reply to a user or provide username/userid.")

    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_promote_members:
        return await update.effective_message.reply_text("I don't have permission to promote users.")

    target_member = await chat.get_member(user_id)
    if isinstance(target_member, ChatMemberAdministrator):
        if not bot_member.can_promote_members:
            return await update.effective_message.reply_text("User already promoted by someone else, I can't change their permissions.")
        if title and target_member.custom_title != title:
            await context.bot.set_administrator_custom_title(chat.id, user_id, title)
            return await update.effective_message.reply_text(f"{user.mention_html()} was already promoted, I just changed their title.", parse_mode=ParseMode.HTML)
        return await update.effective_message.reply_text(f"{user.mention_html()} is already promoted.", parse_mode=ParseMode.HTML)

    rights = ChatAdministratorRights(
        is_anonymous=False,
        can_change_info=True,
        can_delete_messages=True,
        can_invite_users=True,
        can_restrict_members=True,
        can_pin_messages=True,
        can_promote_members=False
    )
    await context.bot.promote_chat_member(chat.id, user_id, **rights.to_dict())
    await context.bot.set_administrator_custom_title(chat.id, user_id, title)
    TEMP_RIGHTS_STORE[user_id] = rights.to_dict()

    buttons = [
        [InlineKeyboardButton("❌ Remove Admin", callback_data=f"removeadmin|{user_id}")],
        [InlineKeyboardButton("⚙️ Edit Permissions", callback_data=f"editrights|{user_id}")]
    ]
    await update.effective_message.reply_text(
        f"{user.mention_html()} has been promoted with title <b>{title}</b>.",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )

@check_admin
@bot_admin
async def demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    from_user = update.effective_user
    member = await chat.get_member(from_user.id)

    if not is_full_admin(member):
        lack = get_lacking_permissions(member)
        lack_text = "\n".join(lack)
        return await update.effective_message.reply_text(f"You lack permissions:\n{lack_text}")

    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        user_id = user.id
    elif context.args:
        try:
            user = await context.bot.get_chat_member(chat.id, context.args[0])
            user_id = user.user.id
        except:
            return await update.effective_message.reply_text("User not found or invalid.")
    else:
        return await update.effective_message.reply_text("Reply to a user or provide username/userid.")

    target_member = await chat.get_member(user_id)
    bot_member = await chat.get_member(context.bot.id)

    if not isinstance(target_member, ChatMemberAdministrator):
        return await update.effective_message.reply_text("This user is not an admin.")
    if not bot_member.can_promote_members:
        return await update.effective_message.reply_text("I can't demote this user, they were promoted by someone else.")

    await context.bot.promote_chat_member(chat.id, user_id, ChatAdministratorRights())
    await update.effective_message.reply_text(f"{user.mention_html()} has been demoted.", parse_mode=ParseMode.HTML)

@check_admin
async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    admins = await context.bot.get_chat_administrators(chat.id)
    text = "<b>Admins in this chat:</b>\n\n"
    for admin in admins:
        user = admin.user
        title = "Owner" if admin.status == "creator" else admin.custom_title or "Admin"
        text += f"• {user.mention_html()} - {title}\n"
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat.id

    if data.startswith("removeadmin|"):
        user_id = int(data.split("|")[1])
        await context.bot.promote_chat_member(chat_id, user_id, ChatAdministratorRights())
        await query.edit_message_text("Admin rights removed.")
    elif data.startswith("editrights|"):
        user_id = int(data.split("|")[1])
        current = TEMP_RIGHTS_STORE.get(user_id, {})
        keyboard = []
        for perm, name in PERMISSION_MAP.items():
            status = current.get(perm, False)
            icon = "✅" if status else "❌"
            keyboard.append([InlineKeyboardButton(f"{icon} {name}", callback_data=f"toggleperm|{user_id}|{perm}")])
        await query.edit_message_text("Click a permission to toggle:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("toggleperm|"):
        _, user_id, perm = data.split("|")
        user_id = int(user_id)
        current = TEMP_RIGHTS_STORE.get(user_id, {})
        current[perm] = not current.get(perm, False)
        TEMP_RIGHTS_STORE[user_id] = current
        rights = ChatAdministratorRights(**current)
        await context.bot.promote_chat_member(chat_id, user_id, **rights.to_dict())
        keyboard = []
        for p, name in PERMISSION_MAP.items():
            status = current.get(p, False)
            icon = "✅" if status else "❌"
            keyboard.append([InlineKeyboardButton(f"{icon} {name}", callback_data=f"toggleperm|{user_id}|{p}")])
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

__help__ = """
Admin Management Commands:

/admin or /promote [optional title]
- Promote a user to admin with default permissions.
- Can be used by replying to a user's message or by providing username/userid.
- Examples:
  /admin (in reply to message)
  /admin @username
  /admin @username Group Moderator
- After promotion, bot sends two buttons:
  ❌ Remove Admin - Instantly demotes the user.
  ⚙️ Edit Permissions - Lets you toggle each admin permission.
- ✅ means the permission is enabled.
- ❌ means the permission is disabled.
- Tap on a permission to enable/disable it instantly.

/unadmin or /demote
- Demote a user and remove all admin rights.
- Can be used by replying to a message or by username/userid.
- Examples:
  /demote (in reply)
  /unadmin @username

/admins
- List all admins in the group along with their titles.

/admin and /demote command usage formats:
- Reply to user's message with /admin or /demote
- /admin or /demote username/userid
- /admin username title (title is optional)

Rules & Behavior:
- Only admins with full permissions (excluding anonymous and owner) can use these commands.
- If you don't have required rights, the bot will tell which ones are missing.
- If the user is already admin and only title is updated, bot replies: "User was already promoted, title updated."
- If the user is already promoted by someone else and bot cannot change rights or demote, it replies: "User already promoted by someone else, I can't demote or change their rights."

Permission Types:
Change Info, Delete Messages, Invite Users, Restrict Members, Pin Messages,
Promote Members, Manage Video Chats, Manage Chat, Post/Edit Messages, Manage Topics.
"""


__mod_name__ = "Admin Control"

__command_list__ = ["admin", "promote", "unadmin", "demote", "admins"]

def __handlers__():
    return [
        CommandHandler(["promote", "admin"], promote_user),
        CommandHandler(["demote", "unadmin"], demote_user),
        CommandHandler("admins", list_admins),
        CallbackQueryHandler(handle_buttons, pattern=r"^(removeadmin|editrights|toggleperm)\|"),
    ]