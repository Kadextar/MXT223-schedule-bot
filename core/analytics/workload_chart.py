from core.schedule_data import SCHEDULE
from core.schedule_service import get_week_number
from core.time_utils import today_uz
import datetime


def calculate_weekly_workload():
    today = today_uz()
    week = get_week_number(today)

    workload = {}

    for day, lessons in SCHEDULE.items():
        count = 0
        for lesson in lessons:
            if week in lesson["weeks"]:
                count += 1
        workload[day] = count

    return workload


def format_workload_chart():
    workload = calculate_weekly_workload()

    day_names = {
        "monday": "Пн",
        "tuesday": "Вт",
        "wednesday": "Ср",
        "thursday": "Чт",
        "friday": "Пт",
    }

    lines = ["📊 Нагрузка недели\n"]

    max_day = max(workload, key=workload.get)
    min_day = min(workload, key=workload.get)

    for day, count in workload.items():
        bar = "█" * count if count > 0 else "—"
        lines.append(f"{day_names.get(day, day)}: {bar} ({count} пары)")

    lines.append("")
    lines.append(f"🔥 Самый загруженный день: {day_names[max_day]} ({workload[max_day]} пары)")
    lines.append(f"😌 Самый лёгкий день: {day_names[min_day]} ({workload[min_day]} пары)")

    return "\n".join(lines)