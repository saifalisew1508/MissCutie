import threading

from sqlalchemy import Column, String

from MissCutie.modules.sql import BASE, SESSION


class CutieChats(BASE):
    __tablename__ = "cutie_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


CutieChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_cutie(chat_id):
    try:
        chat = SESSION.query(CutieChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()


def set_cutie(chat_id):
    with INSERTION_LOCK:
        cutiechat = SESSION.query(CutieChats).get(str(chat_id))
        if not cutiechat:
            cutiechat = CutieChats(str(chat_id))
        SESSION.add(cutiechat)
        SESSION.commit()


def rem_cutie(chat_id):
    with INSERTION_LOCK:
        cutiechat = SESSION.query(CutieChats).get(str(chat_id))
        if cutiechat:
            SESSION.delete(cutiechat)
        SESSION.commit()
