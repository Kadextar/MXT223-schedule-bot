import os
import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ======================
# CONFIG
# ======================

LAST_MESSAGES = {}

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

# ID предметных групп
CHAT_STRATEGY = -1003789929485
CHAT_QUALITY = -1003798438883
CHAT_ECONOMY = -1003814835903
CHAT_INTL_BUSINESS = -1002982024678

ALL_SUBJECT_CHATS = (
    CHAT_STRATEGY,
    CHAT_QUALITY,
    CHAT_ECONOMY,
    CHAT_INTL_BUSINESS,
)

# ======================
# ACADEMIC SETTINGS
# ======================

SEMESTER_START_DATE = datetime.date(2026, 2, 2)  # 4 неделя
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
    ],

    # остальные дни добавим следующим шагом
}

# ======================
# LOGIC FUNCTIONS
# ======================

def get_week_number(today: datetime.date) -> int:
    delta = today - SEMESTER_START_DATE
    return 4 + delta.days // 7

def get_today_schedule():
    today = datetime.date.today()
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
        )

    return "\n".join(lines)

async def send_pair_reminder(context: ContextTypes.DEFAULT_TYPE):
    lesson = context.job.data

    lesson_type = "Лекция" if lesson["type"] == "lecture" else "Семинар"

    text = (
        "⏰ Напоминание!\n"
        "Через 15 минут начинается пара\n\n"
        f"📘 {lesson['subject']}\n"
        f"🎓 {lesson_type}\n"
        f"👩‍🏫 {lesson['teacher']}\n"
        f"🏫 {lesson['room']}"
    )

    await context.bot.send_message(
        chat_id=lesson["chat_id"],
        text=text
    )

def schedule_today_reminders(app: Application):
    # чистим старые напоминания
    for job in app.job_queue.jobs():
        if job.callback == send_pair_reminder:
            job.schedule_removal()

    today = datetime.date.today()
    lessons = get_today_schedule()

    for lesson in lessons:
        pair_time = PAIR_START_TIMES.get(lesson["pair"])
        if not pair_time:
            continue

        lesson_datetime = datetime.datetime.combine(today, pair_time)
        reminder_time = lesson_datetime - datetime.timedelta(minutes=15)

        if reminder_time <= datetime.datetime.now():
            continue

        app.job_queue.run_once(
            send_pair_reminder,
            when=reminder_time,
            data=lesson
        )

# ======================
# KEYBOARD
# ======================

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

# ======================
# BUTTON HANDLER
# ======================

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

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

async def send_evening_schedule(context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌙 Напоминание:\n"
        "Завтра занятия по расписанию.\n"
        "Подробности — утром 📚"
    )

    for chat_id in ALL_SUBJECT_CHATS:
        await context.bot.send_message(chat_id=chat_id, text=text)

# ======================
# MAIN
# ======================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    app.job_queue.run_daily(
        send_morning_schedule,
        time=datetime.time(hour=6, minute=0),
        days=(0, 1, 2, 3, 4),
    )

    app.job_queue.run_daily(
        send_evening_schedule,
        time=datetime.time(hour=20, minute=0),
        days=(0, 1, 2, 3, 4),
    )

    # планируем напоминания на сегодня при запуске
    schedule_today_reminders(app)

    # и каждый день в 07:00 пересобираем напоминания
    app.job_queue.run_daily(
        lambda ctx: schedule_today_reminders(app),
        time=datetime.time(hour=7, minute=0),
        days=(0, 1, 2, 3, 4),
    )

    print("Bot started successfully")
    app.run_polling()

if __name__ == "__main__":
    main()
