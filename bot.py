import os
from aiogram import Bot, Dispatcher, types  # aiogram core classes
from aiogram.filters import Command        # Filter to handle commands like /start
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from docxtpl import DocxTemplate
from aiogram.types import FSInputFile

# Define FSM States for the patient report data collection
class PatientReport(StatesGroup):
    fio = State()                # Full name of patient
    sex = State()                # Gender
    birth = State()              # Date of birth
    address = State()            # Address
    phone = State()              # Contact phone number
    work_place = State()         # Place of work/study
    disease_date = State()       # Date of disease onset
    first_contact_date = State() # Date of first medical contact
    diagnosis_date = State()     # Date when diagnosis was established
    last_visit_date = State()    # Date of last visit
    diag = State()               # Diagnosis
    lab_results = State()        # Laboratory data
    additional_info = State()    # Additional information
    hospital_place = State()     # Place of hospitalization
    reporter = State()           # Doctor's full name (report author)
    sender = State()             # Sender (e.g., referring person or department)
    registration_number = State()# Registration number
    from_hospital = State()      # Institution (hospital/clinic name)

# Initialize bot and dispatcher with memory storage for FSM
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set. Please set BOT_TOKEN before running the bot.")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Start command handler to initiate the data collection conversation
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """
    Handler for /start command. Begins the patient data collection by setting the first state.
    """
    await state.set_state(PatientReport.fio)  # set current state to expecting FIO
    await message.answer("Здравствуйте! Давайте соберем данные пациента.\n\nВведите ФИО пациента:")
    # The bot now waits for the user's next message, which should be the patient's name.

# Handler for patient's full name (State: fio)
@dp.message(PatientReport.fio)
async def process_fio(message: types.Message, state: FSMContext):
    # Save the patient's full name and move to next state
    await state.update_data(fio=message.text)
    await state.set_state(PatientReport.sex)
    await message.answer("Укажите пол пациента (например, мужской/женский):")

# Handler for gender (State: sex)
@dp.message(PatientReport.sex)
async def process_sex(message: types.Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await state.set_state(PatientReport.birth)
    await message.answer("Введите дату рождения пациента (например, 01.01.2010):")

# Handler for birth date (State: birth)
@dp.message(PatientReport.birth)
async def process_birth(message: types.Message, state: FSMContext):
    await state.update_data(birth=message.text)
    await state.set_state(PatientReport.address)
    await message.answer("Введите адрес пациента:")

# Handler for address (State: address)
@dp.message(PatientReport.address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(PatientReport.phone)
    await message.answer("Введите контактный телефон пациента:")

# Handler for phone number (State: phone)
@dp.message(PatientReport.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(PatientReport.work_place)
    await message.answer("Укажите место работы или учебы пациента:")

# Handler for work/study place (State: work_place)
@dp.message(PatientReport.work_place)
async def process_work_place(message: types.Message, state: FSMContext):
    await state.update_data(work_place=message.text)
    await state.set_state(PatientReport.disease_date)
    await message.answer("Введите дату начала заболевания:")

# Handler for disease onset date (State: disease_date)
@dp.message(PatientReport.disease_date)
async def process_disease_date(message: types.Message, state: FSMContext):
    await state.update_data(disease_date=message.text)
    await state.set_state(PatientReport.first_contact_date)
    await message.answer("Введите дату первичного обращения за помощью:")

# Handler for first contact date (State: first_contact_date)
@dp.message(PatientReport.first_contact_date)
async def process_first_contact_date(message: types.Message, state: FSMContext):
    await state.update_data(first_contact_date=message.text)
    await state.set_state(PatientReport.diagnosis_date)
    await message.answer("Введите дату установления диагноза:")

# Handler for diagnosis date (State: diagnosis_date)
@dp.message(PatientReport.diagnosis_date)
async def process_diagnosis_date(message: types.Message, state: FSMContext):
    await state.update_data(diagnosis_date=message.text)
    await state.set_state(PatientReport.last_visit_date)
    await message.answer("Введите дату последнего визита пациента:")

# Handler for last visit date (State: last_visit_date)
@dp.message(PatientReport.last_visit_date)
async def process_last_visit_date(message: types.Message, state: FSMContext):
    await state.update_data(last_visit_date=message.text)
    await state.set_state(PatientReport.diag)
    await message.answer("Введите диагноз пациента:")

# Handler for diagnosis text (State: diag)
@dp.message(PatientReport.diag)
async def process_diag(message: types.Message, state: FSMContext):
    await state.update_data(diag=message.text)
    await state.set_state(PatientReport.lab_results)
    await message.answer("Введите лабораторные данные (если есть):")

# Handler for lab results (State: lab_results)
@dp.message(PatientReport.lab_results)
async def process_lab_results(message: types.Message, state: FSMContext):
    await state.update_data(lab_results=message.text)
    await state.set_state(PatientReport.additional_info)
    await message.answer("Введите дополнительные сведения (если нужны):")

# Handler for additional info (State: additional_info)
@dp.message(PatientReport.additional_info)
async def process_additional_info(message: types.Message, state: FSMContext):
    await state.update_data(additional_info=message.text)
    await state.set_state(PatientReport.hospital_place)
    await message.answer("Укажите место госпитализации (если было):")

# Handler for hospital place (State: hospital_place)
@dp.message(PatientReport.hospital_place)
async def process_hospital_place(message: types.Message, state: FSMContext):
    await state.update_data(hospital_place=message.text)
    await state.set_state(PatientReport.reporter)
    await message.answer("Введите ФИО врача, заполняющего отчет:")

# Handler for doctor's name (State: reporter)
@dp.message(PatientReport.reporter)
async def process_reporter(message: types.Message, state: FSMContext):
    await state.update_data(reporter=message.text)
    await state.set_state(PatientReport.sender)
    await message.answer("Введите должность или ФИО отправителя пациента:")

# Handler for sender (State: sender)
@dp.message(PatientReport.sender)
async def process_sender(message: types.Message, state: FSMContext):
    await state.update_data(sender=message.text)
    await state.set_state(PatientReport.registration_number)
    await message.answer("Введите регистрационный номер (если имеется):")

# Handler for registration number (State: registration_number)
@dp.message(PatientReport.registration_number)
async def process_registration_number(message: types.Message, state: FSMContext):
    await state.update_data(registration_number=message.text)
    await state.set_state(PatientReport.from_hospital)
    await message.answer("Укажите учреждение (больницу/поликлинику):")

# Handler for institution/from_hospital (State: from_hospital) - final step
@dp.message(PatientReport.from_hospital)
async def process_from_hospital(message: types.Message, state: FSMContext):
    # Save the last piece of data
    await state.update_data(from_hospital=message.text)
    # Retrieve all collected data from FSM storage
    data = await state.get_data()

    # Generate the document using the template
    try:
        doc = DocxTemplate("template.docx")           # Load the Word template
        doc.render(data)                              # Substitute variables with actual data
        output_path = "patient_report.docx"
        doc.save(output_path)                         # Save the filled report as a new file

        # Send the generated document to the user
        file = FSInputFile(output_path)
        await message.answer_document(file, caption="✅ Отчет сформирован. Вот ваш документ.")
    except Exception as e:
        # If there's an error during document creation, inform the user
        await message.answer(f"Произошла ошибка при формировании документа: {e}")

    # Finish FSM by clearing any stored state and data
    await state.clear()

# Start the bot by polling Telegram for new messages
if __name__ == "__main__":
    print("Bot is starting...")
    dp.run_polling(bot)
