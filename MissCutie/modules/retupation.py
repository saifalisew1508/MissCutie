from telegram.constants import ParseMode
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes, filters, CommandHandler

from MissCutie import application, LOGGER
from MissCutie.modules.disable import DisableAbleMessageHandler
import MissCutie.modules.sql.reputation_sql as sql
import MissCutie.modules.sql.reputation_settings_sql as settings



async def increase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user1 = update.effective_user
    chat = update.effective_chat
    if not settings.chat_should_reputate(chat.id):
        return
    if msg.reply_to_message:
        user2 = msg.reply_to_message.from_user
        if not settings.user_should_reputate(user1.id):
            await msg.reply_text("You have opted out of reputations, so you are not able to change others reputation neither.")
            return
        if not settings.user_should_reputate(user2.id):
            await msg.reply_text(f"{user2.full_name} opted out of reputations,"
                                 f" so you are not able to change their reputation.")
            return
        if user1.id != user2.id:
            LOGGER.debug(f"{user2.id} : {sql.get_reputation(chat.id, user2.id)}")
            sql.increase_reputation(chat.id, user2.id)
            new_msg = await msg.reply_text(f"<b>{user1.first_name}</b> ({sql.get_reputation(chat.id, user1.id)}) has increased reputation of <b>{user2.first_name}</b> ({sql.get_reputation(chat.id, user2.id)})", parse_mode=ParseMode.HTML).message_id
            try:
                await context.bot.delete_message(chat.id, sql.get_latest_rep_message(chat.id))
            except BadRequest as err:
                LOGGER.debug("Could not delete that message.")
            sql.set_latest_rep_message(chat.id, new_msg)


async def decrease(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user1 = update.effective_user
    chat = update.effective_chat
    if not settings.chat_should_reputate(chat.id):
        return
    if msg.reply_to_message:
        user2 = msg.reply_to_message.from_user
        if not settings.user_should_reputate(user1.id):
            await msg.reply_text("You have opted out of reputations, so you are not able to change others' reputation neither.")
            return
        if not settings.user_should_reputate(user2.id):
            await msg.reply_text(f"{user2.full_name} opted out of reputations,"
                                 f" so you are not able to change their reputation.")
            return
        if user1.id != user2.id:
            LOGGER.debug(f"{user2.id} : {sql.get_reputation(chat.id, user2.id)}")
            sql.decrease_reputation(chat.id, user2.id)
            new_msg = await msg.reply_text(
                f"<b>{user1.first_name}</b> ({sql.get_reputation(chat.id, user1.id)}) has decreased reputation of <b>{user2.first_name}</b> ({sql.get_reputation(chat.id, user2.id)})",
                parse_mode=ParseMode.HTML).message_id
            try:
                await context.bot.delete_message(chat.id, sql.get_latest_rep_message(chat.id))
            except BadRequest as err:
                LOGGER.debug("Could not delete that message.")
            sql.set_latest_rep_message(chat.id, new_msg)


async def reputation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]

    if chat.type == chat.PRIVATE:
        if len(args) >= 1:
            if args[0] in ("yes", "on", "true"):
                settings.set_user_setting(chat.id, True)
                await msg.reply_text("Turned on reputation!")

            elif args[0] in ("no", "off", "false"):
                settings.set_user_setting(chat.id, False)
                await msg.reply_text("Turned off reputation!")
        else:
            await msg.reply_text("Your current reputation preference is: `{}`".format(settings.user_should_reputate(chat.id)),
                                parse_mode=ParseMode.MARKDOWN)

    else:
        if len(args) >= 1:
            if args[0] in ("yes", "on"):
                settings.set_chat_setting(chat.id, True)
                await msg.reply_text("Turned on reputation! Users will now be able to vote on each other's messages, except "
                                     "if they opted out.")

            elif args[0] in ("no", "off"):
                settings.set_chat_setting(chat.id, False)
                await msg.reply_text("Turned off reputation!")
        else:
            await msg.reply_text("This chat's current setting is: `{}`".format(settings.chat_should_reputate(chat.id)),
                                parse_mode=ParseMode.MARKDOWN)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat_latest_messages(old_chat_id, new_chat_id)



def __help__(update: Update) -> str:
    return "" \
           " - /reputation: manage this chats reputation settings, as well as yours.\n" \
           " - +: Increase someones reputation.\n" \
           " - -: Decrease someones reputation."


def __chat_settings__(chat_id, user_id):
    return "Reputations is enabled in this chat, change with /reputation: `{}`".format(
       settings.chat_should_reputate(chat_id))


def __user_settings__(user_id):
    return "Your current reputations setting is `{}`.\nChange this with /reputation in PM.".format(
        settings.user_should_reputate(user_id))


INCREASE_MESSAGE_HANDLER = DisableAbleMessageHandler(
    filters.Regex(r"^\+$"), afk, friendly="afk", block=False
)
DECREASE_MESSAGE_HANDLER = DisableAbleMessageHandler(
    filters.Regex(r"^\-$"), afk, friendly="afk", block=False
)
INCREASE_MESSAGE_HANDLER2 = DisableAbleMessageHandler(
    filters.Regex(r"^\👍$"), afk, friendly="afk", block=False
)
DECREASE_MESSAGE_HANDLER2 = DisableAbleMessageHandler(
    filters.Regex(r"^\👎$"), afk, friendly="afk", block=False
)
SETTINGS_HANDLER = CommandHandler("reputation", reputation, block=False)


application.add_handler(INCREASE_MESSAGE_HANDLER)
application.add_handler(DECREASE_MESSAGE_HANDLER)
application.add_handler(INCREASE_MESSAGE_HANDLER2)
application.add_handler(DECREASE_MESSAGE_HANDLER2)
application.add_handler(SETTINGS_HANDLER)
