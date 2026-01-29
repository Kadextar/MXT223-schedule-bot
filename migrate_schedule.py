#!/usr/bin/env python3
"""
Скрипт миграции расписания из Python в SQLite
Запуск: python migrate_schedule.py
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

from core.database import init_database, add_lesson, clear_all_lessons, get_all_lessons
from core.schedule_data import SCHEDULE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_schedule():
    """Мигрирует расписание из schedule_data.py в SQLite"""
    
    logger.info("🚀 Starting schedule migration...")
    
    # Инициализируем БД
    init_database()
    
    # Очищаем старые данные (если есть)
    clear_all_lessons()
    
    total_lessons = 0
    
    # Переносим данные
    for day_name, lessons in SCHEDULE.items():
        logger.info(f"📅 Migrating {day_name}...")
        
        for lesson in lessons:
            # Конвертируем weeks (range или list) в week_start и week_end
            weeks = lesson["weeks"]
            
            if isinstance(weeks, range):
                week_start = weeks.start
                week_end = weeks.stop - 1  # range не включает последний элемент
            elif isinstance(weeks, list):
                week_start = min(weeks)
                week_end = max(weeks)
            else:
                logger.warning(f"⚠️ Unknown weeks format: {weeks}")
                continue
            
            # Добавляем в БД
            add_lesson(
                day_of_week=day_name,
                pair_number=lesson["pair"],
                subject=lesson["subject"],
                lesson_type=lesson["type"],
                week_start=week_start,
                week_end=week_end,
                room=lesson["room"],
                teacher=lesson["teacher"],
                chat_id=lesson["chat_id"]
            )
            
            total_lessons += 1
    
    logger.info(f"✅ Migration completed! Total lessons: {total_lessons}")
    
    # Проверяем результат
    all_lessons = get_all_lessons()
    logger.info(f"📊 Lessons in database: {len(all_lessons)}")
    
    # Статистика по дням
    days_count = {}
    for lesson in all_lessons:
        day = lesson["day_of_week"]
        days_count[day] = days_count.get(day, 0) + 1
    
    logger.info("📈 Lessons per day:")
    for day, count in sorted(days_count.items()):
        logger.info(f"  • {day}: {count}")


if __name__ == "__main__":
    migrate_schedule()
