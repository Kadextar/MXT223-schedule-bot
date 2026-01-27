from telegram import ReplyKeyboardMarkup

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📅 Сегодня", "🌙 Завтра"],
        ["📊 Нагрузка недели"],
        ["📘 Лекция", "📒 Семинар"],
    ],
    resize_keyboard=True,
)
