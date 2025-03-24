from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from docx import Document
from datetime import datetime
import os

API_TOKEN = os.getenv("7518865505:AAEdCzkLa10pGA6N4uRyuy2CTDAQP0w-IOQ")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Шаги для FSM
class Form(StatesGroup):
    doctor_name = State()
    patient_name = State()
    diagnosis = State()
    lab_results = State()

# Кнопка запуска
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton("\ud83d\udcdc Подать извещение"))

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Нажмите кнопку '📝 Подать извещение', чтобы начать.", reply_markup=start_keyboard)

@dp.message_handler(lambda message: message.text == "\ud83d\udcdc Подать извещение")
async def start_form(message: types.Message):
    await Form.doctor_name.set()
    await message.answer("Введите ФИО врача:")

@dp.message_handler(state=Form.doctor_name)
async def process_doctor(message: types.Message, state: FSMContext):
    await state.update_data(doctor_name=message.text)
    await Form.next()
    await message.answer("Введите ФИО пациента:")

@dp.message_handler(state=Form.patient_name)
async def process_patient(message: types.Message, state: FSMContext):
    await state.update_data(patient_name=message.text)
    await Form.next()
    await message.answer("Введите диагноз:")

@dp.message_handler(state=Form.diagnosis)
async def process_diagnosis(message: types.Message, state: FSMContext):
    await state.update_data(diagnosis=message.text)
    await Form.next()
    await message.answer("Введите лабораторные результаты:")

@dp.message_handler(state=Form.lab_results)
async def process_lab(message: types.Message, state: FSMContext):
    await state.update_data(lab_results=message.text)
    data = await state.get_data()

    # Создание документа
    doc = Document()
    doc.add_heading("Экстренное извещение", level=1)
    doc.add_paragraph(f"ФИО врача: {data['doctor_name']}")
    doc.add_paragraph(f"ФИО пациента: {data['patient_name']}")
    doc.add_paragraph(f"Диагноз: {data['diagnosis']}")
    doc.add_paragraph(f"Лабораторные данные: {data['lab_results']}")
    filename = f"izvesh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc.save(filename)

    with open(filename, "rb") as file:
        await bot.send_document(chat_id=message.chat.id, document=file)

    os.remove(filename)
    await message.answer("Файл сформирован. Если нужно отправить ещё одно извещение — нажмите '📝 Подать извещение'.", reply_markup=start_keyboard)
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
