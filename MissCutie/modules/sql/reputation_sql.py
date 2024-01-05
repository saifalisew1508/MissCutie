import threading

from sqlalchemy import Column, String, UnicodeText, Integer, BigInteger
from Database.sql import BASE, SESSION


class LatestRepMessage(BASE):
    __tablename__ = "rep_messages"
    chat_id = Column(String, primary_key=True)
    msg_id = Column(UnicodeText, default="")

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)


LatestRepMessage.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()


def migrate_chat_latest_messages(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(LatestRepMessage).get(str(old_chat_id))
        if chat:
            chat.chat_id = str(new_chat_id)
        SESSION.commit()


def set_latest_rep_message(chat_id, msg_id):
    with INSERTION_LOCK:
        l = SESSION.query(LatestRepMessage).get(str(chat_id))
        if not l:
            l = LatestRepMessage(str(chat_id))
        l.msg_id = msg_id
        SESSION.add(l)
        SESSION.commit()


def get_latest_rep_message(chat_id):
    l = SESSION.query(LatestRepMessage).get(str(chat_id))
    ret = 0
    if l:
        ret = l.msg_id

    SESSION.close()
    return ret


class Reputation(BASE):
    # I know this  is messed up.
    # The chat id is stored in the column 'user_id', and the chat id in 'user_id'.
    # But I am to lazy to fix this, as this is already rolled out and fixing this would
    # require to migrate existing entries.
    # And this works, so why should I touch it?
    __tablename__ = "reputations"

    user_id = Column(BigInteger, primary_key=True)
    chat_id = Column(String(14), primary_key=True)
    reputation = Column(Integer, default=0)

    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = str(chat_id)
        self.reputation = 0


Reputation.__table__.create(checkfirst=True)


def increase_reputation(user_id, chat_id):
    with INSERTION_LOCK:
        user = SESSION.query(Reputation).get((user_id, str(chat_id)))
        if not user:
            user = Reputation(user_id, str(chat_id))
        user.reputation += 1
        SESSION.add(user)
        SESSION.commit()


def decrease_reputation(user_id, chat_id):
    with INSERTION_LOCK:
        user = SESSION.query(Reputation).get((user_id, str(chat_id)))
        if not user:
            user = Reputation(user_id, str(chat_id))
        user.reputation -= 1
        SESSION.add(user)
        SESSION.commit()


def get_reputation(user_id, chat_id):
    try:
        user = SESSION.query(Reputation).get((user_id, str(chat_id)))
        if not user:
            return 0
        num = user.reputation
        return num
    finally:
        SESSION.close()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Reputation).get(str(old_chat_id))
        if chat:
            chat.chat_id = str(new_chat_id)
        SESSION.commit()
