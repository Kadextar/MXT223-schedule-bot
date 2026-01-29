import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from core.handlers.commands import load
from core.handlers.commands import start, status, health
from core.handlers.buttons import handle_buttons
from core.handlers.admin_handlers import admin_menu, list_lessons, admin_callback_handler, reset_schedule, broadcast, init_students_command
from core.handlers.init_teachers import init_teachers_command
from core.handlers.admin_add_lesson import add_lesson_conversation
from core.handlers.admin_delete_lesson import delete_lesson_conversation
from core.handlers.user_commands import (
    today_schedule,
    tomorrow_schedule,
    next_lesson,
    week_schedule,
    week_navigation_callback,
)
from core.handlers.quick_actions import quick_actions_callback
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


async def post_init(application):
    """Set up bot commands menu after initialization"""
    from telegram import BotCommand
    
    commands = [
        BotCommand("start", "🏠 Главное меню"),
        BotCommand("today", "📅 Расписание на сегодня"),
        BotCommand("tomorrow", "📆 Расписание на завтра"),
        BotCommand("week", "📊 Расписание на неделю"),
        BotCommand("next", "⏰ Следующая пара"),
        BotCommand("load", "📈 Анализ нагрузки"),
        BotCommand("admin", "🔧 Панель администратора"),
    ]
    
    await application.bot.set_my_commands(commands)
    logger.info("✅ Bot commands menu set up")


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("load", load))

    # user commands
    app.add_handler(CommandHandler("today", today_schedule))
    app.add_handler(CommandHandler("tomorrow", tomorrow_schedule))
    app.add_handler(CommandHandler("next", next_lesson))
    app.add_handler(CommandHandler("week", week_schedule))

    # admin commands
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CommandHandler("list_lessons", list_lessons))
    app.add_handler(CommandHandler("reset_schedule", reset_schedule))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("init_students", init_students_command))
    app.add_handler(CommandHandler("init_teachers", init_teachers_command))
    
    # admin conversations
    app.add_handler(add_lesson_conversation)
    app.add_handler(delete_lesson_conversation)
    
    # callback handlers
    app.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^broadcast_"))
    app.add_handler(CallbackQueryHandler(week_navigation_callback, pattern="^week_"))
    app.add_handler(CallbackQueryHandler(quick_actions_callback, pattern="^quick_"))

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
        days=(0, 1, 2, 3, 4),
    )

    logger.info("🚀 Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
