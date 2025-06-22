from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime
import asyncio
import time

router = Router()

# Антиспам
last_click_time = {}
COOLDOWN = 30  # сек

# Репліки при натисканні
panic_responses = [
    "01100100 01111001 01101110 01100001...",
    "Помилка! 0xA13F... ⚠️",
    ">>> System overload: розпізнавання команд зупинено.",
    "🤖 [BOT ERROR]: AI instability detected.",
    "Зачекайте... перепідключення до нейромережі...",
    "🧠 PANIC MODE ACTIVATED... ¯\\_(ツ)_/¯"
]

# Генератор відповідей
def panic_generator():
    i = 0
    while True:
        yield panic_responses[i % len(panic_responses)]
        i += 1

# Ітерація з текстом
async def iterate_with_timeout(target, timeout_seconds=3, is_callback=False):
    gen = panic_generator()
    start = datetime.now()
    while (datetime.now() - start).total_seconds() < timeout_seconds:
        text = next(gen)
        if is_callback:
            await target.message.answer(text)
        else:
            await target.answer(text)
        await asyncio.sleep(0.5)

# Перевірка кулдауна для зовнішнього використання
def is_user_on_cooldown(user_id: int):
    now = time.time()
    if user_id in last_click_time and now - last_click_time[user_id] < COOLDOWN:
        return True, int(COOLDOWN - (now - last_click_time[user_id]))
    return False, 0

# Команда /паніка
async def panic_command(message: Message):
    user_id = message.from_user.id
    last_click_time[user_id] = time.time()
    await iterate_with_timeout(message, timeout_seconds=3, is_callback=False)

# Кнопка паніки
async def panic_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    now = time.time()

    if user_id in last_click_time and now - last_click_time[user_id] < COOLDOWN:
        remaining = int(COOLDOWN - (now - last_click_time[user_id]))
        await callback.answer(f"⏳ Зачекай ще {remaining} сек.", show_alert=True)
        return

    last_click_time[user_id] = now
    await iterate_with_timeout(callback, timeout_seconds=3, is_callback=True)
    await callback.answer()
