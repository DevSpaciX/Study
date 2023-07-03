import asyncio
import datetime
import logging
import datetime
from io import BytesIO

import aiogram
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from asgiref.sync import sync_to_async
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
from aiogram.types import BotCommand
from course.models import Employee
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup

# Инициализируем бота
bot = Bot(token='6117198025:AAHGvfq32khYqQ_29fgBZxVQXv0WsNYfsfc')

# Инициализируем диспетчер
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

k = Employee.objects.count()


class RegistrationState(StatesGroup):
    WaitingForEmail = State()


async def setup_bot_commands(dp):
    commands = [
        types.BotCommand(command="/start", description="Start the bot"),
        types.BotCommand(command="/login", description="Login"),
    ]
    await bot.set_my_commands(commands)


@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Чтобы войти, используй команду /login")


@dp.message_handler(Command("login"))
async def cmd_login(message: types.Message, state: FSMContext):
    await RegistrationState.WaitingForEmail.set()
    await message.answer("Введите свой email:")


@dp.message_handler(state=RegistrationState.WaitingForEmail)
async def process_email(message: types.Message, state: FSMContext):
    user_email = message.text

    try:
        user = await sync_to_async(Employee.objects.get)(name=user_email)
        await message.answer(f"Вы прошли регистрацию с email: {user_email}")
        await state.finish()

        # Обновление списка команд
        commands = [
            types.BotCommand(command="/new_command1", description="New Command 1"),
            types.BotCommand(command="/new_command2", description="New Command 2"),
        ]
        await bot.set_my_commands(commands)

        # Обновление клавиатуры с новыми командами
        await start(message)
    except Employee.DoesNotExist:
        await message.answer("Похоже, тебя нет в базе, попробуй еще раз")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Создание клавиатуры
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_start_work = types.KeyboardButton("Почати роботу 🚀", callback_data='button_start_work')
    button_start_lunch = types.KeyboardButton("Обід 🍔", callback_data='button_start_lunch')
    button_watch_stat = types.KeyboardButton("Статистика 📊", callback_data='button_watch_stat')
    button_learn = types.KeyboardButton("База знань 🧠", callback_data='button_learn')
    keyboard.add(button_start_work, button_start_lunch, button_watch_stat, button_learn)

    # Отправка сообщения с клавиатурой
    await bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)


@dp.message_handler(text="Почати роботу 🚀")
async def create_employee(message: types.Message):
    time = datetime.datetime.now().strftime("%H:%M:%S")
    # Установка состояния FSMContext для ожидания следующего сообщения с именем сотрудника
    await message.answer(f"Работа началась в {time} ")


@dp.message_handler(text="Обід 🍔")
async def lunch_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_food1 = types.KeyboardButton("Еда 1")
    button_food2 = types.KeyboardButton("Еда 2")
    button_return = types.KeyboardButton("Вернуться в главное меню")
    keyboard.add(button_food1, button_food2, button_return)

    await bot.send_message(message.chat.id, "Выберите еду:", reply_markup=keyboard)


@dp.message_handler(text="База знань 🧠")
async def learn_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_failed_online = types.KeyboardButton("Failed_online ⚠️")
    button_date_error = types.KeyboardButton("Касир 💀")
    button_return = types.KeyboardButton("Вернуться в главное меню ❌")
    keyboard.add(button_failed_online, button_date_error, button_return)

    await bot.send_message(message.chat.id, "Выбери ошибку которая тебя интересует:", reply_markup=keyboard)


@dp.message_handler(text="Касир 💀")
async def cashier_errors(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_return = types.KeyboardButton("Повернутися до питань ❌")
    keyboard.add(button_return)
    photo_url = "https://i.imgur.com/4u9s0zS.png"
    response = requests.get(photo_url)
    photo = BytesIO(response.content)
    await bot.send_photo(message.chat.id, photo, reply_markup=keyboard)


@dp.message_handler(text="Failed_online ⚠️")
async def failed_online(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_return = types.KeyboardButton("Повернутися до питань ❌")
    keyboard.add(button_return)
    photo_url = "https://i.imgur.com/ZxGpxNG.png"
    response = requests.get(photo_url)
    photo = BytesIO(response.content)
    await bot.send_photo(message.chat.id, photo, reply_markup=keyboard)


@dp.message_handler(text="Вернуться в главное меню ❌")
async def return_to_main_menu(message: types.Message):
    await start(message)


@dp.message_handler(text="Повернутися до питань ❌")
async def return_to_learn_menu(message: types.Message):
    await learn_menu(message)

def run_bot():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, skip_updates=True, on_startup=setup_bot_commands)


run_bot()
