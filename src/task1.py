from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime
import asyncio

router = Router()

panic_responses = [
    "01100100 01111001 01101110 01100001...",
    "Помилка! 0xA13F... ⚠️",
    ">>> System overload: розпізнавання команд зупинено.",
    "🤖 [BOT ERROR]: AI instability detected.",
    "Зачекайте... перепідключення до нейромережі...",
    "🧠 PANIC MODE ACTIVATED... ¯\\_(ツ)_/¯"
]

# ✅ Generator — infinite panic response loop
def panic_generator():
    i = 0
    while True:
        yield panic_responses[i % len(panic_responses)]
        i += 1

# ✅ Timeout consumer — send panic messages for N seconds
async def iterate_with_timeout(callback_or_message, timeout_seconds=3, is_callback=False):
    gen = panic_generator()
    start = datetime.now()
    while (datetime.now() - start).total_seconds() < timeout_seconds:
        text = next(gen)
        if is_callback:
            await callback_or_message.message.answer(text)
        else:
            await callback_or_message.answer(text)
        await asyncio.sleep(0.5)  # simulate delay

# 🧨 Panic command
async def panic_command(message: Message):
    await iterate_with_timeout(message, timeout_seconds=3, is_callback=False)


async def panic_button(callback: CallbackQuery):
    await iterate_with_timeout(callback, timeout_seconds=3, is_callback=True)
    await callback.answer()
