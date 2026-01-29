"""Callback handlers for quick action buttons in /start command"""
from telegram import Update
from telegram.ext import ContextTypes

from core.handlers.user_commands import (
    today_schedule,
    tomorrow_schedule,
    next_lesson,
    week_schedule
)


async def quick_actions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quick action buttons from /start menu"""
    query = update.callback_query
    await query.answer()
    
    # Map callback data to handler functions
    handlers = {
        "quick_today": today_schedule,
        "quick_tomorrow": tomorrow_schedule,
        "quick_next": next_lesson,
        "quick_week": week_schedule
    }
    
    handler = handlers.get(query.data)
    if handler:
        # Call the appropriate handler
        await handler(update, context)
