from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.routers.commands import start_command

other_router = Router(name='other')


# state not found
@other_router.message()
async def to_start(message: Message, state: FSMContext):
    await start_command(message, state)
