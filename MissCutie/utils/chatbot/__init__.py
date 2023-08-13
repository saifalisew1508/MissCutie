from pymongo import MongoClient
<<<<<<< HEAD
from MissCutie MONGO_URL
=======
from MissCutie import MONGO_URL2
>>>>>>> d9fa0df44dc0ef650688327fb3a8a5bd3cc19e65

mongo = MongoCli(MONGO_URL)
db = mongo.MissCutie

vickdb = MongoClient(MONGO_URL)
vick = vickdb["VickDb"]["Vick"]


from ..chats import *
from ..users import *
