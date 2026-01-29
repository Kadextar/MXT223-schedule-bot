from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import datetime
import logging

from core.database import get_lessons_by_day_and_week
from core.schedule_service import get_week_number, format_today_schedule, format_tomorrow_schedule
from core.config import PAIR_START_TIMES, SEMESTER_START_DATE
from core.time_utils import today_uz, UZ_TZ

logger = logging.getLogger(__name__)


async def today_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /today — расписание на сегодня"""
    today = today_uz()
    
    if today < SEMESTER_START_DATE:
        await update.message.reply_text(
            "📅 Учебный семестр начинается с 2 февраля.\n"
            "Пока занятий нет 😌"
        )
        return
    
    schedule_text = format_today_schedule()
    await update.message.reply_text(schedule_text)


async def tomorrow_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /tomorrow — расписание на завтра"""
    today = today_uz()
    
    if today < SEMESTER_START_DATE:
        await update.message.reply_text(
            "📅 Учебный семестр начинается с 2 февраля.\n"
            "Пока занятий нет 😌"
        )
        return
    
    schedule_text = format_tomorrow_schedule()
    await update.message.reply_text(schedule_text)


async def next_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /next — следующая пара"""
    today = today_uz()
    
    if today < SEMESTER_START_DATE:
        await update.message.reply_text(
            "📅 Учебный семестр начинается с 2 февраля.\n"
            "Пока занятий нет 😌"
        )
        return
    
    # Получаем расписание на сегодня
    week = get_week_number(today)
    weekday = today.strftime("%A").lower()
    lessons = get_lessons_by_day_and_week(weekday, week)
    
    if not lessons:
        await update.message.reply_text("🎉 Сегодня больше нет пар!")
        return
    
    # Находим следующую пару
    now = datetime.datetime.now(UZ_TZ)
    next_lesson_found = None
    
    for lesson in sorted(lessons, key=lambda x: x["pair"]):
        pair_time = PAIR_START_TIMES.get(lesson["pair"])
        if not pair_time:
            continue
        
        lesson_dt = UZ_TZ.localize(
            datetime.datetime.combine(today, pair_time)
        )
        
        if lesson_dt > now:
            next_lesson_found = lesson
            time_until = lesson_dt - now
            break
    
    if not next_lesson_found:
        await update.message.reply_text("🎉 Сегодня больше нет пар!")
        return
    
    # Форматируем сообщение
    pair = next_lesson_found["pair"]
    time = PAIR_START_TIMES[pair].strftime("%H:%M")
    lesson_type = "📘 Лекция" if next_lesson_found["type"] == "lecture" else "📒 Семинар"
    
    # Вычисляем время до начала
    hours = time_until.seconds // 3600
    minutes = (time_until.seconds % 3600) // 60
    
    time_str = ""
    if hours > 0:
        time_str = f"{hours} ч {minutes} мин"
    else:
        time_str = f"{minutes} мин"
    
    message = (
        "⏭ **Следующая пара:**\n\n"
        f"🕒 {pair} пара ({time})\n"
        f"📘 {next_lesson_found['subject']}\n"
        f"{lesson_type}\n"
        f"👩‍🏫 {next_lesson_found['teacher']}\n"
        f"🏫 {next_lesson_found['room']}\n\n"
        f"⏰ До начала: **{time_str}**"
    )
    
    await update.message.reply_text(message, parse_mode="Markdown")


async def week_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /week — расписание на всю неделю"""
    today = today_uz()
    
    if today < SEMESTER_START_DATE:
        await update.message.reply_text(
            "📅 Учебный семестр начинается с 2 февраля.\n"
            "Пока занятий нет 😌"
        )
        return
    
    week = get_week_number(today)
    
    # Дни недели
    days = {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
    }
    
    lines = [f"📅 **Расписание на {week} неделю семестра**\n"]
    
    total_lessons = 0
    
    for day_en, day_ru in days.items():
        lessons = get_lessons_by_day_and_week(day_en, week)
        
        if not lessons:
            lines.append(f"\n**{day_ru}:**\n  Занятий нет 🎉")
            continue
        
        lines.append(f"\n**{day_ru}:**")
        
        for lesson in sorted(lessons, key=lambda x: x["pair"]):
            pair = lesson["pair"]
            time = PAIR_START_TIMES.get(pair)
            time_str = time.strftime("%H:%M") if time else "—"
            lesson_type_emoji = "📘" if lesson["type"] == "lecture" else "📒"
            
            lines.append(
                f"  {lesson_type_emoji} {pair} пара ({time_str}) — {lesson['subject']}"
            )
            total_lessons += 1
    
    lines.append(f"\n📊 Всего пар на неделе: **{total_lessons}**")
    
    # Кнопки навигации
    keyboard = [
        [
            InlineKeyboardButton("⬅️ Пред. неделя", callback_data=f"week_{week-1}"),
            InlineKeyboardButton("След. неделя ➡️", callback_data=f"week_{week+1}"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "\n".join(lines)
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def week_navigation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик навигации по неделям"""
    query = update.callback_query
    await query.answer()
    
    # Получаем номер недели из callback_data
    week = int(query.data.replace("week_", ""))
    
    if week < 4 or week > 20:
        await query.answer("⚠️ Неделя вне диапазона семестра", show_alert=True)
        return
    
    # Дни недели
    days = {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
    }
    
    lines = [f"📅 **Расписание на {week} неделю семестра**\n"]
    
    total_lessons = 0
    
    for day_en, day_ru in days.items():
        lessons = get_lessons_by_day_and_week(day_en, week)
        
        if not lessons:
            lines.append(f"\n**{day_ru}:**\n  Занятий нет 🎉")
            continue
        
        lines.append(f"\n**{day_ru}:**")
        
        for lesson in sorted(lessons, key=lambda x: x["pair"]):
            pair = lesson["pair"]
            time = PAIR_START_TIMES.get(pair)
            time_str = time.strftime("%H:%M") if time else "—"
            lesson_type_emoji = "📘" if lesson["type"] == "lecture" else "📒"
            
            lines.append(
                f"  {lesson_type_emoji} {pair} пара ({time_str}) — {lesson['subject']}"
            )
            total_lessons += 1
    
    lines.append(f"\n📊 Всего пар на неделе: **{total_lessons}**")
    
    # Кнопки навигации
    keyboard = [
        [
            InlineKeyboardButton("⬅️ Пред. неделя", callback_data=f"week_{week-1}"),
            InlineKeyboardButton("След. неделя ➡️", callback_data=f"week_{week+1}"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "\n".join(lines)
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
