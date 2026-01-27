from telegram import Update
from telegram.ext import ContextTypes
import time

from core.time_utils import today_uz
from core.config import SEMESTER_START_DATE

LAST_STATUS_CALL = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n"
        "Я бот расписания группы МХТ-223.\n\n"
        "Доступные команды:\n"
        "📅 Сегодня\n"
        "🌙 Завтра\n"
        "📊 /status\n"
        "⚙️ /enable /disable"
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
        f"📚 Семестр начался: {'✅' if today >= SEMESTER_START_DATE else '❌'}\n"
        f"⏰ Активных задач: {len(context.application.job_queue.jobs())}"
    )


async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Бот работает\n"
        f"🕒 UTC: {today_uz()}"
    )