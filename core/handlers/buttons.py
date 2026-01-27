from telegram import Update
from telegram.ext import ContextTypes

from core.schedule_service import (
    format_today_schedule,
    format_tomorrow_schedule,
)

from core.analytics.workload_chart import format_workload_chart
from core.analytics import analyze_week_load
from core.time_utils import today_uz
from core.config import SEMESTER_START_DATE
from core.ui.keyboards import MAIN_KEYBOARD

# 👇 добавим импорты для новых кнопок
from core.schedule_service import get_today_schedule
from core.config import PAIR_START_TIMES
import datetime
import pytz

UZ_TZ = pytz.timezone("Asia/Tashkent")


def get_next_lesson():
    lessons = get_today_schedule()
    if not lessons:
        return None

    now = datetime.datetime.now(UZ_TZ)

    for lesson in sorted(lessons, key=lambda x: x["pair"]):
        pair_time = PAIR_START_TIMES.get(lesson["pair"])
        if not pair_time:
            continue

        lesson_dt = UZ_TZ.localize(
            datetime.datetime.combine(today_uz(), pair_time)
        )

        if lesson_dt > now:
            return lesson

    return None


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ⛔ семестр не начался
    if today_uz() < SEMESTER_START_DATE:
        await update.message.reply_text(
            "📅 Учебный семестр начинается с 2 февраля.\n"
            "Пока занятий нет 😌",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    # 📅 Сегодня
    if text == "📅 Сегодня":
        await update.message.reply_text(format_today_schedule())

    # 🌙 Завтра
    elif text == "🌙 Завтра":
        await update.message.reply_text(format_tomorrow_schedule())

    elif text == "📊 Нагрузка недели":
        await update.message.reply_text(
            format_workload_chart()
        )

    elif text == "📊 Нагрузка недели":
        data = analyze_week_load()

        day_names = {
            "monday": "Пн",
            "tuesday": "Вт",
            "wednesday": "Ср",
            "thursday": "Чт",
            "friday": "Пт",
        }

        days_text = "\n".join(
            f"• {day_names.get(day, day)} — {hours} ч"
            for day, hours in data["day_load"].items()
        )

        await update.message.reply_text(
            f"📊 Нагрузка недели ({data['week']} неделя)\n\n"
            f"📘 Лекций: {data['lectures']}\n"
            f"📒 Семинаров: {data['seminars']}\n"
            f"⏰ Учебных часов: {data['total_hours']}\n\n"
            f"🔥 Самый загруженный день: {day_names.get(data['hardest_day'], '—')}\n"
            f"😌 Самый лёгкий день: {day_names.get(data['easiest_day'], '—')}\n\n"
            f"📅 По дням:\n{days_text}"
        )

    # ⏭ Следующая пара
    elif text == "⏭ Следующая пара":
        lesson = get_next_lesson()

        if not lesson:
            await update.message.reply_text("🎉 Сегодня больше нет пар")
            return

        pair = lesson["pair"]
        time = PAIR_START_TIMES[pair].strftime("%H:%M")
        lesson_type = "Лекция" if lesson["type"] == "lecture" else "Семинар"

        await update.message.reply_text(
            "⏭ Следующая пара:\n\n"
            f"🕒 {pair} пара ({time})\n"
            f"📘 {lesson['subject']}\n"
            f"🎓 {lesson_type}\n"
            f"👩‍🏫 {lesson['teacher']}\n"
            f"🏫 {lesson['room']}"
        )

    # 🧠 Статус дня
    elif text == "🧠 Статус дня":
        lessons = get_today_schedule()
        next_lesson = get_next_lesson()

        next_text = (
            f"{next_lesson['pair']} пара"
            if next_lesson else "нет"
        )

        await update.message.reply_text(
            "🧠 Статус дня\n\n"
            f"📅 Сегодня: {today_uz().strftime('%d.%m.%Y')}\n"
            f"📘 Пар сегодня: {len(lessons)}\n"
            f"⏰ Ближайшая: {next_text}\n"
            f"🔔 Напоминания: включены"
        )

    # 🤔 неизвестно
    else:
        await update.message.reply_text(
            "🤔 Я не понял команду.\n"
            "Используй кнопки ниже 👇",
            reply_markup=MAIN_KEYBOARD,
        )
