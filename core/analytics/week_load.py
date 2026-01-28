import datetime
from core.schedule_data import SCHEDULE
from core.schedule_service import get_week_number
from core.time_utils import today_uz


def analyze_week_load():
    today = today_uz()
    week = get_week_number(today)

    day_load = {}
    lectures = 0
    seminars = 0
    total_pairs = 0

    for day, lessons in SCHEDULE.items():
        pairs_today = [
            l for l in lessons if week in l["weeks"]
        ]
        hours = len(pairs_today) * 2
        day_load[day] = hours

        for l in pairs_today:
            total_pairs += 1
            if l["type"] == "lecture":
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