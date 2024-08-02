from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.database import Database
from src.utils import ERROR_MESSAGE


ACQUAINTANCE_MESSAGE_1_TEXT = 'Укажите, как вас зовут'
ACQUAINTANCE_MESSAGE_2_TEXT = 'Укажите, сколько вам лет'
ACQUAINTANCE_MESSAGE_3_TEXT = 'Вас зовут {name} и ваш возраст {age}'


router = Router()


class UserForm(StatesGroup):
    name = State()
    age = State()


@router.message(Command('acquaintance'))
async def acquaintance_handler(message: Message, state: FSMContext):
    await state.set_state(UserForm.name)
    await message.answer(ACQUAINTANCE_MESSAGE_1_TEXT)


@router.message(UserForm.name)
async def name_form_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(UserForm.age)
    await message.answer(ACQUAINTANCE_MESSAGE_2_TEXT)


@router.message(UserForm.age)
async def age_form_handler(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0:
            raise ValueError()

        await state.update_data(age=age)

        data = await state.get_data()
        name, age = data.get('name'), data.get('age')

        await Database.obj.add_user(message.from_user.id, name, age)

        await message.answer(
            ACQUAINTANCE_MESSAGE_3_TEXT.format(
                name=name,
                age=age
            )
        )
    except ValueError:
        await message.answer(ERROR_MESSAGE)
    finally:
        await state.clear()
