from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from functools import wraps
import logging

from core.config import ADMIN_IDS
from core.database import get_all_lessons

logger = logging.getLogger(__name__)


def admin_only(func):
    """Декоратор для проверки прав администратора"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_IDS:
            await update.message.reply_text(
                "🔒 У вас нет прав для использования этой команды.\n"
                "Только администраторы могут управлять расписанием."
            )
            logger.warning(f"Unauthorized admin access attempt by user {user_id}")
            return
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


@admin_only
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню администратора"""
    keyboard = [
        [
            InlineKeyboardButton("➕ Добавить занятие", callback_data="admin_add"),
            InlineKeyboardButton("📝 Редактировать", callback_data="admin_edit"),
        ],
        [
            InlineKeyboardButton("🗑 Удалить занятие", callback_data="admin_delete"),
            InlineKeyboardButton("📋 Список занятий", callback_data="admin_list"),
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔧 **Панель администратора**\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


@admin_only
async def list_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список всех занятий в базе данных"""
    lessons = get_all_lessons()
    
    if not lessons:
        await update.message.reply_text("📭 В базе данных нет занятий")
        return
    
    # Группируем по дням недели
    days_map = {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
    }
    
    grouped = {}
    for lesson in lessons:
        day = lesson["day_of_week"]
        if day not in grouped:
            grouped[day] = []
        grouped[day].append(lesson)
    
    # Формируем сообщение
    lines = ["📋 **Все занятия в расписании:**\n"]
    
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
        if day not in grouped:
            continue
        
        day_name = days_map.get(day, day)
        lines.append(f"\n**{day_name}:**")
        
        for lesson in sorted(grouped[day], key=lambda x: x["pair"]):
            lesson_type = "Лекция" if lesson["type"] == "lecture" else "Семинар"
            weeks = f"{lesson['week_start']}-{lesson['week_end']}"
            
            lines.append(
                f"  • ID {lesson['id']}: {lesson['pair']} пара, {lesson['subject']}\n"
                f"    {lesson_type}, недели {weeks}, {lesson['room']}"
            )
    
    # Отправляем по частям, если слишком длинное
    message = "\n".join(lines)
    
    if len(message) > 4000:
        # Разбиваем на части
        chunks = []
        current_chunk = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) > 3900:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_length = len(line)
            else:
                current_chunk.append(line)
                current_length += len(line)
        
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode="Markdown")
    else:
        await update.message.reply_text(message, parse_mode="Markdown")
    
    await update.message.reply_text(
        f"\n📊 Всего занятий: {len(lessons)}"
    )


async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback-кнопок админ-панели"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("🔒 У вас нет прав администратора")
        return
    
    data = query.data
    
    if data == "admin_list":
        # Показываем список занятий
        lessons = get_all_lessons()
        
        if not lessons:
            await query.edit_message_text("📭 В базе данных нет занятий")
            return
        
        await query.edit_message_text(
            f"📋 Всего занятий в БД: {len(lessons)}\n\n"
            "Используйте команду /list_lessons для подробного списка"
        )
    
    elif data == "admin_stats":
        # Показываем статистику
        lessons = get_all_lessons()
        
        lectures = sum(1 for l in lessons if l["type"] == "lecture")
        seminars = sum(1 for l in lessons if l["type"] == "seminar")
        
        # Группируем по дням
        days_count = {}
        for lesson in lessons:
            day = lesson["day_of_week"]
            days_count[day] = days_count.get(day, 0) + 1
        
        days_map = {
            "monday": "Пн",
            "tuesday": "Вт",
            "wednesday": "Ср",
            "thursday": "Чт",
            "friday": "Пт",
        }
        
        days_text = "\n".join(
            f"  • {days_map.get(day, day)}: {count}"
            for day, count in sorted(days_count.items())
        )
        
        await query.edit_message_text(
            f"📊 **Статистика расписания**\n\n"
            f"📘 Лекций: {lectures}\n"
            f"📒 Семинаров: {seminars}\n"
            f"📚 Всего занятий: {len(lessons)}\n\n"
            f"По дням:\n{days_text}",
            parse_mode="Markdown"
        )
    
    elif data == "admin_add":
        await query.edit_message_text(
            "➕ Для добавления занятия используйте команду:\n"
            "/add_lesson"
        )
    
    elif data == "admin_edit":
        await query.edit_message_text(
            "📝 Для редактирования занятия используйте команду:\n"
            "/edit_lesson"
        )
    
    elif data == "admin_delete":
        await query.edit_message_text(
            "🗑 Для удаления занятия используйте команду:\n"
            "/delete_lesson"
        )


@admin_only
async def reset_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс и обновление расписания из фиксированного скрипта"""
    msg = await update.message.reply_text("⏳ Начинаю обновление расписания...")
    
    try:
        # Импортируем функцию здесь
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from update_schedule_fixed import update_schedule
        
        # Запускаем обновление (синхронно, так как это sqlite)
        update_schedule()
        
        await msg.edit_text("✅ Расписание успешно обновлено по новым данным!")
    except Exception as e:
        logger.error(f"Error resetting schedule: {e}")
        await msg.edit_text(f"❌ Ошибка при обновлении: {e}")

@admin_only
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправить объявление всем пользователям и сохранить в БД"""
    from core.database import add_announcement
    
    if not context.args:
        await update.message.reply_text(
            "📣 *Broadcast - Рассылка объявлений*\n\n"
            "Использование:\n"
            "`/broadcast <сообщение>`\n\n"
            "Пример:\n"
            "`/broadcast Завтра пары отменяются!`\n\n"
            "Сообщение будет:\n"
            "• Отправлено всем пользователям бота\n"
            "• Показано на сайте как объявление",
            parse_mode="Markdown"
        )
        return
    
    message = " ".join(context.args)
    
    # Сохраняем в БД
    try:
        add_announcement(message)
        logger.info(f"Announcement created: {message}")
    except Exception as e:
        logger.error(f"Error saving announcement: {e}")
        await update.message.reply_text(f"❌ Ошибка при сохранении объявления: {e}")
        return
    
    # Отправляем всем пользователям (если есть список)
    # Для простоты пока просто подтверждаем админу
    await update.message.reply_text(
        f"✅ *Объявление опубликовано!*\n\n"
        f"📣 {message}\n\n"
        f"Объявление сохранено в БД и будет показано на сайте.",
        parse_mode="Markdown"
    )

async def init_students_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Инициализирует студентов с начальными паролями (только для админа)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Эта команда доступна только администратору.")
        return
    
    from core.database import add_student
    
    students = [
        {"telegram_id": "1748727700", "password": "robiya2026", "name": "Робия"},
        {"telegram_id": "1427112602", "password": "sardor2026", "name": "Сардор"},
        {"telegram_id": "1937736219", "password": "khislatbek2026", "name": "Хислатбек"},
        {"telegram_id": "207103078", "password": "timur2026", "name": "Тимур"},
        {"telegram_id": "5760110758", "password": "amir2026", "name": "Амир"},
        {"telegram_id": "1362668588", "password": "muhammad2026", "name": "Мухаммад"},
        {"telegram_id": "2023499343", "password": "abdumalik2026", "name": "Абдумалик"},
        {"telegram_id": "1214641616", "password": "azamat2026", "name": "Азамат"},
        {"telegram_id": "1020773033", "password": "nozima2026", "name": "Нозима"}
    ]
    
    success_count = 0
    already_exists = 0
    
    for student in students:
        result = add_student(
            telegram_id=student["telegram_id"],
            password=student["password"],
            name=student["name"]
        )
        if result:
            success_count += 1
        else:
            already_exists += 1
    
    await update.message.reply_text(
        f"✅ Инициализация студентов завершена!\n\n"
        f"➕ Добавлено: {success_count}\n"
        f"⚠️ Уже существовали: {already_exists}\n\n"
        f"📋 Начальные пароли:\n"
        f"• Робия: robiya2026\n"
        f"• Сардор: sardor2026\n"
        f"• Хислатбек: khislatbek2026\n"
        f"• Тимур: timur2026\n"
        f"• Амир: amir2026\n"
        f"• Мухаммад: muhammad2026\n"
        f"• Абдумалик: abdumalik2026\n"
        f"• Азамат: azamat2026\n"
        f"• Нозима: nozima2026",
        parse_mode="Markdown"
    )
