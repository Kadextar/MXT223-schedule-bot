# ======================
# IMPORTS
# ======================

import os
import json
import logging
import datetime
from pathlib import Path

import pytz

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ======================
# TIME & TIMEZONE
# ======================

UZ_TZ = pytz.timezone("Asia/Tashkent")

def today_uz():
    return datetime.datetime.now(UZ_TZ).date()

# ======================
# CONFIG
# ======================

LAST_MESSAGES_FILE = Path(__file__).parent / "last_messages.json"
REMINDER_SETTINGS_FILE = Path(__file__).parent / "reminder_settings.json"

def load_last_messages():
    if LAST_MESSAGES_FILE.exists():
        try:
            with open(LAST_MESSAGES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # ключи из JSON — строки, приводим к int
                return {int(k): v for k, v in data.items()}
        except Exception as e:
            logger.error(f"Failed to load last messages: {e}")
    return {}

def save_last_messages():
    try:
        with open(LAST_MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(LAST_MESSAGES, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save last messages: {e}")

def load_reminder_settings():
    if REMINDER_SETTINGS_FILE.exists():
        try:
            with open(REMINDER_SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {int(k): bool(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Failed to load reminder settings: {e}")
    return {}

def save_reminder_settings():
    try:
        with open(REMINDER_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(REMINDER_SETTINGS, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save reminder settings: {e}")

def reminders_enabled(chat_id: int) -> bool:
    # по умолчанию — включены
    return REMINDER_SETTINGS.get(chat_id, True)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LAST_MESSAGES = load_last_messages()
REMINDER_SETTINGS = load_reminder_settings()

logger.info(f"Loaded {len(LAST_MESSAGES)} last messages from file")

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

# ID предметных групп
CHAT_STRATEGY = -1003789929485
CHAT_QUALITY = -1003798438883
CHAT_ECONOMY = -1003814835903
CHAT_INTL_BUSINESS = -1002982024678
CHAT_SCHEDULE_ONLY = -5103325045

ALL_SUBJECT_CHATS = (
    CHAT_STRATEGY,
    CHAT_QUALITY,
    CHAT_ECONOMY,
    CHAT_INTL_BUSINESS,
    CHAT_SCHEDULE_ONLY,
)

# ======================
# ACADEMIC SETTINGS
# ======================

REMINDER_MINUTES = [30, 15, 5]
SEMESTER_START_DATE = datetime.date(2026, 1, 1)  # 4 неделя
PAIR_START_TIMES = {
    1: datetime.time(8, 0),
    2: datetime.time(9, 30),
    3: datetime.time(11, 0),
}

# ======================
# SCHEDULE DATA
# ======================

SCHEDULE = {
    "monday": [
        {
            "pair": 1,
            "subject": "Качество и безопасность в гостиничной деятельности",
            "type": "lecture",
            "weeks": range(4, 9),
            "room": "2/214",
            "teacher": "Махмудова А.П.",
            "chat_id": CHAT_QUALITY,
        },
        {
            "pair": 1,
            "subject": "Стратегический менеджмент в гостиничном хозяйстве",
            "type": "lecture",
            "weeks": range(10, 16),
            "room": "2/214",
            "teacher": "Усманова Н.М.",
            "chat_id": CHAT_STRATEGY,
        },
        {
            "pair": 2,
            "subject": "Стратегический менеджмент в гостиничном хозяйстве",
            "type": "lecture",
            "weeks": range(4, 9),
            "room": "2/214",
            "teacher": "Усманова Н.М.",
            "chat_id": CHAT_STRATEGY,
        },
        {
            "pair": 2,
            "subject": "Мировая экономика и МЭО",
            "type": "lecture",
            "weeks": range(10, 16),
            "room": "2/214",
            "teacher": "Халимов Ш.Х.",
            "chat_id": CHAT_ECONOMY,
        },
        {
            "pair": 3,
            "subject": "Урок просвещения",
            "type": "lecture",
            "weeks": range(4, 16),
            "room": "3/305",
            "teacher": "—",
            "chat_id": CHAT_STRATEGY,
        },
    ],

    "tuesday": [
        {
            "pair": 1,
            "subject": "Мировая экономика и МЭО",
            "type": "lecture",
            "weeks": range(4, 11),
            "room": "2/214",
            "teacher": "Халимов Ш.Х.",
            "chat_id": CHAT_ECONOMY,
        },
        {
            "pair": 1,
            "subject": "Мировая экономика и МЭО",
            "type": "seminar",
            "weeks": range(11, 16),
            "room": "2/214",
            "teacher": "Амриева Ш.Ш.",
            "chat_id": CHAT_ECONOMY,
        },
        {
            "pair": 2,
            "subject": "Качество и безопасность в гостиничной деятельности",
            "type": "lecture",
            "weeks": range(4, 16),
            "room": "2/214",
            "teacher": "Махмудова А.П.",
            "chat_id": CHAT_QUALITY,
        },
        {
            "pair": 3,
            "subject": "Международный гостиничный бизнес",
            "type": "lecture",
            "weeks": range(4, 15),
            "room": "2/214",
            "teacher": "Амриддинова Р.С.",
            "chat_id": CHAT_INTL_BUSINESS,
        },
    ],

    "wednesday": [
        {
            "pair": 1,
            "subject": "Международный гостиничный бизнес",
            "type": "seminar",
            "weeks": range(4, 16),
            "room": "2/214",
            "teacher": "Мейлиев А.Н.",
            "chat_id": CHAT_INTL_BUSINESS,
        },
        {
            "pair": 2,
            "subject": "Качество и безопасность в гостиничной деятельности",
            "type": "seminar",
            "weeks": range(4, 16),
            "room": "2/214",
            "teacher": "Мир-Джафарова А.Д.",
            "chat_id": CHAT_QUALITY,
        },
        {
            "pair": 3,
            "subject": "Стратегический менеджмент",
            "type": "lecture",
            "weeks": [10],
            "room": "2/214",
            "teacher": "Усманова Н.М.",
            "chat_id": CHAT_STRATEGY,
        },
        {
            "pair": 3,
            "subject": "Мировая экономика",
            "type": "seminar",
            "weeks": [15],
            "room": "2/214",
            "teacher": "Амриева Ш.Ш.",
            "chat_id": CHAT_ECONOMY,
        },
    ],

    "thursday": [
        {
            "pair": 1,
            "subject": "Мировая экономика",
            "type": "seminar",
            "weeks": range(4, 16),
            "room": "2/214",
            "teacher": "Амриева Ш.Ш.",
            "chat_id": CHAT_ECONOMY,
        },
        {
            "pair": 2,
            "subject": "Стратегический менеджмент",
            "type": "lecture",
            "weeks": range(4, 10),
            "room": "2/214",
            "teacher": "Усманова Н.М.",
            "chat_id": CHAT_STRATEGY,
        },
        {
            "pair": 2,
            "subject": "Международный гостиничный бизнес",
            "type": "seminar",
            "weeks": [10],
            "room": "2/214",
            "teacher": "Мейлиев А.Н.",
            "chat_id": CHAT_INTL_BUSINESS,
        },
        {
            "pair": 2,
            "subject": "Качество и безопасность",
            "type": "seminar",
            "weeks": range(11, 16),
            "room": "2/214",
            "teacher": "Мир-Джафарова А.Д.",
            "chat_id": CHAT_QUALITY,
        },
        {
            "pair": 3,
            "subject": "Стратегический менеджмент",
            "type": "seminar",
            "weeks": range(6, 13),
            "room": "2/214",
            "teacher": "Бурхонова Н.М.",
            "chat_id": CHAT_STRATEGY,
        },
    ],

    "friday": [
        {
            "pair": 1,
            "subject": "Стратегический менеджмент",
            "type": "seminar",
            "weeks": range(4, 10),
            "room": "2/214",
            "teacher": "Бурхонова Н.М.",
            "chat_id": CHAT_STRATEGY,
        },
        {
            "pair": 1,
            "subject": "Международный гостиничный бизнес",
            "type": "seminar",
            "weeks": range(11, 16),
            "room": "2/214",
            "teacher": "Мейлиев А.Н.",
            "chat_id": CHAT_INTL_BUSINESS,
        },
        {
            "pair": 2,
            "subject": "Мировая экономика",
            "type": "lecture",
            "weeks": range(4, 9),
            "room": "2/214",
            "teacher": "Халимов Ш.Х.",
            "chat_id": CHAT_ECONOMY,
        },
        {
            "pair": 2,
            "subject": "Качество и безопасность",
            "type": "lecture",
            "weeks": [9],
            "room": "3/207",
            "teacher": "Махмудова А.П.",
            "chat_id": CHAT_QUALITY,
        },
        {
            "pair": 3,
            "subject": "Международный гостиничный бизнес",
            "type": "lecture",
            "weeks": range(4, 10),
            "room": "2/214",
            "teacher": "Амриддинова Р.С.",
            "chat_id": CHAT_INTL_BUSINESS,
        },
    ],
}

# ======================
# TIME HELPERS
# ======================

def uz_time_to_utc(hour: int, minute: int = 0):
    uz_now = datetime.datetime.now(UZ_TZ)
    uz_dt = uz_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    utc_dt = uz_dt.astimezone(pytz.UTC)
    return utc_dt.time()

# ======================
# LOGIC FUNCTIONS
# ======================

async def rebuild_today_reminders(context: ContextTypes.DEFAULT_TYPE):
    schedule_today_reminders(context.application)

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

    lines = []
    lines.append("📅 Расписание на сегодня:\n")

    # сортируем по номеру пары
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

def get_tomorrow_schedule():
    tomorrow = today_uz() + datetime.timedelta(days=1)
    week = get_week_number(tomorrow)

    weekday = tomorrow.strftime("%A").lower()
    lessons = SCHEDULE.get(weekday, [])

    return [
        lesson for lesson in lessons
        if week in lesson["weeks"]
    ]

def format_tomorrow_schedule():
    lessons = get_tomorrow_schedule()

    if not lessons:
        return (
            "🌙 Завтра занятий нет 🎉\n\n"
            "Можно спокойно отдыхать 😌"
        )

    lines = []
    lines.append("🌙 Расписание на завтра:\n")

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
        )

    return "\n".join(lines)

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

def daily_rebuild_reminders(context: ContextTypes.DEFAULT_TYPE):
    schedule_today_reminders(context.application)

def schedule_today_reminders(app: Application):
    try:
        today = today_uz()
        if today < SEMESTER_START_DATE:
            return

        # удаляем старые напоминания
        for job in app.job_queue.jobs():
            if job.callback == send_pair_reminder:
                job.schedule_removal()

        lessons = get_today_schedule()

        for lesson in lessons:
            pair_time = PAIR_START_TIMES.get(lesson["pair"])
            if not pair_time:
                continue

            lesson_datetime = UZ_TZ.localize(
                datetime.datetime.combine(today, pair_time)
            )

            for minutes in REMINDER_MINUTES:
                reminder_time = lesson_datetime - datetime.timedelta(minutes=minutes)

                if reminder_time <= datetime.datetime.now(UZ_TZ):
                    continue

                app.job_queue.run_once(
                    send_pair_reminder,
                    when=reminder_time,
                    data={
                        "lesson": lesson,
                        "minutes": minutes
                    }
                )

        logger.info("Daily reminders scheduled successfully")

    except Exception as e:
        logger.exception("❌ Error while scheduling daily reminders")

# ======================
# KEYBOARD
# ======================

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if today_uz() < SEMESTER_START_DATE:
        await update.message.reply_text(
            "📅 Учебный семестр начинается с 2 февраля.\n"
            "Пока занятий нет 😌"
        )
        return

    await update.message.reply_text(format_today_schedule())

async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if today_uz() < SEMESTER_START_DATE:
        await update.message.reply_text(
            "🌙 Занятия начнутся с 2 февраля.\n"
            "Пока можно отдыхать 😌"
        )
        return

    await update.message.reply_text(format_tomorrow_schedule())

keyboard = ReplyKeyboardMarkup(
    [
        ["📅 Сегодня"],
        ["📘 Лекция", "📒 Семинар"],
    ],
    resize_keyboard=True,
)

# ======================
# COMMANDS
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n"
        "Я бот расписания группы МХТ-223.\n"
        "Выбери действие:",
        reply_markup=keyboard
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Status command received")
    jobs_count = len(context.application.job_queue.jobs())

    await update.message.reply_text(
        "🤖 Статус бота\n\n"
        f"📅 Сегодня: {today_uz()}\n"
        f"🎓 Семестр начался: {'✅' if today_uz() >= SEMESTER_START_DATE else '❌'}\n"
        f"⏰ Активных задач: {jobs_count}"
    )

async def enable_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    REMINDER_SETTINGS[chat_id] = True
    save_reminder_settings()

    await update.message.reply_text(
        "🔔 Напоминания включены для этого чата ✅"
    )

async def disable_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    REMINDER_SETTINGS[chat_id] = False
    save_reminder_settings()

    await update.message.reply_text(
        "🔕 Напоминания отключены для этого чата ❌"
    )

# ======================
# BUTTON HANDLER
# ======================

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Incoming message: {update.message.text}")
    text = update.message.text

    if today_uz() < SEMESTER_START_DATE:
        await update.message.reply_text(
            "📅 Учебный семестр начинается с 2 февраля.\n"
            "Пока занятий нет 😌"
        )
        return

    if text == "📅 Сегодня":
        message = format_today_schedule()
        await update.message.reply_text(message)

    elif text == "📘 Лекция":
        await update.message.reply_text(
            "📘 Сегодня есть лекционные занятия.\n"
            "(детализация появится дальше)"
        )

    elif text == "📒 Семинар":
        await update.message.reply_text(
            "📒 Сегодня есть семинарские занятия.\n"
            "(детализация появится дальше)"
        )

# ======================
# AUTO MESSAGES
# ======================

async def send_morning_schedule(context: ContextTypes.DEFAULT_TYPE):
    today = today_uz()
    if today < SEMESTER_START_DATE:
        return
    
    text = (
        "🌅 Доброе утро!\n\n"
        "📅 Сегодня учебный день.\n"
        "Подробное расписание будет отправлено позже ⏰"
    )

    for chat_id in ALL_SUBJECT_CHATS:
        # удаляем прошлое сообщение бота
        last_id = LAST_MESSAGES.get(chat_id)
        if last_id:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=last_id)
            except:
                pass

        msg = await context.bot.send_message(chat_id=chat_id, text=text)
        LAST_MESSAGES[chat_id] = msg.message_id
        
    save_last_messages()

async def send_evening_schedule(context: ContextTypes.DEFAULT_TYPE):
    today = today_uz()
    if today < SEMESTER_START_DATE:
        return
    
    text = format_tomorrow_schedule()

    for chat_id in ALL_SUBJECT_CHATS:
        await context.bot.send_message(chat_id=chat_id, text=text)

# ======================
# MAIN
# ======================

def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("tomorrow", tomorrow_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("enable", enable_command))
    app.add_handler(CommandHandler("disable", disable_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    # утреннее сообщение
    app.job_queue.run_daily(
        send_morning_schedule,
        time=uz_time_to_utc(7, 0),
        days=(0, 1, 2, 3, 4),
    )

    # вечернее сообщение
    app.job_queue.run_daily(
        send_evening_schedule,
        time=uz_time_to_utc(20, 0),
        days=(0, 1, 2, 3, 4),
    )

    # напоминания при старте
    if today_uz() >= SEMESTER_START_DATE:
        schedule_today_reminders(app)

    # 🔧 ВАЖНО: функция должна быть С ОТСТУПОМ
    def rebuild_daily_reminders(context: ContextTypes.DEFAULT_TYPE):
        try:
            schedule_today_reminders(context.application)
            logger.info("Daily reminders rebuilt")
        except Exception:
            logger.exception("❌ Failed to rebuild daily reminders")

    # пересбор напоминаний каждый день в 20:00
    app.job_queue.run_daily(
        rebuild_daily_reminders,
        time=uz_time_to_utc(20, 0),
        days=(0, 1, 2, 3, 4),
    )

    logger.info("Bot started successfully")
    logger.info("Daily reminders scheduler initialized")

    app.run_polling()


if __name__ == "__main__":
    main()
