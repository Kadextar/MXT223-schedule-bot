#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы базы данных
"""

import sys
from pathlib import Path
import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.database import get_lessons_by_day_and_week, get_all_lessons
from core.schedule_service import get_week_number, format_today_schedule
from core.time_utils import today_uz
from core.config import SEMESTER_START_DATE

print("=" * 60)
print("🧪 ТЕСТИРОВАНИЕ БАЗЫ ДАННЫХ")
print("=" * 60)

# Тест 1: Проверка общего количества занятий
all_lessons = get_all_lessons()
print(f"\n✅ Тест 1: Всего занятий в БД: {len(all_lessons)}")

# Тест 2: Проверка занятий на понедельник, 4 неделя
monday_week4 = get_lessons_by_day_and_week("monday", 4)
print(f"\n✅ Тест 2: Понедельник, 4 неделя: {len(monday_week4)} занятий")
for lesson in monday_week4:
    print(f"   • {lesson['pair']} пара: {lesson['subject']}")

# Тест 3: Проверка занятий на вторник, 10 неделя
tuesday_week10 = get_lessons_by_day_and_week("tuesday", 10)
print(f"\n✅ Тест 3: Вторник, 10 неделя: {len(tuesday_week10)} занятий")
for lesson in tuesday_week10:
    print(f"   • {lesson['pair']} пара: {lesson['subject']}")

# Тест 4: Текущая дата и неделя
today = today_uz()
current_week = get_week_number(today)
print(f"\n✅ Тест 4: Сегодня: {today}, Неделя семестра: {current_week}")

# Тест 5: Форматирование расписания (если семестр начался)
if today >= SEMESTER_START_DATE:
    print(f"\n✅ Тест 5: Расписание на сегодня:")
    print(format_today_schedule())
else:
    print(f"\n⏳ Тест 5: Семестр ещё не начался (начало: {SEMESTER_START_DATE})")

print("\n" + "=" * 60)
print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 60)
