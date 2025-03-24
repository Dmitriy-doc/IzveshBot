import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

# Вставьте свой токен бота
TOKEN = "7518865505:AAEdCzkLa10pGA6N4uRyuy2CTDAQP0w-IOQ"

# Логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер с использованием нового синтаксиса
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Обработчик команды /start и остальных сообщений
@dp.message()
async def handle_start(message: Message):
    if message.text == "/start":
        await message.answer("Привет! Я работаю на aiogram 3.19 ✅")
    else:
        await message.answer(f"Ты написал: {message.text}")

# Главная асинхронная функция запуска
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
