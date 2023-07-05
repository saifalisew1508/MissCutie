from typing import Dict, Union

from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

from MissCutie import MONGO_DB_URI

mongo = MongoCli(MONGO_DB_URI)
db = mongo.MissCutie

onoffdb = mongo.MissCutie

async def is_on_off(on_off: int) -> bool:
    onoff = await onoffdb.find_one({"on_off": on_off})
    return bool(onoff)


async def add_on(on_off: int):
    is_on = await is_on_off(on_off)
    if is_on:
        return
    return await onoffdb.insert_one({"on_off": on_off})


async def add_off(on_off: int):
    is_off = await is_on_off(on_off)
    if not is_off:
        return
    return await onoffdb.delete_one({"on_off": on_off})
