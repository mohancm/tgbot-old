import threading
from enum import IntEnum, unique

from sqlalchemy import Column, String, Boolean, UnicodeText, Integer

from tg_bot.modules.sql import SESSION, BASE

DEFAULT_WELCOME = "Hello {first}"
DEFAULT_LEAVE = "Don't bother coming back!"


@unique
class Types(IntEnum):
    TEXT = 0
    BUTTON_TEXT = 1
    STICKER = 2
    DOCUMENT = 3
    PHOTO = 4
    AUDIO = 5
    VOICE = 6
    VIDEO = 7


class Welcome(BASE):
    __tablename__ = "welcome_pref"
    chat_id = Column(String(14), primary_key=True)
    should_welcome = Column(Boolean, default=True)

    custom_welcome = Column(UnicodeText, default=DEFAULT_WELCOME)
    welcome_type = Column(Integer, default=Types.TEXT.value)

    custom_leave = Column(UnicodeText, default=DEFAULT_LEAVE)
    leave_type = Column(Integer, default=Types.TEXT.value)

    def __init__(self, chat_id, should_welcome=True):
        self.chat_id = chat_id
        self.should_welcome = should_welcome

    def __repr__(self):
        return "<Chat {} should Welcome new users: {}>".format(self.chat_id, self.should_welcome)


class WelcomeButtons(BASE):
    __tablename__ = "welcome_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(14), primary_key=True)
    name = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)

    def __init__(self, chat_id, name, url):
        self.chat_id = str(chat_id)
        self.name = name
        self.url = url


class LeaveButtons(BASE):
    __tablename__ = "leave_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(14), primary_key=True)
    name = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)

    def __init__(self, chat_id, name, url):
        self.chat_id = str(chat_id)
        self.name = name
        self.url = url


Welcome.__table__.create(checkfirst=True)
WelcomeButtons.__table__.create(checkfirst=True)
LeaveButtons.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()
WELC_BTN_LOCK = threading.RLock()
LEAVE_BTN_LOCK = threading.RLock()


def get_welc_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()
    if welc:
        return welc.should_welcome, welc.custom_welcome, welc.welcome_type
    else:
        # Welcome by default.
        return True, DEFAULT_WELCOME, Types.TEXT


def get_leave_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()
    if welc:
        return welc.should_welcome, welc.custom_leave, welc.leave_type
    else:
        # Welcome by default.
        return True, DEFAULT_LEAVE, Types.TEXT


def get_preference(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()
    if welc:
        return welc.should_welcome, welc.custom_welcome, welc.custom_leave, welc.welcome_type, welc.leave_type
    else:
        # Welcome by default.
        return True, DEFAULT_WELCOME, DEFAULT_LEAVE, Types.TEXT, Types.TEXT


def set_preference(chat_id, should_welcome):
    with INSERTION_LOCK:
        curr = SESSION.query(Welcome).get(str(chat_id))
        if not curr:
            curr = Welcome(str(chat_id), should_welcome)
        else:
            curr.should_welcome = should_welcome

        SESSION.add(curr)
        SESSION.commit()


def set_custom_welcome(chat_id, custom_welcome, welcome_type, buttons=None):
    if buttons is None:
        buttons = []

    with INSERTION_LOCK:
        welcome_settings = SESSION.query(Welcome).get(str(chat_id))
        if not welcome_settings:
            welcome_settings = Welcome(str(chat_id), True)

        if custom_welcome:
            welcome_settings.custom_welcome = custom_welcome
            welcome_settings.welcome_type = welcome_type.value

        else:
            welcome_settings.custom_welcome = DEFAULT_LEAVE
            welcome_settings.welcome_type = Types.TEXT.value

        SESSION.add(welcome_settings)

        with WELC_BTN_LOCK:
            prev_buttons = SESSION.query(WelcomeButtons).filter(WelcomeButtons.chat_id == str(chat_id)).all()
            for btn in prev_buttons:
                SESSION.delete(btn)

            for b_name, url in buttons:
                button = WelcomeButtons(chat_id, b_name, url)
                SESSION.add(button)

        SESSION.commit()


def get_custom_welcome(chat_id):
    welcome_settings = SESSION.query(Welcome).get(str(chat_id))
    ret = DEFAULT_WELCOME
    if welcome_settings and welcome_settings.custom_welcome:
        ret = welcome_settings.custom_welcome

    SESSION.close()
    return ret


def set_custom_leave(chat_id, custom_leave, leave_type, buttons=None):
    if buttons is None:
        buttons = []

    with INSERTION_LOCK:
        welcome_settings = SESSION.query(Welcome).get(str(chat_id))
        if not welcome_settings:
            welcome_settings = Welcome(str(chat_id), True)

        if custom_leave:
            welcome_settings.custom_leave = custom_leave
            welcome_settings.leave_type = leave_type.value

        else:
            welcome_settings.custom_leave = DEFAULT_LEAVE
            welcome_settings.leave_type = Types.TEXT.value

        SESSION.add(welcome_settings)

        with LEAVE_BTN_LOCK:
            prev_buttons = SESSION.query(LeaveButtons).filter(LeaveButtons.chat_id == str(chat_id)).all()
            for btn in prev_buttons:
                SESSION.delete(btn)

            for b_name, url in buttons:
                button = LeaveButtons(chat_id, b_name, url)
                SESSION.add(button)

        SESSION.commit()


def get_custom_leave(chat_id):
    welcome_settings = SESSION.query(Welcome).get(str(chat_id))
    ret = DEFAULT_LEAVE
    if welcome_settings and welcome_settings.custom_leave:
        ret = welcome_settings.custom_leave

    SESSION.close()
    return ret


def get_welc_buttons(chat_id):
    try:
        return SESSION.query(WelcomeButtons).filter(WelcomeButtons.chat_id == str(chat_id)).all()
    finally:
        SESSION.close()


def get_leave_buttons(chat_id):
    try:
        return SESSION.query(LeaveButtons).filter(LeaveButtons.chat_id == str(chat_id)).all()
    finally:
        SESSION.close()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Welcome).get(str(old_chat_id))
        if chat:
            chat.chat_id = str(new_chat_id)

        with WELC_BTN_LOCK:
            chat_buttons = SESSION.query(WelcomeButtons).filter(WelcomeButtons.chat_id == str(old_chat_id)).all()
            for btn in chat_buttons:
                btn.chat_id = str(new_chat_id)

        with LEAVE_BTN_LOCK:
            chat_buttons = SESSION.query(LeaveButtons).filter(LeaveButtons.chat_id == str(old_chat_id)).all()
            for btn in chat_buttons:
                btn.chat_id = str(new_chat_id)

        SESSION.commit()
