from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

from MissCutie import MONGO_URL

mongo = MongoCli(MONGO_URL)
db = mongo.MissCutie

vickdb = MongoClient(MONGO_URL)
vick = vickdb["VickDb"]["Vick"]


from ...chats import *
from ...users import *
