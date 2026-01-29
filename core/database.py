import os
import sqlite3
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

logger = logging.getLogger(__name__)

# Путь к локальной базе данных (SQLite)
DB_PATH = Path(__file__).parent.parent / "schedule.db"

# URL базы данных (PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")

class PostgresCursorWrapper:
    """Обертка для курсора Postgres для совместимости с синтаксисом SQLite (?)"""
    def __init__(self, cursor):
        self.cursor = cursor
        self.lastrowid = None
        self.rowcount = 0

    def execute(self, sql: str, params=()):
        # Заменяем ? на %s для Postgres
        pg_sql = sql.replace('?', '%s')
        try:
            self.cursor.execute(pg_sql, params)
            self.rowcount = self.cursor.rowcount
            
            # Попытка получить lastrowid если это был INSERT с RETURNING id (нужно для add_lesson)
            # В SQLite lastrowid работает автоматом, в PG нужно RETURNING id
            if "INSERT" in sql.upper() and not "RETURNING" in sql.upper():
                 # Мы не можем постфактум получить ID без RETURNING в PG
                 # Поэтому логика add_lesson должна быть чуть адаптирована или здесь хак
                 pass
        except Exception as e:
            logger.error(f"SQL Error: {e} | Query: {pg_sql}")
            raise e
        return self

    def fetchall(self):
        return self.cursor.fetchall()
    
    def fetchone(self):
        return self.cursor.fetchone()

    def close(self):
        self.cursor.close()

