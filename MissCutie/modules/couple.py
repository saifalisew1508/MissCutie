import random
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, filters, MessageHandler, CommandHandler


def dt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    dt_list = dt_string.split(" ")
    return dt_list

def dt_tom():
    a = (
        str(int(dt()[0].split("/")[0]) + 1)
        + "/"
        + dt()[0].split("/")[1]
        + "/"
        + dt()[0].split("/")[2]
    )
    return a

today = str(dt()[0])
tomorrow = str(dt_tom())

# Command handler for /couple and /couples
async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == 'private':
        return await update.message.reply_text("This command only works in groups.")
    try:
        chat_id = update.message.chat.id
        is_selected = await get_couple(chat_id, today)

        if not is_selected:
            list_of_users = []
            chat_members = await context.bot.get_chat_members(chat_id)
            for i in chat_members:
                if not i.user.is_bot:
                    list_of_users.append(i.user.id)
            
            if len(list_of_users) < 2:
                return await update.message.reply_text("Not enough users")

            c1_id = random.choice(list_of_users)
            c2_id = random.choice(list_of_users)
            
            while c1_id == c2_id:
                c1_id = random.choice(list_of_users)

            c1_mention = (await context.bot.get_chat_member(chat_id, c1_id)).user.mention_html()
            c2_mention = (await context.bot.get_chat_member(chat_id, c2_id)).user.mention_html()

            couple_selection_message = f"""<b>Couple Of the day 💏:</b>\n{c1_mention} + {c2_mention} = ❤️\n
            <i>New couple of the day may be chosen at 12AM {tomorrow}</i>"""
            
            await context.bot.send_message(chat_id, text=couple_selection_message, parse_mode='HTML')
            
            couple = {"c1_id": c1_id, "c2_id": c2_id}
            await save_couple(chat_id, today, couple)

        elif is_selected:
            c1_id = int(is_selected["c1_id"])
            c2_id = int(is_selected["c2_id"])
            c1_user = await context.bot.get_chat_member(chat_id, c1_id)
            c2_user = await context.bot.get_chat_member(chat_id, c2_id)

            c1_mention = c1_user.user.mention_html()
            c2_mention = c2_user.user.mention_html()

            couple_selection_message = f"""<b>Couple of the day:</b>\n{c1_mention} + {c2_mention} = 😘\n
            <i>New couple of the day may be chosen at 12AM {tomorrow}</i>"""

            await context.bot.send_message(chat_id, text=couple_selection_message, parse_mode='HTML')

    except Exception as e:
        print(e)
        await update.message.reply_text(str(e))


# Add the command handler to the dispatcher
couple_handler = CommandHandler(["couple", "couples"], couple)
application.add_handler(couple_handler)
