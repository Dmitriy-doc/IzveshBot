import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, Text
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from docxtpl import DocxTemplate

# Токен бота (здесь пока явно, но лучше вынести в переменные окружения)
TOKEN = "7518865505:AAEdCzkLa10pGA6N4uRyuy2CTDAQP0w-IOQ"
FROM_HOSPITAL = "ГБУЗ МО ДКЦ им. Л.М. Рошаля"

logging.basicConfig(level=logging.INFO)

# Определяем состояния для последовательного ввода данных
class NotificationStates(StatesGroup):
    diag = State()
    fio = State()
    sex = State()
    birth = State()
    address = State()
    phone = State()
    work_place = State()
    disease_date = State()
    last_visit_date = State()
    lab_results = State()
    hospital_place = State()
    additional_info = State()
    reporter = State()

def register_handlers(dp: Dispatcher):
    @dp.message(Command("start"))
    async def start_cmd(message: types.Message, state: FSMContext):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подать извещение", callback_data="new_notification")]
        ])
        await message.answer(
            "Добро пожаловать! Нажмите кнопку «Подать извещение», чтобы начать создание извещения.",
            reply_markup=keyboard
        )

    @dp.callback_query(Text("new_notification"))
    async def new_notification_handler(callback: types.CallbackQuery, state: FSMContext):
        logging.info("Получен callback 'new_notification'")
        await callback.answer("Обрабатывается...", show_alert=False)
        await callback.message.answer("Введите основной диагноз (например, 'J18.9 - Пневмония'):")
        await state.set_state(NotificationStates.diag)

    @dp.message(NotificationStates.diag)
    async def process_diag(message: types.Message, state: FSMContext):
        await state.update_data(diag=message.text)
        await message.answer("Введите ФИО пациента:")
        await state.set_state(NotificationStates.fio)

    @dp.message(NotificationStates.fio)
    async def process_fio(message: types.Message, state: FSMContext):
        await state.update_data(fio=message.text)
        await message.answer("Введите пол (М/Ж):")
        await state.set_state(NotificationStates.sex)

    @dp.message(NotificationStates.sex)
    async def process_sex(message: types.Message, state: FSMContext):
        await state.update_data(sex=message.text)
        await message.answer("Введите дату рождения (например, 11.08.1982):")
        await state.set_state(NotificationStates.birth)

    @dp.message(NotificationStates.birth)
    async def process_birth(message: types.Message, state: FSMContext):
        await state.update_data(birth=message.text)
        await message.answer("Введите адрес проживания:")
        await state.set_state(NotificationStates.address)

    @dp.message(NotificationStates.address)
    async def process_address(message: types.Message, state: FSMContext):
        await state.update_data(address=message.text)
        await message.answer("Введите телефон:")
        await state.set_state(NotificationStates.phone)

    @dp.message(NotificationStates.phone)
    async def process_phone(message: types.Message, state: FSMContext):
        await state.update_data(phone=message.text)
        await message.answer("Введите наименование и адрес места работы/учёбы:")
        await state.set_state(NotificationStates.work_place)

    @dp.message(NotificationStates.work_place)
    async def process_work_place(message: types.Message, state: FSMContext):
        await state.update_data(work_place=message.text)
        await message.answer("Введите дату заболевания (например, 12.03.2025):")
        await state.set_state(NotificationStates.disease_date)

    @dp.message(NotificationStates.disease_date)
    async def process_disease_date(message: types.Message, state: FSMContext):
        await state.update_data(disease_date=message.text)
        await message.answer("Введите дату последнего посещения/госпитализации (например, 12.03.2025):")
        await state.set_state(NotificationStates.last_visit_date)

    @dp.message(NotificationStates.last_visit_date)
    async def process_last_visit_date(message: types.Message, state: FSMContext):
        await state.update_data(last_visit_date=message.text)
        await message.answer("Введите лабораторные результаты (метод, дата отбора, результат):")
        await state.set_state(NotificationStates.lab_results)

    @dp.message(NotificationStates.lab_results)
    async def process_lab_results(message: types.Message, state: FSMContext):
        await state.update_data(lab_results=message.text)
        await message.answer("Введите место госпитализации:")
        await state.set_state(NotificationStates.hospital_place)

    @dp.message(NotificationStates.hospital_place)
    async def process_hospital_place(message: types.Message, state: FSMContext):
        await state.update_data(hospital_place=message.text)
        await message.answer("Введите дополнительные сведения:")
        await state.set_state(NotificationStates.additional_info)

    @dp.message(NotificationStates.additional_info)
    async def process_additional_info(message: types.Message, state: FSMContext):
        await state.update_data(additional_info=message.text)
        await message.answer("Введите ФИО врача (сообщившего извещение):")
        await state.set_state(NotificationStates.reporter)

    @dp.message(NotificationStates.reporter)
    async def process_reporter(message: types.Message, state: FSMContext):
        await state.update_data(reporter=message.text)
        data = await state.get_data()
        current_date = datetime.today().strftime("%d.%m.%Y")
        template_path = "./template.docx"
        output_path = "extr_notification.docx"
        context = {
            "diag": data.get("diag"),
            "fio": data.get("fio"),
            "sex": data.get("sex"),
            "birth": data.get("birth"),
            "address": data.get("address"),
            "phone": data.get("phone"),
            "work_place": data.get("work_place"),
            "disease_date": data.get("disease_date"),
            "first_contact_date": current_date,
            "diagnosis_date": current_date,
            "last_visit_date": data.get("last_visit_date"),
            "lab_results": data.get("lab_results"),
            "hospital_place": data.get("hospital_place"),
            "additional_info": data.get("additional_info"),
            "reporter": data.get("reporter"),
            "sender": data.get("reporter"),
            "registration_number": "",
            "from_hospital": FROM_HOSPITAL
        }

        async def generate_document(tmpl_path: str, out_path: str, ctx: dict):
            def blocking():
                doc = DocxTemplate(tmpl_path)
                doc.render(ctx)
                doc.save(out_path)
            await asyncio.to_thread(blocking)

        try:
            await generate_document(template_path, output_path, context)
        except Exception as e:
            logging.exception("Ошибка при создании документа")
            await message.answer(f"Ошибка при создании документа: {e}")
            return

        try:
            doc_file = FSInputFile(output_path)
            await message.answer_document(doc_file)
        except Exception as e:
            logging.exception("Ошибка при отправке документа")
            await message.answer(f"Ошибка при отправке документа: {e}")
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

        await message.answer("Извещение сформировано и отправлено!")
        await state.clear()

async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    register_handlers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
