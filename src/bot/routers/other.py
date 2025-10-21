from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.routers.commands import start_command

from src.i18n.types import Translator

other_router = Router(name="other")


# state not found
@other_router.message()
async def to_start(message: Message, state: FSMContext, t: Translator, lang: str):
    await start_command(message, state, t, lang)
