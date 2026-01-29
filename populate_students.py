"""
Скрипт для инициализации студентов с начальными паролями
"""
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.database import init_database, add_student

# Список студентов с начальными паролями
STUDENTS = [
    {"telegram_id": "1748727700", "password": "robiya2026", "name": "Робия"},
    {"telegram_id": "1427112602", "password": "sardor2026", "name": "Сардор"},
    {"telegram_id": "1937736219", "password": "khislatbek2026", "name": "Хислатбек"},
    {"telegram_id": "207103078", "password": "timur2026", "name": "Тимур"},
    {"telegram_id": "5760110758", "password": "amir2026", "name": "Амир"},
    {"telegram_id": "1362668588", "password": "muhammad2026", "name": "Мухаммад"},
    {"telegram_id": "2023499343", "password": "abdumalik2026", "name": "Абдумалик"},
    {"telegram_id": "1214641616", "password": "azamat2026", "name": "Азамат"},
    {"telegram_id": "1020773033", "password": "nozima2026", "name": "Нозима"}
]

def populate_students():
    """Заполняет таблицу students начальными данными"""
    print("🔧 Инициализация базы данных...")
    init_database()
    
    print("👥 Добавление студентов...")
    for student in STUDENTS:
        success = add_student(
            telegram_id=student["telegram_id"],
            password=student["password"],
            name=student["name"]
        )
        if success:
            print(f"✅ {student['name']} (ID: {student['telegram_id']}, пароль: {student['password']})")
        else:
            print(f"⚠️  {student['name']} - возможно уже существует")
    
    print("\n🎉 Инициализация завершена!")
    print("\n📋 Начальные пароли:")
    for student in STUDENTS:
        print(f"   {student['name']}: {student['password']}")

if __name__ == "__main__":
    populate_students()
