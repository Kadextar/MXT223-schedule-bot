import logging
import sys
from pathlib import Path

# Добавляем путь к корню проекта, чтобы импортировать модули
sys.path.insert(0, str(Path(__file__).parent))

from core.database import init_database, add_lesson, get_all_lessons, delete_lesson
from core.config import CHAT_STRATEGY, ALL_SUBJECT_CHATS

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словарь преподавателей (копия из веба)
TEACHERS = {
    "Качество и безопасность в гостиничной деятельности": {
        "lecture": "Махмудова Азиза Пирмаматовна",
        "seminar": "Мир-Джафарова Азиза Джавохировна"
    },
    "Стратегический менеджмент в гостиничном хозяйстве": {
        "lecture": "Усманова Нигина Маруповна",
        "seminar": "Бурхонова Наргиза Миршохидовна"
    },
    "Стратегический менеджмент": { 
        "lecture": "Усманова Нигина Маруповна",
        "seminar": "Бурхонова Наргиза Миршохидовна"
    },
    "Мировая экономика и международные экономические отношения": {
        "lecture": "Халимов Шахбоз Халимович",
        "seminar": "Амриева Шахзода Шухратовна"
    },
    "Мировая экономика": { 
        "lecture": "Халимов Шахбоз Халимович",
        "seminar": "Амриева Шахзода Шухратовна"
    },
    "Качество и безопасность": { 
        "lecture": "Махмудова Азиза Пирмаматовна",
        "seminar": "Мир-Джафарова Азиза Джавохировна"
    },
    "Международный гостиничный бизнес": {
        "lecture": "Амриддинова Райхона Садриддиновна",
        "seminar": "Мейлиев Абдугани Наджмиддинович"
    },
    "Урок просвещения": {
        "lecture": "Пардаев Гайрат Яхшибаевич",
        "seminar": ""
    }
}

def get_teacher(subject, type_key):
    # type_key: 'lecture' или 'seminar'
    if subject in TEACHERS:
        return TEACHERS[subject].get(type_key, "")
    
    # Частичное совпадение
    for key in TEACHERS:
        if key in subject or subject in key:
            return TEACHERS[key].get(type_key, "")
    return ""

def get_chat_id(subject):
    # Простая логика выбора чата
    if "Стратегический" in subject:
        return ALL_SUBJECT_CHATS[0]
    if "Качество" in subject:
        return ALL_SUBJECT_CHATS[1]
    if "Мировая" in subject:
        return ALL_SUBJECT_CHATS[2]
    if "Международный" in subject:
        return ALL_SUBJECT_CHATS[3]
    return ALL_SUBJECT_CHATS[4] # Default

