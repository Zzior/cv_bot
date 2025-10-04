from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from src.bot.navigation import to_main_menu

commands_router = Router(name='commands')


@commands_router.message(CommandStart())
async def start_command(message: Message, state: FSMContext) -> None:
    await to_main_menu(message, state)