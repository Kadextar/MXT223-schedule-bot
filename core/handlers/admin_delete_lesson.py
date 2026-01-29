from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
)
import logging

from core.config import ADMIN_IDS
from core.database import get_all_lessons, delete_lesson

logger = logging.getLogger(__name__)

# Состояния диалога
SELECT_LESSON, CONFIRM = range(2)


def is_admin(user_id: int) -> bool:
    """Проверка прав администратора"""
    return user_id in ADMIN_IDS


async def delete_lesson_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало удаления занятия"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("🔒 У вас нет прав администратора")
        return ConversationHandler.END
    
    lessons = get_all_lessons()
    
    if not lessons:
        await update.message.reply_text("📭 В базе данных нет занятий")
        return ConversationHandler.END
    
    # Группируем по дням для удобства
    days_map = {
        "monday": "Пн",
        "tuesday": "Вт",
        "wednesday": "Ср",
        "thursday": "Чт",
        "friday": "Пт",
    }
    
    # Создаём кнопки (максимум 20 занятий на страницу)
    keyboard = []
    
    for lesson in lessons[:20]:  # Ограничиваем для удобства
        day = days_map.get(lesson["day_of_week"], lesson["day_of_week"])
        type_emoji = "📘" if lesson["type"] == "lecture" else "📒"
        
        button_text = (
            f"{day} | {lesson['pair']}п | {type_emoji} {lesson['subject'][:25]}"
        )
        
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"del_{lesson['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "🗑 **Удаление занятия**\n\n"
        "Выберите занятие для удаления:"
    )
    
    if len(lessons) > 20:
        message += f"\n\n⚠️ Показаны первые 20 из {len(lessons)} занятий"
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return SELECT_LESSON


async def select_lesson_to_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор занятия для удаления"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Удаление отменено")
        return ConversationHandler.END
    
    lesson_id = int(query.data.replace("del_", ""))
    
    # Получаем информацию о занятии
    lessons = get_all_lessons()
    lesson = next((l for l in lessons if l["id"] == lesson_id), None)
    
    if not lesson:
        await query.edit_message_text("❌ Занятие не найдено")
        return ConversationHandler.END
    
    context.user_data["lesson_id"] = lesson_id
    context.user_data["lesson"] = lesson
    
    days_map = {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
    }
    
    type_name = "Лекция" if lesson["type"] == "lecture" else "Семинар"
    
    summary = (
        "⚠️ **Подтвердите удаление:**\n\n"
        f"📅 День: {days_map[lesson['day_of_week']]}\n"
        f"⏰ Пара: {lesson['pair']}\n"
        f"📘 Предмет: {lesson['subject']}\n"
        f"🎓 Тип: {type_name}\n"
        f"📆 Недели: {lesson['week_start']}-{lesson['week_end']}\n"
        f"🏫 Аудитория: {lesson['room']}\n"
        f"👩‍🏫 Преподаватель: {lesson['teacher']}\n\n"
        "Удалить это занятие?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, удалить", callback_data="confirm_delete"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_delete"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        summary,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return CONFIRM


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение удаления"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_delete":
        await query.edit_message_text("❌ Удаление отменено")
        return ConversationHandler.END
    
    lesson_id = context.user_data.get("lesson_id")
    lesson = context.user_data.get("lesson")
    
    try:
        success = delete_lesson(lesson_id)
        
        if success:
            await query.edit_message_text(
                f"✅ **Занятие удалено!**\n\n"
                f"Предмет: {lesson['subject']}\n"
                f"ID: {lesson_id}",
                parse_mode="Markdown"
            )
            
            logger.info(f"Admin {update.effective_user.id} deleted lesson ID {lesson_id}")
        else:
            await query.edit_message_text("❌ Не удалось удалить занятие")
        
    except Exception as e:
        logger.error(f"Failed to delete lesson: {e}")
        await query.edit_message_text("❌ Ошибка при удалении занятия")
    
    return ConversationHandler.END


async def cancel_delete_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога"""
    await update.message.reply_text("❌ Операция отменена")
    return ConversationHandler.END


# Создаём ConversationHandler
delete_lesson_conversation = ConversationHandler(
    entry_points=[CommandHandler("delete_lesson", delete_lesson_start)],
    states={
        SELECT_LESSON: [CallbackQueryHandler(select_lesson_to_delete)],
        CONFIRM: [CallbackQueryHandler(confirm_delete)],
    },
    fallbacks=[CommandHandler("cancel", cancel_delete_conversation)],
)
