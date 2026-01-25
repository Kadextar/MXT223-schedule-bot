import os
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, filters
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # добавим позже

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

# ---------- КНОПКИ ----------
keyboard = ReplyKeyboardMarkup(
    [
        ["📅 Сегодня", "📆 Завтра"],
        ["📚 Неделя"]
    ],
    resize_keyboard=True
)

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот расписания группы МХТ-223 👋\nВыбери действие:",
        reply_markup=keyboard
    )

# ---------- ОБРАБОТКА КНОПОК ----------
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📅 Сегодня":
        await update.message.reply_text("📅 Расписание на сегодня:\n(пока заглушка)")
    elif text == "📆 Завтра":
        await update.message.reply_text("📆 Расписание на завтра:\n(пока заглушка)")
    elif text == "📚 Неделя":
        await update.message.reply_text("📚 Расписание на неделю:\n(пока заглушка)")

# ---------- АВТО-ОТПРАВКА ----------
async def send_daily_schedule(context: ContextTypes.DEFAULT_TYPE):
    if not GROUP_CHAT_ID:
        return

    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text="⏰ Доброе утро!\nВот расписание на сегодня 📅\n(пока заглушка)"
    )

# ---------- MAIN ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CommandHandler("today", handle_buttons))
    app.add_handler(CommandHandler("tomorrow", handle_buttons))
    app.add_handler(CommandHandler("week", handle_buttons))

    app.add_handler(
        CommandHandler("buttons", start)
    )
    app.add_handler(
        telegram.ext.MessageHandler(
            telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND,
            handle_buttons
        )
    )

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_daily_schedule,
        trigger="cron",
        hour=7,
        minute=30,
        args=[app.bot],
    )
    scheduler.start()

    app.run_polling()

if __name__ == "__main__":
    main()
