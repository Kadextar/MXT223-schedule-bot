import datetime
import logging
from telegram.ext import ContextTypes, Application

from core.time_utils import UZ_TZ, today_uz
from core.config import (
    SEMESTER_START_DATE,
    REMINDER_MINUTES,
    PAIR_START_TIMES,
    CHAT_SCHEDULE_ONLY,
)
from core.schedule_service import get_today_schedule
from core.storage import load_json, REMINDER_SETTINGS_FILE

logger = logging.getLogger(__name__)

REMINDER_SETTINGS = load_json(REMINDER_SETTINGS_FILE)
logger.info(f"Loaded reminder settings: {len(REMINDER_SETTINGS)} chats")


def reminders_enabled(chat_id: int) -> bool:
    return REMINDER_SETTINGS.get(chat_id, True)


async def send_pair_reminder(context: ContextTypes.DEFAULT_TYPE):
    try:
        lesson = context.job.data["lesson"]
        minutes = context.job.data["minutes"]
        chat_id = lesson["chat_id"]

        subject_enabled = reminders_enabled(chat_id)
        schedule_enabled = reminders_enabled(CHAT_SCHEDULE_ONLY)

        if not subject_enabled and not schedule_enabled:
            return

        lesson_type = "Лекция" if lesson["type"] == "lecture" else "Семинар"
        emoji = "🕒" if minutes == 30 else "⏰" if minutes == 15 else "🚨"

        text = (
            f"{emoji} До пары осталось {minutes} минут!\n\n"
            f"📘 {lesson['subject']}\n"
            f"🎓 {lesson_type}\n"
            f"👩‍🏫 {lesson['teacher']}\n"
            f"🏫 {lesson['room']}"
        )

        if subject_enabled:
            await context.bot.send_message(chat_id=chat_id, text=text)

        if chat_id != CHAT_SCHEDULE_ONLY and schedule_enabled:
            await context.bot.send_message(chat_id=CHAT_SCHEDULE_ONLY, text=text)

    except Exception:
        logger.exception("❌ Failed to send pair reminder")


def schedule_today_reminders(app: Application):
    logger.info("⏰ Scheduling today reminders...")

    today = today_uz()
    if today < SEMESTER_START_DATE:
        return

    # удаляем старые напоминания
    for job in app.job_queue.jobs():
        if job.callback == send_pair_reminder:
            job.schedule_removal()

    for lesson in get_today_schedule():
        pair_time = PAIR_START_TIMES.get(lesson["pair_number"])
        if not pair_time:
            continue

        lesson_dt = UZ_TZ.localize(
            datetime.datetime.combine(today, pair_time)
        )

        for minutes in REMINDER_MINUTES:
            remind_at = lesson_dt - datetime.timedelta(minutes=minutes)
            if remind_at <= datetime.datetime.now(UZ_TZ):
                continue

            app.job_queue.run_once(
                send_pair_reminder,
                when=remind_at,
                data={
                    "lesson": lesson,
                    "minutes": minutes,
                },
            )

    logger.info("Daily reminders scheduled")


def rebuild_daily_reminders(context: ContextTypes.DEFAULT_TYPE):
    logger.info("🔁 Rebuilding daily reminders")
    schedule_today_reminders(context.application)
