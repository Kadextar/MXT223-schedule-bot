from telegram import Update
from telegram.ext import ContextTypes
import logging

from core.handlers.admin_handlers import admin_only

logger = logging.getLogger(__name__)

@admin_only
async def init_teachers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Инициализирует преподавателей в базе данных (только для админа)"""
    from core.database import add_or_update_teacher
    
    teachers = [
        {"name": "Роман", "subject": "Стратегический менеджмент"},
        {"name": "Свидлова", "subject": "Управление качеством"},
        {"name": "Жасулан", "subject": "Экономика"},
        {"name": "Аймир", "subject": "Международный бизнес"}
    ]
    
    success_count = 0
    
    for teacher in teachers:
        try:
            add_or_update_teacher(name=teacher["name"], subject=teacher["subject"])
            success_count += 1
        except Exception as e:
            logger.error(f"Error adding teacher {teacher['name']}: {e}")
    
    await update.message.reply_text(
        f"✅ Инициализация преподавателей завершена!\\n\\n"
        f"➕ Добавлено/обновлено: {success_count}\\n\\n"
        f"📋 Преподаватели:\\n"
        f"• Роман (Стратегический менеджмент)\\n"
        f"• Свидлова (Управление качеством)\\n"
        f"• Жасулан (Экономика)\\n"
        f"• Аймир (Международный бизнес)",
        parse_mode="Markdown"
    )
