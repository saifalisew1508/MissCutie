from typing import Dict, Union

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from MissCutie import MONGO_DB_URI

mongo = MongoClient(MONGO_DB_URI)
db = mongo.MissCutie
