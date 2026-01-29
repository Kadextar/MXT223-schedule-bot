import datetime
from core.database import get_lessons_by_day_and_week
from core.schedule_service import get_week_number
from core.time_utils import today_uz


def analyze_week_load():
    today = today_uz()
    week = get_week_number(today)

    day_load = {}
    lectures = 0
    seminars = 0
    total_pairs = 0

    # Дни недели
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    for day in weekdays:
        # Получаем занятия из БД для каждого дня
        lessons = get_lessons_by_day_and_week(day, week)
        
        hours = len(lessons) * 2
        day_load[day] = hours

        for lesson in lessons:
            total_pairs += 1
            if lesson["type"] == "lecture":
                lectures += 1
            else:
                seminars += 1

    total_hours = total_pairs * 2

    hardest_day = max(day_load, key=day_load.get) if day_load else None
    easiest_day = min(day_load, key=day_load.get) if day_load else None

    return {
        "week": week,
        "lectures": lectures,
        "seminars": seminars,
        "total_hours": total_hours,
        "day_load": day_load,
        "hardest_day": hardest_day,
        "easiest_day": easiest_day,
    }