# Данные расписания (из веба)
NEW_SCHEDULE = [
    # --- ПОНЕДЕЛЬНИК ---
    {
        "day": "monday", "pair": 1, 
        "subject": "Качество и безопасность в гостиничной деятельности", "type": "lecture",
        "weeks": [4, 8], "room": "2/214"
    },
    {
        "day": "monday", "pair": 1, 
        "subject": "Стратегический менеджмент в гостиничном хозяйстве", "type": "lecture",
        "weeks": [10, 15], "room": "2/214"
    },
    {
        "day": "monday", "pair": 2, 
        "subject": "Стратегический менеджмент в гостиничном хозяйстве", "type": "lecture",
        "weeks": [4, 8], "room": "2/214"
    },
    {
        "day": "monday", "pair": 2, 
        "subject": "Мировая экономика и международные экономические отношения", "type": "lecture",
        "weeks": [10, 15], "room": "2/214"
    },
    {
        "day": "monday", "pair": 3, 
        "subject": "Урок просвещения", "type": "lecture",
        "weeks": [4, 8], "room": "3/305"
    },
    {
        "day": "monday", "pair": 3, 
        "subject": "Урок просвещения", "type": "lecture",
        "weeks": [10, 12], "room": "3/305"
    },
    {
        "day": "monday", "pair": 3, 
        "subject": "Урок просвещения", "type": "lecture",
        "weeks": [13, 15], "room": "3/305"
    },
    # --- ВТОРНИК ---
    {
        "day": "tuesday", "pair": 1,
        "subject": "Мировая экономика и международные экономические отношения", "type": "lecture",
        "weeks": [4, 10], "room": "2/214"
    },
    {
        "day": "tuesday", "pair": 1,
        "subject": "Мировая экономика и международные экономические отношения", "type": "seminar",
        "weeks": [11, 15], "room": "2/214"
    },
    {
        "day": "tuesday", "pair": 2,
        "subject": "Качество и безопасность в гостиничной деятельности", "type": "lecture",
        "weeks": [4, 10], "room": "2/214"
    },
    {
        "day": "tuesday", "pair": 2,
        "subject": "Качество и безопасность в гостиничной деятельности", "type": "lecture",
        "weeks": [11, 15], "room": "2/214"
    },
    {
        "day": "tuesday", "pair": 3,
        "subject": "Международный гостиничный бизнес", "type": "lecture",
        "weeks": [4, 14], "room": "2/214"
    },
    # --- СРЕДА ---
    {
        "day": "wednesday", "pair": 1,
        "subject": "Международный гостиничный бизнес", "type": "seminar",
        "weeks": [4, 15], "room": "2/214"
    },
    {
        "day": "wednesday", "pair": 2,
        "subject": "Качество и безопасность в гостиничной деятельности", "type": "seminar",
        "weeks": [4, 15], "room": "2/214"
    },
    {
        "day": "wednesday", "pair": 3,
        "subject": "Стратегический менеджмент", "type": "lecture",
        "weeks": [10, 10], "room": "2/214"
    },
    {
        "day": "wednesday", "pair": 3,
        "subject": "Мировая экономика", "type": "seminar",
        "weeks": [15, 15], "room": "2/214"
    },
    # --- ЧЕТВЕРГ ---
    {
        "day": "thursday", "pair": 1,
        "subject": "Мировая экономика", "type": "seminar",
        "weeks": [4, 15], "room": "2/214"
    },
    {
        "day": "thursday", "pair": 2,
        "subject": "Стратегический менеджмент", "type": "lecture",
        "weeks": [4, 9], "room": "2/214"
    },
    {
        "day": "thursday", "pair": 2,
        "subject": "Международный гостиничный бизнес", "type": "seminar",
        "weeks": [10, 10], "room": "2/214"
    },
    {
        "day": "thursday", "pair": 2,
        "subject": "Качество и безопасность", "type": "seminar",
        "weeks": [11, 15], "room": "2/214"
    },
    {
        "day": "thursday", "pair": 3,
        "subject": "Стратегический менеджмент", "type": "seminar",
        "weeks": [6, 12], "room": "2/214"
    },
    {
        "day": "thursday", "pair": 3,
        "subject": "Качество и безопасность", "type": "seminar",
        "weeks": [13, 13], "room": "2/214"
    },
    # --- ПЯТНИЦА ---
    {
        "day": "friday", "pair": 1,
        "subject": "Стратегический менеджмент", "type": "seminar",
        "weeks": [4, 9], "room": "2/214"
    },
    {
        "day": "friday", "pair": 1,
        "subject": "Международный гостиничный бизнес", "type": "seminar",
        "weeks": [11, 15], "room": "2/214"
    },
    {
        "day": "friday", "pair": 2,
        "subject": "Мировая экономика", "type": "lecture",
        "weeks": [4, 8], "room": "2/214"
    },
    {
        "day": "friday", "pair": 2,
        "subject": "Качество и безопасность", "type": "lecture",
        "weeks": [9, 9], "room": "3/207"
    },
    {
        "day": "friday", "pair": 2,
        "subject": "Стратегический менеджмент", "type": "seminar",
        "weeks": [11, 15], "room": "2/214"
    },
    {
        "day": "friday", "pair": 3,
        "subject": "Международный гостиничный бизнес", "type": "lecture",
        "weeks": [4, 9], "room": "2/214"
    },
    {
        "day": "friday", "pair": 3,
        "subject": "Международный гостиничный бизнес", "type": "lecture",
        "weeks": [11, 11], "room": "2/214"
    }
]

def update_schedule():
    logger.info("🗑 Clearing old schedule...")
    existing = get_all_lessons()
    for lesson in existing:
        delete_lesson(lesson["id"])
    
    logger.info("🚀 Adding correct schedule...")
    count = 0
    for l in NEW_SCHEDULE:
        teacher = get_teacher(l["subject"], l["type"])
        chat_id = get_chat_id(l["subject"])
        
        lesson_id = add_lesson(
            day_of_week=l["day"],
            pair_number=l["pair"],
            subject=l["subject"],
            lesson_type=l["type"],
            week_start=l["weeks"][0],
            week_end=l["weeks"][1],
            room=l["room"],
            teacher=teacher,
            chat_id=chat_id
        )
        count += 1
        print(f"✅ Added: {l['day']} {l['pair']}p - {l['subject']}")
        
    logger.info(f"🎉 Done! Total lessons: {count}")

if __name__ == "__main__":
    update_schedule()
