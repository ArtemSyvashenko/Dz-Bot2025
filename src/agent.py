from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Стан для очікування запиту
class AgentState(StatesGroup):
    waiting_for_prompt = State()

# Обробка команди /ai — вхід у режим агента
async def enter_ageent_mode(message: types.Message, state: FSMContext):
    await state.set_state(AgentState.waiting_for_prompt)
    await message.answer("🧠 Введи запит, і я його залогую.")

# Прийом повідомлення і логування
async def receive_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    prompt = message.text.strip()

    with open(f"logs/agent_{user_id}.txt", "a", encoding="utf-8") as f:
        f.write(prompt + "\n")

    await state.clear()
    await message.answer("✅ Запит збережено в лог.")

# Кнопка (опціональна, для меню)
async def button_agent_mode(callback: types.CallbackQuery):
    await callback.message.answer("🧠 Введи /ai щоб перейти в режим агента.")
    await callback.answer()
