import threading
from sqlalchemy import Boolean, BigInteger, Column
from MissCutie.modules.sql import BASE, SESSION

class JoinRequestSettings(BASE):
    __tablename__ = "join_request_settings"

    chat_id = Column(BigInteger, primary_key=True)
    join_request = Column(Boolean, default=False, nullable=False)
    auto_approve = Column(Boolean, default=False, nullable=False)

    def __init__(self, chat_id: int, join_request: bool, auto_approve: bool):
        self.chat_id = chat_id
        self.join_request = join_request
        self.auto_approve = auto_approve

    def __repr__(self):
        return "<JoinRequest setting {} (join_request={}, auto_approve={})>".format(
            self.chat_id, self.join_request, self.auto_approve
        )

JoinRequestSettings.__table__.create(checkfirst=True)
JOINREQUEST_SETTING_LOCK = threading.RLock()

def enable_join_request(chat_id: int):
    with JOINREQUEST_SETTING_LOCK:
        chat = SESSION.query(JoinRequestSettings).get(chat_id)
        if not chat:
            chat = JoinRequestSettings(chat_id, True, False)

        chat.join_request = True
        chat.auto_approve = False
        SESSION.add(chat)
        SESSION.commit()

def enable_auto_approve(chat_id: int):
    with JOINREQUEST_SETTING_LOCK:
        chat = SESSION.query(JoinRequestSettings).get(chat_id)
        if not chat:
            chat = JoinRequestSettings(chat_id, False, True)

        chat.join_request = False
        chat.auto_approve = True
        SESSION.add(chat)
        SESSION.commit()

def disable_features(chat_id: int):
    with JOINREQUEST_SETTING_LOCK:
        chat = SESSION.query(JoinRequestSettings).get(chat_id)
        if chat:
            chat.join_request = False
            chat.auto_approve = False
            SESSION.add(chat)
            SESSION.commit()

def join_request_status(chat_id: int) -> bool:
    chat = SESSION.query(JoinRequestSettings).get(chat_id)
    return chat is not None and chat.join_request

def auto_approve_status(chat_id: int) -> bool:
    chat = SESSION.query(JoinRequestSettings).get(chat_id)
    return chat is not None and chat.auto_approve

def migrate_chat(old_chat_id, new_chat_id):
    with JOINREQUEST_SETTING_LOCK:
        chat = SESSION.query(JoinRequestSettings).get(old_chat_id)
        if chat:
            chat.chat_id = new_chat_id
            SESSION.add(chat)
        SESSION.commit()
