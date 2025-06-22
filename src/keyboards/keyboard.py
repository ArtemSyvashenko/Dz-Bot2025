from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Паніка"),
            KeyboardButton(text="AI Асистент")
        ],
        [
            KeyboardButton(text="ДЗ"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Оберіть дію:"
)
