from typing import Dict, Union

from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

from MissCutie import MONGO_DB_URI

mongo = MongoCli(MONGO_DB_URI)
db = mongo.MissCutie

nsfwdb = db.nsfw



async def is_nsfw_on(chat_id: int) -> bool:
    chat = nsfwdb.find_one({"chat_id": chat_id})
    if not chat:
        return True
    return False


async def nsfw_on(chat_id: int):
    is_nsfw = await is_nsfw_on(chat_id)
    if is_nsfw:
        return
    return nsfwdb.delete_one({"chat_id": chat_id})


async def nsfw_off(chat_id: int):
    is_nsfw = await is_nsfw_on(chat_id)
    if not is_nsfw:
        return
    return nsfwdb.insert_one({"chat_id": chat_id})
