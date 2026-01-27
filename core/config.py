import datetime

# ======================
# ACADEMIC SETTINGS
# ======================

SEMESTER_START_DATE = datetime.date(2026, 2, 2)  # начало семестра (4 неделя)

REMINDER_MINUTES = (30, 15, 5)

PAIR_START_TIMES = {
    1: datetime.time(8, 0),   # 1 пара
    2: datetime.time(9, 30),  # 2 пара
    3: datetime.time(11, 0),  # 3 пара
}

# ======================
# CHAT IDS
# ======================

CHAT_STRATEGY = -1003789929485
CHAT_QUALITY = -1003798438883
CHAT_ECONOMY = -1003814835903
CHAT_INTL_BUSINESS = -1002982024678
CHAT_SCHEDULE_ONLY = -5103325045

ALL_SUBJECT_CHATS = (
    CHAT_STRATEGY,
    CHAT_QUALITY,
    CHAT_ECONOMY,
    CHAT_INTL_BUSINESS,
    CHAT_SCHEDULE_ONLY,
)
