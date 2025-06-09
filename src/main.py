import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
from config import TOKEN, SUBJECTS

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_subject_data(subject):
    path = os.path.join(DATA_DIR, f"{subject}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"main": None, "adds": [], "done": False, "chat_id": None}

def save_subject_data(subject, data):
    path = os.path.join(DATA_DIR, f"{subject}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 ДЗ", callback_data="menu_homework")
    builder.button(text="🔧 Адмін", callback_data="menu_admin")
    builder.adjust(2)
    await message.answer("Привіт! Обери дію:", reply_markup=builder.as_markup())

@dp.callback_query(lambda call: call.data == "menu_homework")
async def show_subjects(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for tag, name in SUBJECTS.items():
        builder.button(text=name, callback_data=f"user_subject:{tag}")
    builder.adjust(1)
    await call.message.edit_text("Оберіть предмет:", reply_markup=builder.as_markup())

@dp.callback_query(lambda call: call.data.startswith("user_subject:"))
async def show_homework(call: CallbackQuery):
    subject = call.data.split(":")[1]
    data = get_subject_data(subject)
    if not data or data.get("done"):
        await call.answer("Немає активного ДЗ або воно вже виконане.")
        return

    main_id = data.get("main")
    additions = data.get("adds", [])
    from_chat = data.get("chat_id", call.message.chat.id)

    if main_id:
        try:
            await bot.forward_message(call.message.chat.id, from_chat, main_id)
        except:
            await call.message.answer("❌ Основне ДЗ недоступне.")

    for msg_id in additions:
        try:
            await bot.forward_message(call.message.chat.id, from_chat, msg_id)
        except:
            continue

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Виконано", callback_data=f"mark_done:{subject}")
    builder.button(text="🔁 Зробити знову", callback_data=f"undo_done:{subject}")
    builder.adjust(2)
    await call.message.answer("Статус ДЗ:", reply_markup=builder.as_markup())

@dp.callback_query(lambda call: call.data.startswith("mark_done:"))
async def mark_done(call: types.CallbackQuery):
    subject = call.data.split(":")[1]
    data = get_subject_data(subject)
    data["done"] = True
    save_subject_data(subject, data)
    await call.answer("Позначено як виконане ✅")

@dp.callback_query(lambda call: call.data.startswith("undo_done:"))
async def undo_done(call: types.CallbackQuery):
    subject = call.data.split(":")[1]
    data = get_subject_data(subject)
    data["done"] = False
    save_subject_data(subject, data)
    await call.answer("Повернено як невиконане 🔁")

@dp.message()
async def handle_tags(message: types.Message):
    text = message.text or message.caption  # <- підтримка і тексту, і підпису
    if not text:
        return

    for word in text.split():
        if word.startswith("#"):
            tag = word[1:]
            is_add = tag.endswith("+")
            subject = tag.rstrip("+")

            if subject not in SUBJECTS:
                return

            # Перевірка чи є щось окрім хештега
            content = text.replace(word, "").strip()
            if not content and not message.photo and not message.document:
                await message.reply("⚠️ Повідомлення не містить ДЗ.")
                return

            data = get_subject_data(subject)

            if is_add:
                data.setdefault("adds", []).append(message.message_id)
            else:
                data["main"] = message.message_id
                data["adds"] = []
                data["done"] = False

            data["chat_id"] = message.chat.id
            save_subject_data(subject, data)
            await message.reply("✅ Збережено.")
            return



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

