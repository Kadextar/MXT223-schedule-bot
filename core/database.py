import sqlite3
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Путь к базе данных
DB_PATH = Path(__file__).parent.parent / "schedule.db"


def get_connection():
    """Создаёт подключение к базе данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Возвращать строки как словари
    return conn


def init_database():
    """Инициализирует базу данных и создаёт таблицы"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week TEXT NOT NULL,
            pair_number INTEGER NOT NULL,
            subject TEXT NOT NULL,
            lesson_type TEXT NOT NULL,
            week_start INTEGER NOT NULL,
            week_end INTEGER NOT NULL,
            room TEXT NOT NULL,
            teacher TEXT NOT NULL,
            chat_id INTEGER NOT NULL
        )
    """)
    
    # Индексы для быстрого поиска
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_day_week 
        ON schedule(day_of_week, week_start, week_end)
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Database initialized at {DB_PATH}")


def add_lesson(
    day_of_week: str,
    pair_number: int,
    subject: str,
    lesson_type: str,
    week_start: int,
    week_end: int,
    room: str,
    teacher: str,
    chat_id: int
) -> int:
    """Добавляет занятие в расписание"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO schedule 
        (day_of_week, pair_number, subject, lesson_type, week_start, week_end, room, teacher, chat_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (day_of_week, pair_number, subject, lesson_type, week_start, week_end, room, teacher, chat_id))
    
    lesson_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return lesson_id


def get_lessons_by_day_and_week(day_of_week: str, week_number: int) -> List[Dict[str, Any]]:
    """Получает занятия для конкретного дня недели и номера недели"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM schedule
        WHERE day_of_week = ?
        AND week_start <= ?
        AND week_end >= ?
        ORDER BY pair_number
    """, (day_of_week, week_number, week_number))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Конвертируем в список словарей
    lessons = []
    for row in rows:
        lessons.append({
            "id": row["id"],
            "day_of_week": row["day_of_week"],
            "pair": row["pair_number"],
            "subject": row["subject"],
            "type": row["lesson_type"],
            "week_start": row["week_start"],
            "week_end": row["week_end"],
            "room": row["room"],
            "teacher": row["teacher"],
            "chat_id": row["chat_id"]
        })
    
    return lessons


def get_all_lessons() -> List[Dict[str, Any]]:
    """Получает все занятия из расписания"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM schedule ORDER BY day_of_week, pair_number")
    rows = cursor.fetchall()
    conn.close()
    
    lessons = []
    for row in rows:
        lessons.append({
            "id": row["id"],
            "day_of_week": row["day_of_week"],
            "pair": row["pair_number"],
            "subject": row["subject"],
            "type": row["lesson_type"],
            "week_start": row["week_start"],
            "week_end": row["week_end"],
            "room": row["room"],
            "teacher": row["teacher"],
            "chat_id": row["chat_id"]
        })
    
    return lessons


def delete_lesson(lesson_id: int) -> bool:
    """Удаляет занятие по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM schedule WHERE id = ?", (lesson_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted


def update_lesson(
    lesson_id: int,
    day_of_week: Optional[str] = None,
    pair_number: Optional[int] = None,
    subject: Optional[str] = None,
    lesson_type: Optional[str] = None,
    week_start: Optional[int] = None,
    week_end: Optional[int] = None,
    room: Optional[str] = None,
    teacher: Optional[str] = None,
    chat_id: Optional[int] = None
) -> bool:
    """Обновляет занятие (только указанные поля)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Формируем запрос динамически
    updates = []
    params = []
    
    if day_of_week is not None:
        updates.append("day_of_week = ?")
        params.append(day_of_week)
    if pair_number is not None:
        updates.append("pair_number = ?")
        params.append(pair_number)
    if subject is not None:
        updates.append("subject = ?")
        params.append(subject)
    if lesson_type is not None:
        updates.append("lesson_type = ?")
        params.append(lesson_type)
    if week_start is not None:
        updates.append("week_start = ?")
        params.append(week_start)
    if week_end is not None:
        updates.append("week_end = ?")
        params.append(week_end)
    if room is not None:
        updates.append("room = ?")
        params.append(room)
    if teacher is not None:
        updates.append("teacher = ?")
        params.append(teacher)
    if chat_id is not None:
        updates.append("chat_id = ?")
        params.append(chat_id)
    
    if not updates:
        return False
    
    params.append(lesson_id)
    query = f"UPDATE schedule SET {', '.join(updates)} WHERE id = ?"
    
    cursor.execute(query, params)
    updated = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return updated


def clear_all_lessons():
    """Удаляет все занятия (для миграции)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM schedule")
    
    conn.commit()
    conn.close()
    logger.info("🗑 All lessons cleared from database")
