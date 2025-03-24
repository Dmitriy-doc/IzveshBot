from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from docxtpl import DocxTemplate
from datetime import datetime
import os

# Вставь свой токен сюда
TOKEN = "7518865505:AAEdCzkLa10pGA6N4uRyuy2CTDAQP0w-IOQ"

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Кнопка запуска
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton("📝 Подать извещение"))

# Хранилище состояний
user_data = {}

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Здравствуйте! Я помогу сформировать экстренное извещение.\n\nНажмите кнопку ниже, чтобы начать:", reply_markup=start_keyboard)

@dp.message_handler(lambda message: message.text == "📝 Подать извещение")
async def start_report(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Введите ФИО врача:")
    user_data[message.from_user.id]["step"] = "fio"

@dp.message_handler()
async def handle_all_messages(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.answer("Нажмите кнопку '📝 Подать извещение', чтобы начать.")
        return

    step = user_data[user_id].get("step")

    if step == "fio":
        user_data[user_id]["doctor"] = message.text
        await message.answer("Введите ФИО пациента:")
        user_data[user_id]["step"] = "patient"

    elif step == "patient":
        user_data[user_id]["patient"] = message.text
        await message.answer("Введите диагноз:")
        user_data[user_id]["step"] = "diagnosis"

    elif step == "diagnosis":
        user_data[user_id]["diagnosis"] = message.text
        await message.answer("Введите лабораторные результаты:")
        user_data[user_id]["step"] = "lab"

    elif step == "lab":
        user_data[user_id]["lab"] = message.text

        # Формируем извещение
        doc = DocxTemplate("template.docx")

        context = {
            "doctor": user_data[user_id]["doctor"],
            "hospital": "ГБУЗ МО ДКЦ им. Л.М. Рошаля",
            "patient": user_data[user_id]["patient"],
            "diagnosis": user_data[user_id]["diagnosis"],
            "lab": user_data[user_id]["lab"],
            "date": datetime.today().strftime("%d.%m.%Y"),
        }

        output_file = f"notification_{user_id}.docx"
        doc.render(context)
        doc.save(output_file)

        with open(output_file, "rb") as f:
            await message.answer_document(f, caption="📄 Готовый документ")
        
        os.remove(output_file)
        user_data.pop(user_id, None)

        await message.answer("Извещение сформировано. Чтобы создать новое — нажмите кнопку ниже.", reply_markup=start_keyboard)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp)
