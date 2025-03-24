from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

import logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token="7518865505:AAEdCzkLa10pGA6N4uRyuy2CTDAQP0w-IOQ")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Шаги FSM
class Form(StatesGroup):
    doctor_name = State()
    patient_name = State()

# Кнопка
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton("✍ Подать извещение"))

# Старт
@dp.message_handler(commands=['start'], state='*')
@dp.message_handler(lambda message: message.text == "✍ Подать извещение", state='*')
async def start_form(message: types.Message, state: FSMContext):
    await Form.doctor_name.set()
    await message.answer("Введите ФИО врача:")

# Ввод врача
@dp.message_handler(state=Form.doctor_name)
async def get_doctor_name(message: types.Message, state: FSMContext):
    await state.update_data(doctor_name=message.text)
    await Form.patient_name.set()
    await message.answer("Введите ФИО пациента:")

# Ввод пациента
@dp.message_handler(state=Form.patient_name)
async def get_patient_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    doctor = data['doctor_name']
    patient = message.text

    # Здесь будет генерация файла (пока просто подтверждение)
    await message.answer(f"ФИО врача: {doctor}\nФИО пациента: {patient}\n\nИзвещение готово. Спасибо!")
    await state.finish()

# Если пользователь пишет что-то вне шагов
@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer("Нажмите кнопку '✍ Подать извещение', чтобы начать.", reply_markup=start_keyboard)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