def get_connection():
    """Создаёт подключение к базе данных (SQLite или Postgres)"""
    if DATABASE_URL:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        try:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to Postgres: {e}")
            raise e
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_database():
    """Инициализирует базу данных и создаёт таблицы"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Для Postgres синтаксис AUTOINCREMENT -> SERIAL/GENERATED
    # SQLite: INTEGER PRIMARY KEY AUTOINCREMENT
    # Postgres: SERIAL PRIMARY KEY
    
    is_postgres = bool(DATABASE_URL)
    
    id_type = "SERIAL PRIMARY KEY" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
    chat_id_type = "BIGINT" if is_postgres else "INTEGER"
    
    sql = f"""
        CREATE TABLE IF NOT EXISTS schedule (
            id {id_type},
            day_of_week TEXT NOT NULL,
            pair_number INTEGER NOT NULL,
            subject TEXT NOT NULL,
            lesson_type TEXT NOT NULL,
            week_start INTEGER NOT NULL,
            week_end INTEGER NOT NULL,
            room TEXT NOT NULL,
            teacher TEXT NOT NULL,
            chat_id {chat_id_type} NOT NULL
        )
    """
    
    cursor.execute(sql)
    
    # Announcements table
    announcements_sql = f"""
        CREATE TABLE IF NOT EXISTS announcements (
            id {id_type},
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """
    cursor.execute(announcements_sql)
    
    # Индексы
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_day_week 
        ON schedule(day_of_week, week_start, week_end)
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Database initialized ({'Postgres' if is_postgres else 'SQLite'})")


def execute_query(sql: str, params=(), fetch_one=False, fetch_all=False, commit=False, return_id=False):
    """Универсальная функция выполнения запроса"""
    conn = get_connection()
    cursor = conn.cursor()
    
    is_postgres = bool(DATABASE_URL)
    
    # Адаптация синтаксиса
    if is_postgres:
        final_sql = sql.replace('?', '%s')
        # Для получения ID в Postgres нужно добавить RETURNING id
        if return_id and "INSERT" in final_sql.upper() and "RETURNING" not in final_sql.upper():
            final_sql += " RETURNING id"
    else:
        final_sql = sql
        
    try:
        cursor.execute(final_sql, params)
        
        result = None
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        elif return_id:
            if is_postgres:
                row = cursor.fetchone()
                result = row['id'] if row else None
            else:
                result = cursor.lastrowid
                
        if commit:
            conn.commit()
            
        return result
        
    except Exception as e:
        logger.error(f"DB Error: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

# --- API Функции (переписаны на execute_query для совместимости) ---

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
    sql = """
        INSERT INTO schedule 
        (day_of_week, pair_number, subject, lesson_type, week_start, week_end, room, teacher, chat_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    return execute_query(
        sql, 
        (day_of_week, pair_number, subject, lesson_type, week_start, week_end, room, teacher, chat_id),
        commit=True,
        return_id=True
    )

def get_lessons_by_day_and_week(day_of_week: str, week_number: int) -> List[Dict[str, Any]]:
    sql = """
        SELECT * FROM schedule
        WHERE day_of_week = ?
        AND week_start <= ?
        AND week_end >= ?
        ORDER BY pair_number
    """
    rows = execute_query(sql, (day_of_week, week_number, week_number), fetch_all=True)
    return [dict(row) for row in rows]

def get_all_lessons() -> List[Dict[str, Any]]:
    sql = "SELECT * FROM schedule ORDER BY day_of_week, pair_number"
    rows = execute_query(sql, fetch_all=True)
    return [dict(row) for row in rows]

def delete_lesson(lesson_id: int) -> bool:
    sql = "DELETE FROM schedule WHERE id = ?"
    # Для проверки удаления нам нужно знать rowcount.
    # execute_query возвращает result, но не rowcount.
    # Реализуем удаление напрямую
    conn = get_connection()
    cursor = conn.cursor()
    
    is_postgres = bool(DATABASE_URL)
    real_sql = sql.replace('?', '%s') if is_postgres else sql
    
    cursor.execute(real_sql, (lesson_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def update_lesson(
    lesson_id: int,
    day_of_week=None, pair_number=None, subject=None, lesson_type=None,
    week_start=None, week_end=None, room=None, teacher=None, chat_id=None
) -> bool:
    updates = []
    params = []
    
    if day_of_week is not None: updates.append("day_of_week = ?"); params.append(day_of_week)
    if pair_number is not None: updates.append("pair_number = ?"); params.append(pair_number)
    if subject is not None: updates.append("subject = ?"); params.append(subject)
    if lesson_type is not None: updates.append("lesson_type = ?"); params.append(lesson_type)
    if week_start is not None: updates.append("week_start = ?"); params.append(week_start)
    if week_end is not None: updates.append("week_end = ?"); params.append(week_end)
    if room is not None: updates.append("room = ?"); params.append(room)
    if teacher is not None: updates.append("teacher = ?"); params.append(teacher)
    if chat_id is not None: updates.append("chat_id = ?"); params.append(chat_id)
    
    if not updates: return False
    
    params.append(lesson_id)
    sql = f"UPDATE schedule SET {', '.join(updates)} WHERE id = ?"
    
    conn = get_connection()
    cursor = conn.cursor()
    is_postgres = bool(DATABASE_URL)
    real_sql = sql.replace('?', '%s') if is_postgres else sql
    
    cursor.execute(real_sql, params)
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def clear_all_lessons():
    execute_query("DELETE FROM schedule", commit=True)

# --- Announcement Functions ---

def add_announcement(message: str) -> int:
    """Добавляет новое объявление и деактивирует старые"""
    conn = get_connection()
    cursor = conn.cursor()
    is_postgres = bool(DATABASE_URL)
    
    # Деактивируем все старые объявления
    deactivate_sql = "UPDATE announcements SET is_active = FALSE" if not is_postgres else "UPDATE announcements SET is_active = FALSE"
    cursor.execute(deactivate_sql)
    
    # Добавляем новое
    insert_sql = "INSERT INTO announcements (message, is_active) VALUES (?, TRUE)"
    if is_postgres:
        insert_sql = insert_sql.replace('?', '%s') + " RETURNING id"
    
    cursor.execute(insert_sql.replace('?', '%s') if is_postgres else insert_sql, (message,))
    
    if is_postgres:
        row = cursor.fetchone()
        announcement_id = row['id'] if row else None
    else:
        announcement_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return announcement_id

def get_active_announcement():
    """Получает активное объявление"""
    sql = "SELECT * FROM announcements WHERE is_active = TRUE ORDER BY created_at DESC LIMIT 1"
    result = execute_query(sql, fetch_one=True)
    return dict(result) if result else None

def deactivate_all_announcements():
    """Деактивирует все объявления"""
    execute_query("UPDATE announcements SET is_active = FALSE", commit=True)
