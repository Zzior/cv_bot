from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.states import BotState

menu_router = Router(name='user')


@menu_router.message(BotState.main_menu)
async def main_menu_handler(message: Message, state: FSMContext):
    if message.text:
        await message.answer(message.text)

    else:
        await message.answer("hi")