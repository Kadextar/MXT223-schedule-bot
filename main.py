import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from core.handlers.commands import start, status, health
from core.handlers.buttons import handle_buttons
from core.reminders import schedule_today_reminders, rebuild_daily_reminders
from core.auto_messages import send_morning_schedule, send_evening_schedule
from core.time_utils import today_uz, uz_time_to_utc
from core.config import SEMESTER_START_DATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

WEEKDAYS = (0, 1, 2, 3, 4)  # Пн–Пт


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("health", health))

    # buttons
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    # auto messages
    app.job_queue.run_daily(
        send_morning_schedule,
        time=uz_time_to_utc(7, 0),
        days=WEEKDAYS,
    )

    app.job_queue.run_daily(
        send_evening_schedule,
        time=uz_time_to_utc(20, 0),
        days=WEEKDAYS,
    )

    # reminders
    if today_uz() >= SEMESTER_START_DATE:
        logger.info("📌 Scheduling today's reminders")
        schedule_today_reminders(app)

    app.job_queue.run_daily(
        rebuild_daily_reminders,
        time=uz_time_to_utc(20, 0),
        days=WEEKDAYS,
    )

    logger.info("🚀 Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
