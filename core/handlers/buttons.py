from telegram import Update
from telegram.ext import ContextTypes

from core.schedule_service import (
    format_today_schedule,
    format_tomorrow_schedule,
)
from core.time_utils import today_uz
from core.config import SEMESTER_START_DATE


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if today_uz() < SEMESTER_START_DATE:
        await update.message.reply_text(
            "📅 Учебный семестр начинается с 2 февраля.\n"
            "Пока занятий нет 😌"
        )
        return

    if text == "📅 Сегодня":
        await update.message.reply_text(format_today_schedule())

    elif text == "🌙 Завтра":
        await update.message.reply_text(format_tomorrow_schedule())

    elif text == "📘 Лекция":
        await update.message.reply_text(
            "📘 Лекционные занятия будут отображаться здесь."
        )

    elif text == "📒 Семинар":
        await update.message.reply_text(
            "📒 Семинарские занятия будут отображаться здесь."
        )