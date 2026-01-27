# core/schedule_service.py

from core.schedule_data import SCHEDULE
from core.config import PAIR_START_TIMES, SEMESTER_START_DATE
from core.time_utils import today_uz
import datetime


def get_week_number(today: datetime.date) -> int:
    delta = today - SEMESTER_START_DATE
    return 4 + delta.days // 7


def get_today_schedule():
    today = today_uz()
    week = get_week_number(today)

    weekday = today.strftime("%A").lower()
    lessons = SCHEDULE.get(weekday, [])

    return [
        lesson for lesson in lessons
        if week in lesson["weeks"]
    ]


def format_today_schedule():
    lessons = get_today_schedule()

    if not lessons:
        return "📅 Сегодня занятий нет 🎉"

    lines = ["📅 Расписание на сегодня:\n"]
    lessons = sorted(lessons, key=lambda x: x["pair"])

    for lesson in lessons:
        pair = lesson["pair"]
        time = PAIR_START_TIMES.get(pair)
        time_str = time.strftime("%H:%M") if time else "—"
        lesson_type = "Лекция" if lesson["type"] == "lecture" else "Семинар"

        lines.append(
            f"⏰ {pair} пара ({time_str})\n"
            f"📘 {lesson['subject']}\n"
            f"🎓 {lesson_type}\n"
            f"👩‍🏫 {lesson['teacher']}\n"
            f"🏫 {lesson['room']}\n"
            "——————————————\n"
        )

    return "\n".join(lines)


def format_tomorrow_schedule():
    tomorrow = today_uz() + datetime.timedelta(days=1)
    week = get_week_number(tomorrow)

    weekday = tomorrow.strftime("%A").lower()
    lessons = SCHEDULE.get(weekday, [])

    lessons = [l for l in lessons if week in l["weeks"]]

    if not lessons:
        return "🌙 Завтра занятий нет 🎉"

    lines = ["🌙 Расписание на завтра:\n"]

    for lesson in lessons:
        pair = lesson["pair"]
        time = PAIR_START_TIMES.get(pair)
        time_str = time.strftime("%H:%M") if time else "—"
        lesson_type = "Лекция" if lesson["type"] == "lecture" else "Семинар"

        lines.append(
            f"⏰ {pair} пара ({time_str})\n"
            f"📘 {lesson['subject']}\n"
            f"🎓 {lesson_type}\n"
            f"👩‍🏫 {lesson['teacher']}\n"
            f"🏫 {lesson['room']}\n"
        )

    return "\n".join(lines)
