import threading
from sqlalchemy import Column, String, Integer, BigInteger
from Database.sql import BASE, SESSION


class whisper_message():
    message = ""
    sender_id = 0
    receiver_id = 0

    def __init__(self, sender_id, receiver_id, message):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message = message


class Whispers(BASE):
    __tablename__ = "whispers"

    whisper_id = Column(String(14), primary_key=True)
    receiver_id = Column(BigInteger)
    sender_id = Column(BigInteger)
    message = Column(String, default="")

    def __init__(self, whisper_id, receiver_id, sender_id):
        self.whisper_id = whisper_id
        self.receiver_id = receiver_id
        self.sender_id = sender_id


Whispers.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()


def add_whisper(sender_id, receiver_id, message, id):
    with INSERTION_LOCK:
        w = Whispers(id, receiver_id, sender_id)
        w.message = message
        SESSION.add(w)
        SESSION.commit()


def get_message(whisper_id):
    try:
        w = SESSION.query(Whispers).get(str(whisper_id))
        if not w:
            return "null"
        result = whisper_message(w.sender_id, w.receiver_id, w.message)
        return result
    finally:
        SESSION.close()

class Number(BASE):
    __tablename__ = "whisperids"

    bot_id = Column(BigInteger, primary_key=True)
    id = Column(Integer, default=0)

    def __init__(self, bot_id):
        self.bot_id = bot_id
        self.id = 0


Number.__table__.create(checkfirst=True)


def get_whispers(bot_id):
    r = SESSION.query(Number).get(bot_id)
    ret = 0
    if r:
        ret = r.id

    SESSION.close()
    return ret


def increase_whisper_ids(bot_id):
    r = SESSION.query(Number).get(bot_id)
    if not r:
        r = Number(bot_id)
    r.id += 1
    SESSION.add(r)
    SESSION.commit()
