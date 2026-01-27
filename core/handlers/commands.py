from telegram import Update
from telegram.ext import ContextTypes
import time
import datetime
from core.time_utils import UZ_TZ, today_uz

from core.time_utils import today_uz
from core.config import SEMESTER_START_DATE
from core.ui.keyboards import MAIN_KEYBOARD

LAST_STATUS_CALL = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n"
        "Я бот расписания группы МХТ-223.\n\n"
        "Выбери действие ⬇️",
        reply_markup=MAIN_KEYBOARD,
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    now = time.time()

    # защита от спама
    if chat_id in LAST_STATUS_CALL and now - LAST_STATUS_CALL[chat_id] < 5:
        return
    LAST_STATUS_CALL[chat_id] = now

    today = today_uz()

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
