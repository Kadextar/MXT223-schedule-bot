#!/usr/bin/env python3
"""
Тестовый скрипт для проверки логики UX команд
"""

import sys
from pathlib import Path
import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.database import get_lessons_by_day_and_week
from core.schedule_service import get_week_number
from core.time_utils import today_uz
from core.config import SEMESTER_START_DATE

print("=" * 60)
print("🧪 ТЕСТИРОВАНИЕ ЛОГИКИ UX КОМАНД")
print("=" * 60)

today = today_uz()
week = get_week_number(today)

print(f"📅 Сегодня: {today} (Неделя {week})")

if today < SEMESTER_START_DATE:
    print("⚠️ Семестр ещё не начался, расписание неактивно.")
else:
    # Тест 1: Логика /today
    weekday = today.strftime("%A").lower()
    lessons_today = get_lessons_by_day_and_week(weekday, week)
    print(f"\n✅ Тест 1 (/today): Уроков сегодня: {len(lessons_today)}")
    
    # Тест 2: Логика /week
    print(f"\n✅ Тест 2 (/week): Проверка расписания на неделю {week}")
    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    total_week_lessons = 0
    
    for day in days:
        lessons = get_lessons_by_day_and_week(day, week)
        count = len(lessons)
        total_week_lessons += count
        print(f"   • {day}: {count} занятий")
        
    print(f"   Всего на неделе: {total_week_lessons}")

print("\n" + "=" * 60)
print("✅ ТЕСТЫ ЛОГИКИ ЗАВЕРШЕНЫ")
print("=" * 60)
print("\n📝 Теперь протестируйте команды в Telegram:")
print("   • /week — Красивое расписание на неделю")
print("   • /next — Ближайшая пара")
print("   • /today и /tomorrow")
print("   • Попробуйте навигацию по неделям (кнопки)")
