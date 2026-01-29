from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import logging

from core.config import ADMIN_IDS, ALL_SUBJECT_CHATS
from core.database import add_lesson

logger = logging.getLogger(__name__)

# Состояния диалога
DAY, PAIR, SUBJECT, TYPE, WEEKS, ROOM, TEACHER, CHAT, CONFIRM = range(9)


def is_admin(user_id: int) -> bool:
    """Проверка прав администратора"""
    return user_id in ADMIN_IDS


async def add_lesson_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления занятия"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("🔒 У вас нет прав администратора")
        return ConversationHandler.END
    
    # Очищаем данные
    context.user_data.clear()
    
    # Кнопки выбора дня
    keyboard = [
        [InlineKeyboardButton("Понедельник", callback_data="day_monday")],
        [InlineKeyboardButton("Вторник", callback_data="day_tuesday")],
        [InlineKeyboardButton("Среда", callback_data="day_wednesday")],
        [InlineKeyboardButton("Четверг", callback_data="day_thursday")],
        [InlineKeyboardButton("Пятница", callback_data="day_friday")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "➕ **Добавление занятия**\n\n"
        "Шаг 1/8: Выберите день недели:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return DAY


async def select_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор дня недели"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Добавление занятия отменено")
        return ConversationHandler.END
    
    day = query.data.replace("day_", "")
    context.user_data["day"] = day
    
    days_map = {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
    }
    
    await query.edit_message_text(
        f"✅ День: {days_map[day]}\n\n"
        "Шаг 2/8: Введите номер пары (1, 2 или 3):"
    )
    
    return PAIR


async def enter_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод номера пары"""
    text = update.message.text.strip()
    
    if text not in ["1", "2", "3"]:
        await update.message.reply_text(
            "⚠️ Пожалуйста, введите корректный номер пары: 1, 2 или 3"
        )
        return PAIR
    
    context.user_data["pair"] = int(text)
    
    await update.message.reply_text(
        f"✅ Пара: {text}\n\n"
        "Шаг 3/8: Введите название предмета:"
    )
    
    return SUBJECT


async def enter_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод названия предмета"""
    subject = update.message.text.strip()
    
    if len(subject) < 3:
        await update.message.reply_text(
            "⚠️ Название предмета слишком короткое. Попробуйте ещё раз:"
        )
        return SUBJECT
    
    context.user_data["subject"] = subject
    
    # Кнопки выбора типа
    keyboard = [
        [InlineKeyboardButton("📘 Лекция", callback_data="type_lecture")],
        [InlineKeyboardButton("📒 Семинар", callback_data="type_seminar")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Предмет: {subject}\n\n"
        "Шаг 4/8: Выберите тип занятия:",
        reply_markup=reply_markup
    )
    
    return TYPE


async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор типа занятия"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Добавление занятия отменено")
        return ConversationHandler.END
    
    lesson_type = query.data.replace("type_", "")
    context.user_data["type"] = lesson_type
    
    type_name = "Лекция" if lesson_type == "lecture" else "Семинар"
    
    await query.edit_message_text(
        f"✅ Тип: {type_name}\n\n"
        "Шаг 5/8: Введите диапазон недель (например: 4-8 или 10-15):"
    )
    
    return WEEKS


async def enter_weeks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод диапазона недель"""
    text = update.message.text.strip()
    
    # Парсим диапазон
    if "-" not in text:
        await update.message.reply_text(
            "⚠️ Неверный формат. Используйте формат: 4-8"
        )
        return WEEKS
    
    try:
        start, end = text.split("-")
        week_start = int(start.strip())
        week_end = int(end.strip())
        
        if week_start < 1 or week_end < week_start or week_end > 20:
            raise ValueError()
        
        context.user_data["week_start"] = week_start
        context.user_data["week_end"] = week_end
        
        await update.message.reply_text(
            f"✅ Недели: {week_start}-{week_end}\n\n"
            "Шаг 6/8: Введите номер аудитории (например: 2/214):"
        )
        
        return ROOM
        
    except ValueError:
        await update.message.reply_text(
            "⚠️ Неверный формат. Введите диапазон недель (например: 4-8):"
        )
        return WEEKS


async def enter_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод аудитории"""
    room = update.message.text.strip()
    
    if len(room) < 1:
        await update.message.reply_text(
            "⚠️ Введите номер аудитории:"
        )
        return ROOM
    
    context.user_data["room"] = room
    
    await update.message.reply_text(
        f"✅ Аудитория: {room}\n\n"
        "Шаг 7/8: Введите ФИО преподавателя:"
    )
    
    return TEACHER


async def enter_teacher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод преподавателя"""
    teacher = update.message.text.strip()
    
    if len(teacher) < 3:
        await update.message.reply_text(
            "⚠️ Введите ФИО преподавателя:"
        )
        return TEACHER
    
    context.user_data["teacher"] = teacher
    
    # Кнопки выбора чата
    keyboard = [
        [InlineKeyboardButton("Стратегический менеджмент", callback_data=f"chat_{ALL_SUBJECT_CHATS[0]}")],
        [InlineKeyboardButton("Качество и безопасность", callback_data=f"chat_{ALL_SUBJECT_CHATS[1]}")],
        [InlineKeyboardButton("Мировая экономика", callback_data=f"chat_{ALL_SUBJECT_CHATS[2]}")],
        [InlineKeyboardButton("Международный бизнес", callback_data=f"chat_{ALL_SUBJECT_CHATS[3]}")],
        [InlineKeyboardButton("Только расписание", callback_data=f"chat_{ALL_SUBJECT_CHATS[4]}")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Преподаватель: {teacher}\n\n"
        "Шаг 8/8: Выберите чат для уведомлений:",
        reply_markup=reply_markup
    )
    
    return CHAT


async def select_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор чата"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Добавление занятия отменено")
        return ConversationHandler.END
    
    chat_id = int(query.data.replace("chat_", ""))
    context.user_data["chat_id"] = chat_id
    
    # Показываем итоговую информацию
    data = context.user_data
    
    days_map = {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
    }
    
    type_name = "Лекция" if data["type"] == "lecture" else "Семинар"
    
    summary = (
        "📋 **Проверьте данные:**\n\n"
        f"📅 День: {days_map[data['day']]}\n"
        f"⏰ Пара: {data['pair']}\n"
        f"📘 Предмет: {data['subject']}\n"
        f"🎓 Тип: {type_name}\n"
        f"📆 Недели: {data['week_start']}-{data['week_end']}\n"
        f"🏫 Аудитория: {data['room']}\n"
        f"👩‍🏫 Преподаватель: {data['teacher']}\n\n"
        "Всё верно?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Сохранить", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Отмена", callback_data="confirm_no"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        summary,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    return CONFIRM


async def confirm_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение и сохранение"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_no":
        await query.edit_message_text("❌ Добавление занятия отменено")
        return ConversationHandler.END
    
    # Сохраняем в БД
    data = context.user_data
    
    try:
        lesson_id = add_lesson(
            day_of_week=data["day"],
            pair_number=data["pair"],
            subject=data["subject"],
            lesson_type=data["type"],
            week_start=data["week_start"],
            week_end=data["week_end"],
            room=data["room"],
            teacher=data["teacher"],
            chat_id=data["chat_id"]
        )
        
        await query.edit_message_text(
            f"✅ **Занятие успешно добавлено!**\n\n"
            f"ID: {lesson_id}\n"
            f"Предмет: {data['subject']}\n"
            f"Недели: {data['week_start']}-{data['week_end']}",
            parse_mode="Markdown"
        )
        
        logger.info(f"Admin {update.effective_user.id} added lesson ID {lesson_id}")
        
    except Exception as e:
        logger.error(f"Failed to add lesson: {e}")
        await query.edit_message_text(
            "❌ Ошибка при сохранении занятия. Попробуйте ещё раз."
        )
    
    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога"""
    await update.message.reply_text("❌ Операция отменена")
    return ConversationHandler.END


# Создаём ConversationHandler
add_lesson_conversation = ConversationHandler(
    entry_points=[CommandHandler("add_lesson", add_lesson_start)],
    states={
        DAY: [CallbackQueryHandler(select_day)],
        PAIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_pair)],
        SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_subject)],
        TYPE: [CallbackQueryHandler(select_type)],
        WEEKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_weeks)],
        ROOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_room)],
        TEACHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_teacher)],
        CHAT: [CallbackQueryHandler(select_chat)],
        CONFIRM: [CallbackQueryHandler(confirm_add)],
    },
    fallbacks=[CommandHandler("cancel", cancel_conversation)],
)
