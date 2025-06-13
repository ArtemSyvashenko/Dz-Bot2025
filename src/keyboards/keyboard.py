from aiogram.types import ReplyKeybpardMarkup, Keyboardbutton

main_menu = ReplyKeybpardMarkup(
    keyboard=[
        [Keyboardbutton(text="📚 ДЗ")], Keyboardbutton(text="⚙️ Налаштування")
        [Keyboardbutton(text="🤖 AI агент")]
        [KeyboardButton(text="🧠 Паніка")]
    ],
    resize_keyboard=True

)