import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from docxtpl import DocxTemplate

# Загрузка токена бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не указан токен бота. Установите переменную окружения BOT_TOKEN.")

# Инициализация бота и диспетчера с указанием режима парсинга HTML (актуально для aiogram 3.x)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Определение состояний (FSM)
class Form(StatesGroup):
    fio = State()
    sex = State()
    birth = State()
    address = State()
    phone = State()
    work = State()
    disease_date = State()
    consult_date = State()
    diagnosis_date = State()
    last_visit_date = State()
    diagnosis = State()
    lab_results = State()
    additional_info = State()
    doctor_name = State()
    sender = State()

# Обработчик команды /start – запускает сценарий заполнения формы
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # Устанавливаем первое состояние и запрашиваем ФИО пациента
    await state.set_state(Form.fio)
    await message.answer(
        "Привет! Я помогу заполнить экстренное извещение (форма №058-у).\n\n"
        "Начнем. Введите ФИО пациента (полностью):",
        reply_markup=ReplyKeyboardRemove()
    )

# Обработчик состояния Form.fio (ФИО пациента)
@dp.message(Form.fio)
async def process_fio(message: Message, state: FSMContext):
    fio = message.text.strip()
    await state.update_data(fio=fio)
    # Переходим к следующему вопросу – пол пациента
    await state.set_state(Form.sex)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Пол пациента:", reply_markup=keyboard)

# Обработчик состояния Form.sex (пол)
@dp.message(Form.sex)
async def process_sex(message: Message, state: FSMContext):
    sex = message.text.strip()
    await state.update_data(sex=sex)
    await state.set_state(Form.birth)
    await message.answer("Дата рождения пациента (ДД.MM.ГГГГ):", reply_markup=ReplyKeyboardRemove())

# Обработчик состояния Form.birth (дата рождения)
@dp.message(Form.birth)
async def process_birth(message: Message, state: FSMContext):
    birth = message.text.strip()
    await state.update_data(birth=birth)
    await state.set_state(Form.address)
    await message.answer("Адрес пациента (место жительства):")

# Обработчик состояния Form.address (адрес)
@dp.message(Form.address)
async def process_address(message: Message, state: FSMContext):
    address = message.text.strip()
    await state.update_data(address=address)
    await state.set_state(Form.phone)
    await message.answer("Контактный телефон пациента:")

# Обработчик состояния Form.phone (телефон)
@dp.message(Form.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(phone=phone)
    await state.set_state(Form.work)
    await message.answer("Место работы или учебы пациента:")

# Обработчик состояния Form.work (место работы)
@dp.message(Form.work)
async def process_work(message: Message, state: FSMContext):
    work = message.text.strip()
    await state.update_data(work=work)
    await state.set_state(Form.disease_date)
    await message.answer("Дата заболевания (первый день болезни):")

# Обработчик состояния Form.disease_date (дата заболевания)
@dp.message(Form.disease_date)
async def process_disease_date(message: Message, state: FSMContext):
    disease_date = message.text.strip()
    await state.update_data(disease_date=disease_date)
    await state.set_state(Form.consult_date)
    await message.answer("Дата обращения за медицинской помощью:")

# Обработчик состояния Form.consult_date (дата обращения)
@dp.message(Form.consult_date)
async def process_consult_date(message: Message, state: FSMContext):
    consult_date = message.text.strip()
    await state.update_data(consult_date=consult_date)
    await state.set_state(Form.diagnosis_date)
    await message.answer("Дата установления диагноза:")

# Обработчик состояния Form.diagnosis_date (дата диагноза)
@dp.message(Form.diagnosis_date)
async def process_diagnosis_date(message: Message, state: FSMContext):
    diagnosis_date = message.text.strip()
    await state.update_data(diagnosis_date=diagnosis_date)
    await state.set_state(Form.last_visit_date)
    await message.answer("Дата последнего визита пациента:")

# Обработчик состояния Form.last_visit_date (дата последнего визита)
@dp.message(Form.last_visit_date)
async def process_last_visit_date(message: Message, state: FSMContext):
    last_visit_date = message.text.strip()
    await state.update_data(last_visit_date=last_visit_date)
    await state.set_state(Form.diagnosis)
    await message.answer("Диагноз (название заболевания):")

# Обработчик состояния Form.diagnosis (диагноз)
@dp.message(Form.diagnosis)
async def process_diagnosis(message: Message, state: FSMContext):
    diagnosis = message.text.strip()
    await state.update_data(diagnosis=diagnosis)
    await state.set_state(Form.lab_results)
    await message.answer("Лабораторные результаты (если есть):")

# Обработчик состояния Form.lab_results (лабораторные результаты)
@dp.message(Form.lab_results)
async def process_lab_results(message: Message, state: FSMContext):
    lab_results = message.text.strip()
    await state.update_data(lab_results=lab_results)
    await state.set_state(Form.additional_info)
    await message.answer("Дополнительные сведения (при необходимости):")

# Обработчик состояния Form.additional_info (доп. сведения)
@dp.message(Form.additional_info)
async def process_additional_info(message: Message, state: FSMContext):
    additional_info = message.text.strip()
    await state.update_data(additional_info=additional_info)
    await state.set_state(Form.doctor_name)
    await message.answer("ФИО врача, заполнившего извещение:")

# Обработчик состояния Form.doctor_name (ФИО врача)
@dp.message(Form.doctor_name)
async def process_doctor_name(message: Message, state: FSMContext):
    doctor_name = message.text.strip()
    await state.update_data(doctor_name=doctor_name)
    await state.set_state(Form.sender)
    await message.answer("ФИО отправителя извещения (если отличается):")

# Обработчик состояния Form.sender (отправитель извещения)
@dp.message(Form.sender)
async def process_sender(message: Message, state: FSMContext):
    sender = message.text.strip()
    data = await state.update_data(sender=sender)  # собираем все данные в словарь
    await state.clear()  # сбрасываем состояние FSM
    data["institution"] = "ДКЦ им. Л.М. Рошаля"    # добавляем фиксированное учреждение
    try:
        # Формируем документ по шаблону
        doc = DocxTemplate("template.docx")
        doc.render(data)
        output_file = f"notification_{message.from_user.id}.docx"
        doc.save(output_file)
        # Отправляем документ пользователю
        file = FSInputFile(output_file, filename="izveshchenie_058u.docx")
        await message.answer_document(file, caption="✅ Экстренное извещение сформировано.")
    except Exception as e:
        logging.exception("Ошибка при формировании документа")
        await message.answer("Извините, не удалось сформировать документ.")

# Обработчик команды /cancel для отмены заполнения и сброса состояния
@dp.message(Command("cancel"))
async def cancel_process(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Заполнение формы отменено. Начните сначала командой /start.", reply_markup=ReplyKeyboardRemove())

# Запуск бота (долгий опрос)
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
