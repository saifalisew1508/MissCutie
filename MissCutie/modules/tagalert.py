import dateparser 
import asyncio
import pytz

from pyrogram import filters
from pymongo import MongoClient
from datetime import datetime, timedelta
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions

from MissCutie import pbot
from MissCutie import BOT_ID, MONGO_DB_URI

client = MongoClient(MONGO_DB_URI)
dbd = client["missjuliarobot"]
approved_users = dbd.approve
db = dbd

tagdb = db.tagdb1
alarms = db.alarm
shedule = db.shedule
nightmod = db.nightmode4

def get_info(id):
    return nightmod.find_one({"id": id})

@pbot.on_message(filters.command(["tagalert"]) & filters.private)
async def locks_dfunc(_, message):
    lol = await message.reply("Processing..")
    if len(message.command) != 2:
        return await lol.edit("Expected on or off 👀")
    parameter = message.text.strip().split(None, 1)[1].lower()

    if parameter in ("on", "ON"):
        if not message.from_user or not message.from_user.username:
            return await lol.edit("Only users with usernames are eligible for tag alert service")

        uname = str(message.from_user.username).lower()
        isittrue = tagdb.find_one({"teg": uname})
        
        if not isittrue:
            tagdb.insert_one({"teg": uname})
            return await lol.edit(f"Tag alerts enabled.\nWhen someone tags you as @{uname} you will be notified")
        else:
            return await lol.edit("Tag alerts already enabled for you")

    if parameter in ("off", "OFF"):
        if not message.from_user or not message.from_user.username:
            return await lol.edit("Only users with usernames are eligible for tag alert service")

        uname = message.from_user.username.lower()
        isittrue = tagdb.find_one({"teg": uname})

        if isittrue:
            tagdb.delete_one({"teg": uname})
            return await lol.edit("Tag alerts removed")
        else:
            return await lol.edit("Tag alerts already disabled for you") 
    else:
        await lol.edit("Expected on or off 👀")

@pbot.on_message(filters.incoming)
async def mentioned_alert(client, message):
    try:
        if not message or not message.from_user:
            return message.continue_propagation()

        input_str = message.text.lower()

        if "@" in input_str:
            input_str = input_str.replace("@", "  |")
            inuka = input_str.split("|")[1]
            text = inuka.split()[0]
        else:
            for c in alarms.find({}):
                chat, user, time, zone, reason = c["chat"], c["user"], c["time"], c["zone"], c["reason"]
                present = dateparser.parse('now', settings={'TIMEZONE': zone, 'DATE_ORDER': 'YMD'}) 
                ttime = dateparser.parse(time, settings={'TIMEZONE': zone}) 

                if present > ttime:
                    try:
                        alarms.delete_one({"chat": chat, "user": user, "time": time, "zone": zone, "reason": reason})
                        await client.send_message(chat, f"**🚨 REMINDER 🚨**\n\n__This is a reminder set by__ {user}\n__Reason__: {reason} \n\n`Reminded at: {ttime}`")
                        message.continue_propagation()
                    except:
                        alarms.delete_one({"chat": chat, "user": user, "time": time, "zone": zone, "reason": reason"})
                        return message.continue_propagation()
                    break
                continue

            for c in shedule.find({}):
                chat, reason = c["chat"], c["reason"]
                present = dateparser.parse('now', settings={'TIMEZONE': c["zone"], 'DATE_ORDER': 'YMD'}) 
                ttime = dateparser.parse(c["time"], settings={'TIMEZONE': c["zone"]}) 

                if present > ttime:
                    try:
                        shedule.delete_one(c)
                        await client.send_message(chat, f"{reason}")
                        message.continue_propagation()
                    except:
                        shedule.delete_one(c)
                        return message.continue_propagation()
                    break
                continue

            for c in nightmod.find({}):
                id, valid, zone, ctime, otime = c["id"], c["valid"], c["zone"], c["ctime"], c["otime"]
                present = dateparser.parse("now", settings={"TIMEZONE": zone, "DATE_ORDER": "YMD"})

                try:
                    if present > otime and valid:
                        newtime = otime + timedelta(days=1)
                        to_check = get_info(id=id)

                        if to_check and newtime:
                            nightmod.update_one(
                                {
                                    "_id": to_check["_id"],
                                    "id": to_check["id"],
                                    "valid": to_check["valid"],
                                    "zone": to_check["zone"],
                                    "ctime": to_check["ctime"],
                                    "otime": to_check["otime"],
                                },
                                {"$set": {"otime": newtime}},
                            )                  
                            await client.set_chat_permissions(
                                id,
                                ChatPermissions(
                                    can_send_messages=True,
                                    can_send_media_messages=True,
                                    can_send_stickers=True,
                                    can_send_animations=True
                                )
                            )

                            await client.send_message(
                                id,
                                "**🌗 Night Mode Ended: `Chat Opening`\n\nEveryOne Should Be Able To Send Messages.**",
                            )
                            message.continue_propagation()
                            break
                except:
                    print("Chat open error in nightbot")
                    return message.continue_propagation()
                continue

            for c in nightmod.find({}):
                id, valid, zone, ctime, otime = c["id"], c["valid"], c["zone"], c["ctime"], c["otime"]
                present = dateparser.parse("now", settings={"TIMEZONE": zone, "DATE_ORDER": "YMD"})

                try:
                    if present > ctime and valid:
                        newtime = ctime + timedelta(days=1)
                        to_check = get_info(id=id)

                        if to_check and newtime:
                            nightmod.update_one(
                                {
                                    "_id": to_check["_id"],
                                    "id": to_check["id"],
                                    "valid": to_check["valid"],
                                    "zone": to_check["zone"],
                                    "ctime": to_check["ctime"],
                                    "otime": to_check["otime"],
                                },
                                {"$set": {"ctime": newtime}},
                            )
                            await client.set_chat_permissions(id, ChatPermissions())                  
                            await client.send_message(
                                id,
                                "**🌗 Night Mode Starting: `Chat close initiated`\n\nOnly Admins Should Be Able To Send Messages**",
                            )
                            message.continue_propagation()
                            break
                except:
                    print("Chat close err")
                    return message.continue_propagation()
                continue

            return message.continue_propagation()

        if tagdb.find_one({"teg": text}):
            pass
        else:
            return message.continue_propagation()

        try:
            chat_name = message.chat.title
            chat_id = message.chat.id
            tagged_msg_link = message.link
        except:
            return message.continue_propagation()

        user_ = message.from_user.mention or f"@{message.from_user.username}"

        final_tagged_msg = f"""
**User:** {message.from_user.mention if message.from_user else None} [`{message.from_user.id if message.from_user else None}`]
**Text:** {message.text.markdown if message.text else message.caption if message.caption else None}
**Chat:** {message.chat.title} [`{message.chat.id}`]
**Bot:** {message.from_user.is_bot}
"""

        button_s = InlineKeyboardMarkup([[InlineKeyboardButton("🔔 View Message 🔔", url=tagged_msg_link)]])
        try:
            await client.send_message(chat_id=f"{text}", text=final_tagged_msg, reply_markup=button_s, disable_web_page_preview=True)

        except:
            return message.continue_propagation()

        message.continue_propagation()

    except:
        return message.continue_propagation()

__mod_name__ = "Tag-Alert"

from MissCutie.modules.language import gs

def get_help(chat):
    return gs(chat, "tagalert_help")
