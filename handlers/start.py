import os
from aiogram import Bot, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, InputTextMessageContent, InlineQueryResultArticle, CallbackQuery
    
from aiogram.fsm.context import FSMContext

from datetime import datetime
from secrets import token_hex

from core.state import UserStates
from core import kb
from test import submit_forms
from config import BOT_TOKEN, PASSWORD

bot = Bot(
        BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

handlers_router = Router()

@handlers_router.inline_query(F.query == "results")
async def results_handler(iquery: Message, state: FSMContext) -> None:
    results = []
    for file in os.listdir(f'tables/{iquery.from_user.id}'):
        results.append(InlineQueryResultArticle(
            id=token_hex(2),
            title=f"Результаты от {file.replace('.xlsx', '')}",
            thumbnail_url="https://i.ibb.co/PMNVkxF/completed-task.png",
            description="Нажмите для получения результатов",
            hide_url=True,
            input_message_content=InputTextMessageContent(
                message_text=f"completed=tables/{iquery.from_user.id}/{file}",
                parse_mode="HTML"
            )))
    await iquery.answer(results[::-1], cache_time=1)


@handlers_router.message(F.via_bot & F.text.startswith("completed="))
async def query_completed_task(msg: Message, state: FSMContext):
    dir = msg.text.split("completed=")[-1].strip()
    await msg.delete()
    await msg.answer_document(FSInputFile(dir), caption="Результаты")

@handlers_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await message.answer("Введите пароль, чтобы получить доступ. (ПАРОЛЬ 123)")
    await state.set_state(UserStates.MAIN)

@handlers_router.message(Command("results"))
async def results_handler(message: Message, state: FSMContext) -> None:
    await message.answer("Выберите время когда запустили рассылку!", reply_markup=kb.res_button)

@handlers_router.message(Command("admin"))
async def admin_handler(message: Message, state: FSMContext) -> None:
    await message.answer_document(FSInputFile("sites_data.xlsx"), caption="Отправьте таблицу с сайтами, пример таблицы прикреплен")
    await state.set_state(UserStates.ADMIN)
@handlers_router.message(UserStates.ADMIN)
async def adminc_handler(message: Message, state: FSMContext) -> None:
    if message.document:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, destination=f"sites_data.xlsx")
        await message.answer("Таблица успешно обновлена!")

@handlers_router.message(UserStates.MAIN)
async def start_handler(message: Message, state: FSMContext) -> None:
    
    if message.text == PASSWORD:

        await message.answer_photo(FSInputFile("start.jpg"), caption="Привет! Я бот для отправки заявок на сайты.", reply_markup=kb.main_menu)
        await state.set_state(UserStates.waiting_for_password)
    else:
        await message.answer("Неверный пароль. Попробуйте ещё раз.")

    
@handlers_router.callback_query(F.data == "start")
async def password_handler(call: CallbackQuery, state: FSMContext) -> None:

    await call.message.answer("Введите имя:")
    await state.set_state(UserStates.waiting_for_name)


@handlers_router.message(UserStates.waiting_for_name)
async def name_handler(message: Message, state: FSMContext) -> None:
    user_name = message.text
    await state.update_data(user_name=user_name)
    await message.answer(f"Введите номер телефона:")
    await state.set_state(UserStates.waiting_for_phone)

@handlers_router.message(UserStates.waiting_for_phone)
async def phone_handler(message: Message, state: FSMContext) -> None:
    user_phone = message.text
    await state.update_data(user_phone=user_phone)
    await message.answer(f"Введите почту:")
    await state.set_state(UserStates.waiting_for_email)

@handlers_router.message(UserStates.waiting_for_email)
async def email_handler(message: Message, state: FSMContext) -> None:
    user_email = message.text
    await state.update_data(user_email=user_email)
    await message.answer(f"Выберите категорию:", reply_markup=kb.get_categories_button())

@handlers_router.callback_query(F.data.startswith("category="))
async def category_handler(call: CallbackQuery, state: FSMContext) -> None:
    category = call.data.split("=")[1]
    await state.update_data(category=None)
    data = await state.get_data()
    user_name = data.get("user_name")
    user_phone = data.get("user_phone")
    user_email = data.get("user_email")
    if category == "all":
        category = "Все"

    await call.message.answer(f"Введенные данные:\nИмя: {user_name}\nТелефон: {user_phone}\nПочта: {user_email}\nКатегория: {category}", reply_markup=kb.start_menu)

@handlers_router.callback_query(F.data == "start_message")
async def start_message_handler(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user_name = data.get("user_name")
    user_phone = data.get("user_phone")
    user_email = data.get("user_email")
    category = data.get("category")
    await call.message.answer("Идет рассылка...")
    await submit_forms(user_name=user_name, user_phone=user_phone, user_email=user_email, message=call, category=category)
    await call.message.answer("Рассылка успешно завершена", reply_markup=kb.start_menu)
