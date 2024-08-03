from asyncio import (
    create_task as asyncio_create_task,
    sleep as asyncio_sleep,
)

from aiogram import BaseMiddleware, Router, F
from aiogram.dispatcher.flags import get_flag
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    Update,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from src.database import Database
from src.logging import Logger
from src.utils import ERROR_MESSAGE
from src.weather import WeatherAPI


START_MESSAGE = 'Добро пожаловать в наш бот!'

ECHO_MESSAGE = 'Введите сообщение для его повтора'

HELP_MESSAGE = (
    'Доступные команды: /start, /help, /echo, /photo, '
    '/acquaintance, /users, /weather, /reply_check'
)

PHOTO_MESSAGE = 'Пришлите одно изображение'
PHOTO_ANSWER_MESSAGE = 'Размер изображения: {width}x{height}'

USER_LIST_MESSAGE = 'Список пользователей:\n{table}'

WEATHER_MESSAGE = 'Напишите название города'
WEATHER_ANSWER_MESSAGE = 'Погода в городе {city}:\nТемпература воздуха {temp}\n{desc}'

REPLY_TIME = 15
REPLY_MESSAGE = 'Привет, {username}! Как ты сегодня?'
REPLY_ANSWER_MESSAGE = 'Спасибо за ответ!'
REPLY_FORGOT_MESSAGE = 'Вы забыли ответить'

INLINE_KEYBOARD_CHOICE_1_TEXT = 'Выбор 1'
CHOICE_1_REPLY_TEXT = 'Вы выбрали Выбор 1'
INLINE_KEYBOARD_CHOICE_2_TEXT = 'Выбор 2'
CHOICE_2_REPLY_TEXT = 'Вы выбрали Выбор 2'


router = Router()


class CommandStates(StatesGroup):
    waiting_echo = State()
    waiting_photo = State()
    waiting_weather = State()
    waiting_reply = State()


class ReminderMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not get_flag(data, 'reminder'):
            reminder_task = asyncio_create_task(self.set_reminder(event, data['state']))
            await data['state'].update_data(reminder_task=reminder_task)
        return await handler(event, data)

    async def set_reminder(self, event: Update, state: FSMContext):
        await asyncio_sleep(REPLY_TIME)
        current_state = await state.get_state()
        if current_state == CommandStates.waiting_reply.state:
            await event.message.answer(REPLY_FORGOT_MESSAGE)
        await state.update_data(reminder_task=None)


@router.message(Command('start'))
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=INLINE_KEYBOARD_CHOICE_1_TEXT,
                    callback_data='choice_1'
                )
            ],
            [
                InlineKeyboardButton(
                    text=INLINE_KEYBOARD_CHOICE_2_TEXT,
                    callback_data='choice_2'
                )
            ]
        ]
    )

    await message.answer(START_MESSAGE, reply_markup=keyboard)


@router.callback_query(F.data.regexp(r'choice_\d+'))
async def choices_callback(callback_query: CallbackQuery):
    if (code := callback_query.data.split('_')[1]) == '1':
        await callback_query.message.answer(CHOICE_1_REPLY_TEXT)
    elif code == '2':
        await callback_query.message.answer(CHOICE_2_REPLY_TEXT)
    else:
        Logger.obj.log.info(f'Wrong choice callback code: {code}')


@router.message(Command('help'))
async def help_handler(message: Message):
    await message.answer(HELP_MESSAGE)


@router.message(Command('echo'))
async def echo_handler(message: Message, state: FSMContext):
    await message.answer(ECHO_MESSAGE)
    await state.set_state(CommandStates.waiting_echo)


@router.message(CommandStates.waiting_echo)
async def waiting_echo_handler(message: Message, state: FSMContext):
    await message.answer(message.text)
    await state.clear()


@router.message(Command('photo'))
async def photo_handler(message: Message, state: FSMContext):
    await message.answer(PHOTO_MESSAGE)
    await state.set_state(CommandStates.waiting_photo)


@router.message(CommandStates.waiting_photo)
async def waiting_photo_handler(message: Message, state: FSMContext):
    if (
        message.photo is None or
        message.text is not None or
        message.document is not None
    ):
        Logger.obj.log.error('Message must contains only one photo')
        await message.answer(ERROR_MESSAGE)
        await state.clear()
        return

    photo = message.photo[-1]
    await message.answer(
        PHOTO_ANSWER_MESSAGE.format(width=photo.width, height=photo.height)
    )
    await state.clear()


@router.message(Command('users'))
async def users_handler(message: Message):
    users = await Database.obj.get_users()
    if users:
        table = '\n'.join(
            f'{str(user[0]):10} | {user[1]:20} | {str(user[2]):5}'
            for user in users
        )
        await message.answer(USER_LIST_MESSAGE.format(table=table))
    else:
        await message.answer(ERROR_MESSAGE)


@router.message(Command('weather'))
async def weather_handler(message: Message, state: FSMContext):
    await message.answer(WEATHER_MESSAGE)
    await state.set_state(CommandStates.waiting_weather)


@router.message(CommandStates.waiting_weather)
async def waiting_weather_handler(message: Message, state: FSMContext):
    data = WeatherAPI.obj.get_city_weather(message.text)

    if data.get('success'):
        await message.answer(WEATHER_ANSWER_MESSAGE.format(**data))
    else:
        Logger.obj.log.error('Wrong answer from API server')
        await message.answer(ERROR_MESSAGE)

    await state.clear()


@router.message(Command(commands=['reply_check']))
async def reply_check_handler(message: Message, state: FSMContext):
    await message.answer(
        REPLY_MESSAGE.format(username=message.from_user.first_name)
    )
    await state.set_state(CommandStates.waiting_reply)


@router.message(CommandStates.waiting_reply, flags={'reminder': True})
async def waiting_reply_check_handler(message: Message, state: FSMContext):
    await message.answer(REPLY_ANSWER_MESSAGE)
    reminder_task = (await state.get_data()).get('reminder_task')
    if reminder_task:
        reminder_task.cancel()
    await state.clear()
