from typing import Dict, Union

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from MissCutie import DB_NAME, MONGO_DB_URI

client = MongoClient(MONGO_DB_URI)
mongo = client[DB_NAME]
