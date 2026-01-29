from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def exams_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show exams schedule"""
    from core.database import get_exams
    
    exams = get_exams()
    
    if not exams:
        await update.message.reply_text(
            "📚 Расписание экзаменов пока не опубликовано.\\n\\n"
            "🌐 Следите за обновлениями на сайте:\\n"
            "https://mxt223-web-production.up.railway.app/exams.html"
        )
        return
    
    # Format exams list
    text = "📝 **Расписание экзаменов**\\n\\n"
    
    for exam in exams:
        text += f"📅 **{exam['exam_date']}**\\n"
        text += f"📚 {exam['subject']}\\n"
        
        if exam.get('teacher'):
            text += f"👨‍🏫 {exam['teacher']}\\n"
        
        if exam.get('exam_time'):
            text += f"⏰ {exam['exam_time']}"
        
        if exam.get('room'):
            text += f" • 🏛️ {exam['room']}"
        
        if exam.get('exam_time') or exam.get('room'):
            text += "\\n"
        
        if exam.get('exam_type'):
            text += f"📝 {exam['exam_type']}\\n"
        
        if exam.get('notes'):
            text += f"💡 {exam['notes']}\\n"
        
        text += "\\n"
    
    text += "🌐 Подробнее на сайте:\\n"
    text += "https://mxt223-web-production.up.railway.app/exams.html"
    
    await update.message.reply_text(text, parse_mode="Markdown")
