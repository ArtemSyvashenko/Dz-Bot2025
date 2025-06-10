from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext 
import json
from datetime import datetime

router = Router()

class AgentState(StatesGroup):
    waiting_for_prompt = State()
    
async def enter_ageent_mode(message: Message, state: FSMContext):
    await message.answer("🧠 Надішли мені запит, який я маю передати AI-агенту.")
    await state.set_state(AgentState.waiting_for_prompt)

async def button_agent_mode(callback: CallbackQuery, state:FSMContext):
    await callback.message.answer("🧠 Надішли мені запит, який я маю передати AI-агенту.")
    await state.set_state(AgentState.waiting_for_prompt)
    await callback.answer()

async def receive_prompt(message: Message, state: FSMContext):
    user_prompt = message.text
     
    await message.answer(f"🔄 Обробляю твій запит...\n(Зараз фейковий AI 😅)")
    
    try:
       with open("ai_prompts_log.json", "r", encoding="utf-8") as f:
         prompt = json.load(f)
    except FileExistsError:
        prompt = []

    prompt.append({
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "prompt": user_prompt,
        "timestamp": datetime.now().isoformat()
    })    

    with open("ai_prompts_log.json", "w", encoding="utf-8") as f:
        json.dump(prompt, f, ensure_ascii=False, indent=2)

    await message.answer("✅ Запит збережено. (У майбутньому буде AI-відповідь)")            
    await state.clear()