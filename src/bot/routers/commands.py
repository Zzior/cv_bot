from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from ..navigation import to_main_menu

from i18n.types import Translator

commands_router = Router(name="commands")


@commands_router.message(CommandStart())
async def start_command(message: Message, state: FSMContext, t: Translator, lang: str) -> None:
    await to_main_menu(message, state, t, lang)