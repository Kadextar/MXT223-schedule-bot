from telegram import ReplyKeyboardMarkup

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📅 Сегодня", "🌙 Завтра"],
        ["⏭ Следующая пара"],
        ["🧠 Статус дня"],
    ],
    resize_keyboard=True,
)
