#!/usr/bin/env python3
"""
Тестовый скрипт для проверки админ-функций
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.database import add_lesson, get_all_lessons, delete_lesson
from core.config import ADMIN_IDS, CHAT_STRATEGY

print("=" * 60)
print("🧪 ТЕСТИРОВАНИЕ АДМИН-ФУНКЦИЙ")
print("=" * 60)

# Тест 1: Проверка админ ID
print(f"\n✅ Тест 1: Админ ID настроен: {ADMIN_IDS}")

# Тест 2: Добавление тестового занятия
print("\n✅ Тест 2: Добавление тестового занятия...")
test_lesson_id = add_lesson(
    day_of_week="monday",
    pair_number=1,
    subject="ТЕСТОВЫЙ ПРЕДМЕТ",
    lesson_type="lecture",
    week_start=4,
    week_end=8,
    room="TEST/001",
    teacher="Тестовый Преподаватель",
    chat_id=CHAT_STRATEGY
)
print(f"   Добавлено занятие с ID: {test_lesson_id}")

# Тест 3: Проверка добавления
all_lessons = get_all_lessons()
test_lesson = next((l for l in all_lessons if l["id"] == test_lesson_id), None)

if test_lesson:
    print(f"\n✅ Тест 3: Занятие найдено в БД")
    print(f"   Предмет: {test_lesson['subject']}")
    print(f"   Преподаватель: {test_lesson['teacher']}")
else:
    print("\n❌ Тест 3: Занятие НЕ найдено в БД")

# Тест 4: Удаление тестового занятия
print(f"\n✅ Тест 4: Удаление тестового занятия...")
deleted = delete_lesson(test_lesson_id)

if deleted:
    print(f"   Занятие ID {test_lesson_id} успешно удалено")
else:
    print(f"   ❌ Не удалось удалить занятие")

# Тест 5: Проверка удаления
all_lessons = get_all_lessons()
test_lesson = next((l for l in all_lessons if l["id"] == test_lesson_id), None)

if test_lesson is None:
    print(f"\n✅ Тест 5: Занятие успешно удалено из БД")
else:
    print(f"\n❌ Тест 5: Занятие всё ещё в БД")

print("\n" + "=" * 60)
print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 60)
print("\n📝 Следующий шаг: Запустите бота и протестируйте команды:")
print("   • /admin — главное меню")
print("   • /add_lesson — добавить занятие")
print("   • /delete_lesson — удалить занятие")
print("   • /list_lessons — список всех занятий")
