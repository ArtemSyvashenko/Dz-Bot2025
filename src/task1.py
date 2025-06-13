from aiogram import Router, F
from aiogram.types import Message, CallbackQuery 

import random

router = Router()

panic_responses = [
    "01100100 01111001 01101110 01100001...",
    "Помилка! 0xA13F... ⚠️",
    ">>> System overload: розпізнавання команд зупинено.",
    "🤖 [BOT ERROR]: AI instability detected.",
    "Зачекайте... перепідключення до нейромережі...",
    "🧠 PANIC MODE ACTIVATED... ¯\\_(ツ)_/¯"
]

async def panic_command(message: Message):
    await message.answer(random.choice(panic_responses))

async def pansc_button(callback: CallbackQuery):
    await callback.message.answer(random.choice(panic_responses))
    await callback.answer()    