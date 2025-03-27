import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from docxtpl import DocxTemplate
from aiogram.types import FSInputFile

# Включаем логирование для отладки (по желанию можно отключить INFO уровень)
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found. Please set the BOT_TOKEN environment variable.")
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

# Определение состояний FSM
class Form(StatesGroup):
    destination = State()       # Куда (получатель документа)
    fullname = State()          # ФИО (например, пациента или другого лица)
    additional = State()        # Дополнительные сведения (можно пропустить)

# Регистрация роутера для сообщений
router = dp.include_router(types.Router())  # Создаем и подключаем Router для хендлеров сообщений

# Обработчик команды /start – запускает FSM
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    # Начало заполнения формы: сразу переходим к первому шагу (destination)
    await state.set_state(Form.destination)
    # Отправляем пользователю инструкцию для первого шага
    await message.answer("👋 Привет! Давайте сформируем документ.\n\nВведите получателя (куда направляем документ):")

# Обработчик первого шага FSM: получатель (destination)
@router.message(Form.destination)
async def process_destination(message: types.Message, state: FSMContext) -> None:
    # Сохраняем ответ пользователя (или пустую строку, если пользователь ничего не ввёл)
    dest_text = message.text.strip() if message.text else ""
    await state.update_data(destination=dest_text)
    # Переходим к следующему шагу: ввод ФИО
    await state.set_state(Form.fullname)
    # Запрашиваем ФИО (можно оставить пустым)
    await message.answer("Введите ФИО (можно не указывать):")

# Обработчик второго шага FSM: ФИО (fullname)
@router.message(Form.fullname)
async def process_fullname(message: types.Message, state: FSMContext) -> None:
    name_text = message.text.strip() if message.text else ""
    await state.update_data(fullname=name_text)
    # Переходим к следующему шагу: дополнительные сведения
    await state.set_state(Form.additional)
    await message.answer("Введите дополнительные сведения (при необходимости, можно пропустить):")

# Обработчик третьего шага FSM: дополнительные сведения
@router.message(Form.additional)
async def process_additional(message: types.Message, state: FSMContext) -> None:
    add_text = message.text.strip() if message.text else ""
    # Собираем все данные, которые есть в FSM (destination и fullname из предыдущих шагов)
    user_data = await state.get_data()
    user_data["additional"] = add_text
    # Добавляем поле "Откуда" автоматически
    user_data["from_org"] = "ДКЦ им. Л.М. Рошаля"
    # Генерируем документ на основе шаблона с помощью docxtpl
    try:
        template = DocxTemplate("template.docx")  # Укажите путь к шаблону .docx
    except Exception as e:
        await message.answer(f"Ошибка: не удалось открыть шаблон документа ({e})")
        await state.clear()
        return
    try:
        template.render(user_data)  # Подставляем данные в шаблон
    except Exception as e:
        await message.answer(f"Ошибка при формировании документа: {e}")
        await state.clear()
        return
    output_filename = "result.docx"
    try:
        template.save(output_filename)
    except Exception as e:
        await message.answer(f"Ошибка при сохранении документа: {e}")
        await state.clear()
        return
    # Отправляем получившийся .docx файл пользователю
    try:
        doc_file = FSInputFile(output_filename)
        await message.answer_document(doc_file, caption="📄 Ваш документ сформирован.")
    except Exception as e:
        await message.answer(f"Не удалось отправить документ: {e}")
    # Очищаем состояние FSM, завершая диалог
    await state.clear()

# Обработчик команды /cancel для отмены заполнения формы на любом этапе
@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext) -> None:
    # Отменяем и сбрасываем состояние
    await state.clear()
    await message.answer("🚫 Заполнение формы отменено. Если хотите начать заново, отправьте /start")

# Запуск бота в режиме polling
async def main():
    # Запускаем polling, пропуская накопившиеся обновления, если бот перезапущен
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
