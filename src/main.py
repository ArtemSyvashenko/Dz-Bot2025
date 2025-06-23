import json
import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from config import SUBJECTS 
from config import TOKEN
from agent import button_agent_mode, receive_prompt, enter_ageent_mode, AgentState
from task1 import panic_button

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

click_counter = {}  # user_id: count

class EventEmitter:
    def __init__(self):
        self.listeners = []

    def subscribe(self, listener):
        self.listeners.append(listener)

    def emit(self, data):
        for fn in self.listeners:
            fn(data)

def panic_handler(data):
    print("⚠️ Паніка! Користувач натиснув 'ДЗ' 5 разів!", data)

panic_events = EventEmitter()
panic_events.subscribe(panic_handler)

def get_subject_data(subject):
    path = os.path.join(DATA_DIR, f"{subject}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_subject_data(subject, data):
    path = os.path.join(DATA_DIR, f"{subject}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@dp.message(F.text.lower() == "/start")
async def start_handler(msg: types.Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📚 ДЗ", callback_data="menu_homework")
    keyboard.button(text="🧠 AI-агент", callback_data="menu_ai")
    keyboard.button(text="🔥 Популярне ДЗ", callback_data="menu_popular_hw")
    keyboard.button(text="📌 Невиконане ДЗ", callback_data="menu_unfinished_hw")
    keyboard.button(text="😱 Паніка", callback_data="menu_panic")
    await msg.answer("Привіт! Обери дію:", reply_markup=keyboard.as_markup())

@dp.callback_query(lambda c: c.data == "menu_panic")
async def call_panic(callback: CallbackQuery):
    await panic_button(callback)

@dp.callback_query(lambda call: call.data == "menu_homework")
async def show_subjects(call: types.CallbackQuery):
    user_id = call.from_user.id
    click_counter[user_id] = click_counter.get(user_id, 0) + 1

    if click_counter[user_id] == 5:
        panic_events.emit({"user_id": user_id, "chat_id": call.message.chat.id})

    builder = InlineKeyboardBuilder()
    for tag, name in SUBJECTS.items():
        builder.button(text=name, callback_data=f"user_subject:{tag}")
    builder.adjust(1)
    await call.message.edit_text("Оберіть предмет:", reply_markup=builder.as_markup())

@dp.callback_query(lambda call: call.data.startswith("user_subject:"))
async def show_homework(call: CallbackQuery):
    subject = call.data.split(":")[1]
    click_counter[subject] = click_counter.get(subject, 0) + 1
    data = get_subject_data(subject)
    if not data or data.get("done"):
        await call.answer("Немає активного ДЗ або воно вже виконане.")
        return

    from_chat = data.get("chat_id", call.message.chat.id)
    if data.get("main"):
        try:
            await bot.forward_message(call.message.chat.id, from_chat, data["main"])
        except:
            await call.message.answer("❌ Основне ДЗ недоступне.")

    for msg_id in data.get("adds", []):
        try:
            await bot.forward_message(call.message.chat.id, from_chat, msg_id)
        except:
            continue

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Виконано", callback_data=f"mark_done:{subject}")
    builder.button(text="🔁 Зробити знову", callback_data=f"undo_done:{subject}")
    builder.adjust(2)
    await call.message.answer("Статус ДЗ:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("mark_done:"))
async def mark_done(callback: CallbackQuery):
    subject = callback.data.split(":")[1]
    data = get_subject_data(subject)
    data["done"] = True
    save_subject_data(subject, data)
    await callback.message.answer("✅ Позначено як виконане.")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("undo_done:"))
async def undo_done(callback: CallbackQuery):
    subject = callback.data.split(":")[1]
    data = get_subject_data(subject)
    data["done"] = False
    save_subject_data(subject, data)
    await callback.message.answer("↩️ Позначено як невиконане.")
    await callback.answer()

@dp.message()
async def global_check(message: types.Message):
    text = message.text or message.caption
    if not text:
        return

    for word in text.split():
        if word.startswith("#"):
            tag = word[1:]
            is_add = tag.endswith("+")
            subject = tag.rstrip("+")

            if subject not in SUBJECTS:
                return

            content = text.replace(word, "").strip()
            if not content and not message.photo and not message.document:
                await message.reply("⚠️ Повідомлення не містить ДЗ.")
                return

            data = get_subject_data(subject)

            if is_add:
                data.setdefault("adds", []).append(message.message_id)
            else:
                if data.get("main"):
                    data.setdefault("history", []).append({
                        "main": data["main"],
                        "adds": data.get("adds", []),
                        "done": data.get("done", False)
                    })
                data["main"] = message.message_id
                data["adds"] = []
                data["done"] = False

            data["chat_id"] = message.chat.id
            save_subject_data(subject, data)
            await message.reply("✅ Збережено.")
            return

async def async_filter(items, predicate):
    result = []
    for item in items:
        if await predicate(item):
            result.append(item)
    return result

@dp.callback_query(lambda c: c.data == "menu_popular")
async def show_popular_subjects(callback: CallbackQuery):
    sorted_subjects = sorted(click_counter.items(), key=lambda x: x[1], reverse=True)[:3]
    
    for subject_tag, _ in sorted_subjects:
        data = get_subject_data(subject_tag)
        chat_id = data.get("chat_id")
        main = data.get("main")
        
        if main and chat_id:
            try:
                await bot.forward_message(callback.message.chat.id, chat_id, main)
                for msg_id in data.get("adds", []):
                    await bot.forward_message(callback.message.chat.id, chat_id, msg_id)
            except:
                continue

    await callback.message.answer("🔝 Це найпопулярніші предмети!")
    await callback.answer()


@dp.callback_query(lambda c: c.data == "menu_unfinished_hw")
async def show_unfinished_homework(callback: CallbackQuery):
    count = 0
    for subject in SUBJECTS:
        data = get_subject_data(subject)
        if data.get("done"):
            continue
        main = data.get("main")
        chat_id = data.get("chat_id")
        if main and chat_id:
            try:
                await bot.forward_message(callback.message.chat.id, chat_id, main)
                for add in data.get("adds", []):
                    await bot.forward_message(callback.message.chat.id, chat_id, add)
                count += 1
            except:
                continue

    if count == 0:
        await callback.message.answer("😴 Немає невиконаних ДЗ.")
    else:
        await callback.message.answer(f"📦 Показано {count} невиконаних предмет(ів).")
    await callback.answer()

dp.callback_query.register(button_agent_mode, F.data == "menu_ai")
dp.message.register(receive_prompt, AgentState.waiting_for_prompt)
dp.message.register(enter_ageent_mode, F.text == "/ai")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

