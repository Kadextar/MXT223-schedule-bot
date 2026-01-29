from telegram import Update
from telegram.ext import ContextTypes
import time
import datetime
from core.time_utils import UZ_TZ, today_uz

from core.analytics import analyze_week_load
from core.config import SEMESTER_START_DATE


LAST_STATUS_CALL = {}


from core.ui.keyboards import MAIN_KEYBOARD

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n"
        "Я бот расписания группы МХТ-223.\n\n"
        "📌 **Доступные команды:**\n"
        "/today — Расписание на сегодня\n"
        "/tomorrow — Расписание на завтра\n"
        "/week — Расписание на неделю\n"
        "/next — Следующая пара\n"
        "/load — Анализ нагрузки\n\n"
        "Или используйте кнопки ⬇️",
        reply_markup=MAIN_KEYBOARD,
        parse_mode="Markdown",
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    now = time.time()

    if chat_id in LAST_STATUS_CALL and now - LAST_STATUS_CALL[chat_id] < 5:
        await update.message.reply_text(
            "⏳ Подожди пару секунд перед следующим запросом"
        )
        return

    LAST_STATUS_CALL[chat_id] = now

    today = today_uz()
    now_uz = datetime.datetime.now(UZ_TZ).strftime("%H:%M:%S")

    await update.message.reply_text(
        f"📅 Сегодня: {today}\n"
        f"🕒 Время (UZ): {now_uz}\n"
        f"📚 Семестр начался: {'✅' if today >= SEMESTER_START_DATE else '❌'}\n"
        f"⏰ Активных задач: {len(context.application.job_queue.jobs())}"
    )


async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now_uz = datetime.datetime.now(UZ_TZ).strftime("%H:%M:%S")
    today = today_uz()

    await update.message.reply_text(
        f"📅 Сегодня: {today}\n"
        f"🕒 Время (UZ): {now_uz}\n"
        f"📚 Семестр начался: {'✅' if today >= SEMESTER_START_DATE else '❌'}\n"
        f"⏰ Активных задач: {len(context.application.job_queue.jobs())}"
    )

async def load(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    text = (
        f"📊 Нагрузка недели ({data['week']} неделя)\n\n"
        f"📘 Лекций: {data['lectures']}\n"
        f"📒 Семинаров: {data['seminars']}\n"
        f"⏰ Учебных часов: {data['total_hours']}\n\n"
        f"🔥 Самый загруженный день: {day_names.get(data['hardest_day'], '—')}\n"
        f"😌 Самый лёгкий день: {day_names.get(data['easiest_day'], '—')}\n\n"
        f"📅 По дням:\n{days_text}"
    )

    await update.message.reply_text(text)
