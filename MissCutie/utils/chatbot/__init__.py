from pymongo import MongoClient
from MissCutie import MONGO_URL2

mongo = MongoCli(MONGO_URL2)
db = mongo.MissCutie

vickdb = MongoClient(MONGO_URL2)
vick = vickdb["VickDb"]["Vick"]


from ..chats import *
from ..users import *
