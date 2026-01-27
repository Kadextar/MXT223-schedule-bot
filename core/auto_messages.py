import logging
from telegram.ext import ContextTypes

from core.time_utils import today_uz
from core.config import SEMESTER_START_DATE, ALL_SUBJECT_CHATS
from core.schedule_service import format_tomorrow_schedule
from core.storage import load_json, save_json, LAST_MESSAGES_FILE

logger = logging.getLogger(__name__)

LAST_MESSAGES = load_json(LAST_MESSAGES_FILE)


async def send_morning_schedule(context: ContextTypes.DEFAULT_TYPE):
    if today_uz() < SEMESTER_START_DATE:
        return

    text = (
        "🌅 Доброе утро!\n\n"
        "📅 Сегодня учебный день.\n"
        "Подробное расписание будет отправлено позже ⏰"
    )

    for chat_id in ALL_SUBJECT_CHATS:
        # ✅ удаляем прошлое утреннее сообщение (если было)
        old_id = LAST_MESSAGES.get(chat_id)
        if old_id:
            try:
                await context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=old_id
                )
            except Exception:
                pass  # сообщение могло быть удалено вручную

        # ✅ отправляем новое
        msg = await context.bot.send_message(chat_id=chat_id, text=text)
        LAST_MESSAGES[chat_id] = msg.message_id

    save_json(LAST_MESSAGES_FILE, LAST_MESSAGES)


async def send_evening_schedule(context: ContextTypes.DEFAULT_TYPE):
    if today_uz() < SEMESTER_START_DATE:
        return

    text = format_tomorrow_schedule()

    for chat_id in ALL_SUBJECT_CHATS:
        await context.bot.send_message(chat_id=chat_id, text=text)
    
