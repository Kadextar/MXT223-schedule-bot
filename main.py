import os
import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ======================
# CONFIG
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

# ID предметных групп
CHAT_STRATEGY = -1003789929485
CHAT_QUALITY = -1003798438883
CHAT_ECONOMY = -1003814835903
CHAT_INTL_BUSINESS = -1002982024678

ALL_SUBJECT_CHATS = (
    CHAT_STRATEGY,
    CHAT_QUALITY,
    CHAT_ECONOMY,
    CHAT_INTL_BUSINESS,
)

# ======================
# KEYBOARD
# ======================

keyboard = ReplyKeyboardMarkup(
    [
        ["📅 Сегодня"],
        ["📘 Лекция", "📒 Семинар"],
    ],
    resize_keyboard=True,
)

# ======================
# COMMANDS
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n"
        "Я бот расписания группы МХТ-223.\n"
        "Выбери действие:",
        reply_markup=keyboard
    )

# ======================
# BUTTON HANDLER
# ======================

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📅 Сегодня":
        await update.message.reply_text(
            "📅 Расписание на сегодня:\n\n"
            "— Стратегический менеджмент\n"
            "— Качество и безопасность\n"
            "— Мировая экономика\n"
            "— Международный гостиничный бизнес\n\n"
            "(пока без умной логики)"
        )

    elif text == "📘 Лекция":
        await update.message.reply_text(
            "📘 Сегодня есть лекционные занятия.\n"
            "(детализация появится дальше)"
        )

    elif text == "📒 Семинар":
        await update.message.reply_text(
            "📒 Сегодня есть семинарские занятия.\n"
            "(детализация появится дальше)"
        )

# ======================
# AUTO MESSAGES
# ======================

async def send_morning_schedule(context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌅 Доброе утро!\n\n"
        "📅 Сегодня учебный день.\n"
        "Подробное расписание будет отправлено позже ⏰"
    )

    for chat_id in ALL_SUBJECT_CHATS:
        await context.bot.send_message(chat_id=chat_id, text=text)

async def send_evening_schedule(context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌙 Напоминание:\n"
        "Завтра занятия по расписанию.\n"
        "Подробности — утром 📚"
    )

    for chat_id in ALL_SUBJECT_CHATS:
        await context.bot.send_message(chat_id=chat_id, text=text)

# ======================
# MAIN
# ======================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    # jobs (ПН–ПТ)
    app.job_queue.run_daily(
        send_morning_schedule,
        time=datetime.time(hour=6, minute=0),
        days=(0, 1, 2, 3, 4),
    )

    app.job_queue.run_daily(
        send_evening_schedule,
        time=datetime.time(hour=20, minute=0),
        days=(0, 1, 2, 3, 4),
    )

    print("Bot started successfully")
    app.run_polling()

if __name__ == "__main__":
    main()
