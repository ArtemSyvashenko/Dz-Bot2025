import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery

from config import TOKEN, SUBJECTS
from task1 import panic_command, panic_button
#from task3 import async_memoize
from task8 import button_agent_mode, receive_prompt, AgentState, enter_ageent_mode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# === Збереження та зчитування ДЗ ===
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

# === Команди ===
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 ДЗ", callback_data="menu_homework")
    builder.button(text="📦 Всі ДЗ", callback_data="menu_all_hw")
    builder.button(text="🤖 AI Агент", callback_data="menu_ai")
    builder.button(text="📛 Паніка", callback_data="паніка")
    builder.adjust(2)
    await message.answer("Привіт! Обери дію:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data == "паніка")
async def handle_panic(callback: CallbackQuery):
    await panic_button(callback)

@dp.message(F.text == "паніка")
async def handle_panic_text(message: types.Message):
    await panic_command(message)

# === ДЗ за предметами ===
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

# === Обробка тегів у повідомленнях ===
@dp.message()
async def handle_tags(message: types.Message):
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
                data["main"] = message.message_id
                data["adds"] = []
                data["done"] = False
            data["chat_id"] = message.chat.id
            save_subject_data(subject, data)
            await message.reply("✅ Збережено.")
            return

# === Task 5: Показати всі ДЗ одразу ===
@dp.callback_query(lambda c: c.data == "menu_all_hw")
async def show_all_homework(callback: CallbackQuery):
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
        await callback.message.answer(f"📦 Показано {count} предмет(ів) із ДЗ.")
    await callback.answer()

# === Task 8: AI Агент ===
dp.callback_query.register(button_agent_mode, F.data == "menu_ai")
dp.message.register(receive_prompt, AgentState.waiting_for_prompt)
dp.message.register(enter_ageent_mode, F.text == "/ai")

# === Запуск ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

