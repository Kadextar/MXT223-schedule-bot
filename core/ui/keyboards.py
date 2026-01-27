from telegram import ReplyKeyboardMarkup

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📅 Сегодня", "🌙 Завтра"],
        ["📊 Нагрузка недели"],
        ["📊 Статус"],
    ],
    resize_keyboard=True
)